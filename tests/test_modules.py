from unittest.mock import patch

import numpy as np
import pytest

from modules.fusion import fuse_mood
from modules.voice_detector import _fallback_detect


def test_fallback_detect():
    pytest.importorskip("librosa")

    audio = np.random.randn(16000).astype(np.float32)
    result = _fallback_detect(audio, 16000)
    assert "emotion" in result
    assert result["emotion"] in ("happy", "sad", "neutral")


def test_face_detector():
    pytest.importorskip("cv2")
    pytest.importorskip("deepface")

    with patch("deepface.DeepFace") as mock_deepface:
        mock_deepface.analyze.return_value = [{
            "dominant_emotion": "happy",
            "emotion": {"happy": 90, "sad": 5, "neutral": 5},
        }]
        from modules.face_detector import FaceDetector

        detector = FaceDetector(interval_frames=1)
        frame = np.zeros((360, 640, 3), dtype=np.uint8)
        result = detector.analyze_frame(frame)
        assert result["emotion"] == "happy"
        assert result["detected"] is True


def test_fusion_with_mocked_inputs():
    face = {"emotion": "neutral", "confidence": 0.5, "detected": True}
    voice = {"emotion": "neutral", "confidence": 0.5}
    assert fuse_mood(face, voice)["mismatch"] is False
