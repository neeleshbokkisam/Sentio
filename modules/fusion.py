from modules.config import EMOTIONS


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

    if not detected or face_emo == "no_face":
        mood = voice_emo
        mismatch = False
    elif face_emo == voice_emo:
        mood = face_emo
        mismatch = False
    else:
        mood = f"{face_emo}/{voice_emo}"
        mismatch = True

    return {
        "mood": mood,
        "mismatch": mismatch,
        "face_emotion": face_emo if detected else "no_face",
        "voice_emotion": voice_emo,
        "face_confidence": face.get("confidence", 0.0),
        "voice_confidence": voice.get("confidence", 0.0),
    }
