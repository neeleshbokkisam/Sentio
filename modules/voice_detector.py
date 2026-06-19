import math

import librosa
import numpy as np
import sounddevice as sd
import torch

from modules.config import SAMPLE_RATE, VOICE_LABEL_MAP, SPEECHBRAIN_MODEL
from modules.fusion import normalize_emotion

_classifier = None
_use_fallback = False


def voice_backend() -> str:
    if _use_fallback:
        return "fallback"
    return "speechbrain" if _classifier else "unknown"


def _load_classifier():
    global _classifier, _use_fallback
    if _classifier is not None or _use_fallback:
        return _classifier

    try:
        from speechbrain.inference.interfaces import foreign_class

        _classifier = foreign_class(
            source=SPEECHBRAIN_MODEL,
            pymodule_file="custom_interface.py",
            classname="CustomEncoderWav2vec2Classifier",
        )
    except Exception as e:
        print("speechbrain failed to load, using fallback:", e)
        _use_fallback = True
    return _classifier


def _normalize_conf(score: float) -> float:
    # speechbrain returns log-probs — squash to 0-1
    if score <= 0:
        return min(1.0, max(0.0, float(score) + 1.0))
    if score <= 1.0:
        return float(score)
    return 1.0 / (1.0 + math.exp(-score))


def _fallback_detect(audio: np.ndarray, sr: int) -> dict:
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40)
    avg = float(np.mean(mfcc))
    if avg > 0.1:
        emotion = "happy"
    elif avg < -0.1:
        emotion = "sad"
    else:
        emotion = "neutral"
    return {"emotion": emotion, "confidence": 0.4}


def _resample(audio: np.ndarray, sr: int) -> np.ndarray:
    if sr == SAMPLE_RATE:
        return audio.astype(np.float32)
    return librosa.resample(audio.astype(np.float32), orig_sr=sr, target_sr=SAMPLE_RATE)


def detect_voice_emotion(audio: np.ndarray, sr: int) -> dict:
    if audio is None or len(audio) < sr * 0.5:
        return {"emotion": "unknown", "confidence": 0.0}

    audio = audio.flatten()
    if np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))

    classifier = _load_classifier()
    if classifier is None:
        wav = _resample(audio, sr)
        return _fallback_detect(wav, SAMPLE_RATE)

    wav = _resample(audio, sr)
    tensor = torch.tensor(wav).unsqueeze(0)
    try:
        out_prob, score, _index, text_lab = classifier.classify_batch(tensor)
        raw_label = text_lab[0] if text_lab else "neutral"
        mapped = VOICE_LABEL_MAP.get(raw_label.lower(), normalize_emotion(raw_label))
        if out_prob is not None and hasattr(out_prob, "max"):
            conf = float(torch.softmax(out_prob, dim=-1).max().item())
        else:
            conf = _normalize_conf(float(score[0]) if hasattr(score, "__getitem__") else float(score))
        return {"emotion": mapped, "confidence": round(conf, 3), "raw_label": raw_label}
    except Exception as e:
        print("voice error:", e)
        return _fallback_detect(wav, SAMPLE_RATE)


def record_audio(duration: float, sample_rate: int = 22050) -> tuple:
    samples = int(duration * sample_rate)
    audio = sd.rec(samples, samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    return audio.flatten(), sample_rate
