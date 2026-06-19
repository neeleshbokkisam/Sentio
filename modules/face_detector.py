import cv2
import numpy as np
from deepface import DeepFace

from modules.config import DEEPFACE_INTERVAL_FRAMES
from modules.fusion import normalize_emotion


def _face_result(emotion: str, confidence: float, detected: bool) -> dict:
    return {
        "emotion": emotion,
        "confidence": round(float(confidence), 3),
        "detected": detected,
    }


class FaceDetector:
    def __init__(self, interval_frames: int = DEEPFACE_INTERVAL_FRAMES):
        self.interval_frames = interval_frames
        self._frame_count = 0
        self._last = _face_result("detecting", 0.0, False)

    def analyze_frame(self, frame) -> dict:
        self._frame_count += 1
        if self._frame_count % self.interval_frames != 0:
            return dict(self._last)

        try:
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            result = DeepFace.analyze(
                small,
                actions=["emotion"],
                enforce_detection=False,
                detector_backend="opencv",
            )
            emotions = result[0]["emotion"]
            dominant = result[0]["dominant_emotion"]
            conf = float(emotions.get(dominant, 0.0)) / 100.0
            self._last = _face_result(
                normalize_emotion(dominant),
                conf,
                dominant != "unknown" and conf > 0.05,
            )
        except Exception as e:
            print("face error:", e)
            self._last = _face_result("no_face", 0.0, False)

        return dict(self._last)

    def analyze_image_bytes(self, image_bytes: bytes) -> dict:
        arr = np.frombuffer(image_bytes, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if frame is None:
            return _face_result("unknown", 0.0, False)
        self._frame_count = self.interval_frames - 1
        return self.analyze_frame(frame)
