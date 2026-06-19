from modules.config import EMOTIONS
from modules.display import signal_strength


def normalize_emotion(label: str) -> str:
    if not label:
        return "unknown"
    clean = label.lower().strip()
    if "no face" in clean or clean == "detecting...":
        return "no_face"
    for emo in EMOTIONS:
        if emo in clean:
            return emo
    return clean


def fuse_mood(face: dict, voice: dict) -> dict:
    face_emo = normalize_emotion(face.get("emotion", "unknown"))
    voice_emo = normalize_emotion(voice.get("emotion", "unknown"))
    detected = face.get("detected", False)
    face_conf = float(face.get("confidence", 0.0))
    voice_conf = float(voice.get("confidence", 0.0))

    if not detected or face_emo == "no_face":
        mood = voice_emo
        mismatch = False
        face_offline = True
    elif face_emo == voice_emo:
        mood = face_emo
        mismatch = False
        face_offline = False
    else:
        mood = f"{face_emo}/{voice_emo}"
        mismatch = True
        face_offline = False

    return {
        "mood": mood,
        "mismatch": mismatch,
        "face_offline": face_offline,
        "face_emotion": face_emo if detected else "no_face",
        "voice_emotion": voice_emo,
        "face_confidence": face_conf,
        "voice_confidence": voice_conf,
        "face_signal": signal_strength(face_conf, detected and not face_offline),
        "voice_signal": signal_strength(voice_conf, voice_emo not in ("unknown", "detecting")),
    }
