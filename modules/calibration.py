import json
import time
from dataclasses import dataclass, asdict

import numpy as np

from modules.config import CALIBRATION_FILE, AUDIO_DURATION, RECORD_SAMPLE_RATE
from modules.face_detector import FaceDetector
from modules.voice_detector import detect_voice_emotion, record_audio


@dataclass
class CalibrationProfile:
    neutral_face: dict
    happy_face: dict
    neutral_voice: dict
    created_at: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


def load_profile():
    if not CALIBRATION_FILE.exists():
        return None
    try:
        data = json.loads(CALIBRATION_FILE.read_text())
        return CalibrationProfile.from_dict(data)
    except Exception:
        return None


def save_profile(profile: CalibrationProfile):
    CALIBRATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    CALIBRATION_FILE.write_text(json.dumps(profile.to_dict(), indent=2))


def apply_calibration(face: dict, voice: dict, profile):
    if profile is None:
        return face, voice

    face = dict(face)
    voice = dict(voice)

    if face.get("detected") and profile.neutral_face:
        base = profile.neutral_face.get("confidence", 0.5)
        face["confidence"] = min(1.0, face.get("confidence", 0) + (base * 0.1))

    if profile.neutral_voice:
        base = profile.neutral_voice.get("confidence", 0.5)
        voice["confidence"] = min(1.0, voice.get("confidence", 0) + (base * 0.1))

    return face, voice


def _avg_face_readings(cap, detector: FaceDetector, seconds: float) -> dict:
    scores = {}
    count = 0
    end = time.time() + seconds
    while time.time() < end:
        ret, frame = cap.read()
        if not ret:
            break
        result = detector.analyze_frame(frame)
        if result.get("detected"):
            emo = result["emotion"]
            scores[emo] = scores.get(emo, 0) + result.get("confidence", 0)
            count += 1
        time.sleep(0.1)

    if not scores:
        return {"emotion": "neutral", "confidence": 0.5, "detected": True}

    top = max(scores, key=scores.get)
    return {"emotion": top, "confidence": round(scores[top] / max(count, 1), 3), "detected": True}


def _avg_voice_readings(seconds: float) -> dict:
    chunks = max(1, int(seconds / AUDIO_DURATION))
    labels = []
    confs = []
    for _ in range(chunks):
        audio, sr = record_audio(AUDIO_DURATION, RECORD_SAMPLE_RATE)
        result = detect_voice_emotion(audio, sr)
        labels.append(result["emotion"])
        confs.append(result.get("confidence", 0))
        time.sleep(0.2)

    if not labels:
        return {"emotion": "neutral", "confidence": 0.5}

    top = max(set(labels), key=labels.count)
    avg_conf = float(np.mean([c for l, c in zip(labels, confs) if l == top] or confs))
    return {"emotion": top, "confidence": round(avg_conf, 3)}


def run_calibration(cap, steps_callback=None) -> CalibrationProfile:
    detector = FaceDetector(interval_frames=5)

    if steps_callback:
        steps_callback("neutral_face", "Sit neutral — looking at the camera")
    neutral_face = _avg_face_readings(cap, detector, 8)

    if steps_callback:
        steps_callback("happy_face", "Smile or look happy")
    happy_face = _avg_face_readings(cap, detector, 8)

    if steps_callback:
        steps_callback("neutral_voice", "Speak normally for a few seconds")
    neutral_voice = _avg_voice_readings(8)

    profile = CalibrationProfile(
        neutral_face=neutral_face,
        happy_face=happy_face,
        neutral_voice=neutral_voice,
        created_at=time.strftime("%Y-%m-%dT%H:%M:%S"),
    )
    save_profile(profile)
    return profile
