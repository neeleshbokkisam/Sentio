def signal_strength(confidence: float, detected: bool = True) -> str:
    if not detected or confidence <= 0:
        return "offline"
    if confidence < 0.35:
        return "weak"
    if confidence < 0.66:
        return "medium"
    return "strong"


def mood_phrase(mood: str) -> str:
    return mood.replace("/", " / ").replace("_", " ")
