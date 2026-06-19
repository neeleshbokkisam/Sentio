import cv2

from modules.config import MOOD_COLORS
from modules.display import signal_strength


def draw_dashboard(frame, face: dict, voice: dict, fused: dict):
    h, w = frame.shape[:2]
    mood = fused.get("mood", "unknown").split("/")[0]
    color = MOOD_COLORS.get(mood, MOOD_COLORS["unknown"])["bgr"]

    cx, cy, r = w - 80, 80, 50
    cv2.circle(frame, (cx, cy), r, color, 4)
    cv2.putText(frame, mood[:8], (cx - 40, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    face_sig = fused.get("face_signal", signal_strength(fused.get("face_confidence", 0), not fused.get("face_offline")))
    voice_sig = fused.get("voice_signal", signal_strength(fused.get("voice_confidence", 0)))

    cv2.putText(frame, f"Face: {fused.get('face_emotion', '?')} ({face_sig})", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 255), 2)
    cv2.putText(frame, f"Voice: {fused.get('voice_emotion', '?')} ({voice_sig})", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 0), 2)
    cv2.putText(frame, f"Mood: {fused.get('mood', '?')}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

    if fused.get("face_offline"):
        cv2.putText(frame, "face offline - voice only", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)
    elif fused.get("mismatch"):
        cv2.putText(frame, "face and voice disagree", (10, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

    return frame
