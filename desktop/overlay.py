import cv2

from modules.config import MOOD_COLORS


def draw_dashboard(frame, face: dict, voice: dict, fused: dict):
    h, w = frame.shape[:2]
    mood = fused.get("mood", "unknown").split("/")[0]
    color = MOOD_COLORS.get(mood, MOOD_COLORS["unknown"])["bgr"]

    # mood ring
    cx, cy, r = w - 80, 80, 50
    cv2.circle(frame, (cx, cy), r, color, 4)
    cv2.putText(frame, mood[:8], (cx - 40, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # confidence bars
    face_conf = int(fused.get("face_confidence", 0) * 100)
    voice_conf = int(fused.get("voice_confidence", 0) * 100)
    _draw_bar(frame, 10, h - 60, w - 20, 12, face_conf, "Face")
    _draw_bar(frame, 10, h - 35, w - 20, 12, voice_conf, "Voice")

    # labels
    cv2.putText(frame, f"Face: {fused.get('face_emotion', '?')}", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    cv2.putText(frame, f"Voice: {fused.get('voice_emotion', '?')}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    cv2.putText(frame, f"Mood: {fused.get('mood', '?')}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

    if fused.get("mismatch"):
        cv2.putText(
            frame,
            f"MISMATCH face={fused.get('face_emotion')} voice={fused.get('voice_emotion')}",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2,
        )

    return frame


def _draw_bar(frame, x, y, width, height, pct, label):
    cv2.rectangle(frame, (x, y), (x + width, y + height), (60, 60, 60), -1)
    fill = int(width * pct / 100)
    cv2.rectangle(frame, (x, y), (x + fill, y + height), (0, 200, 100), -1)
    cv2.putText(frame, f"{label} {pct}%", (x + 4, y + height - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
