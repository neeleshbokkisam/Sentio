import json

import pytest

from modules.fusion import fuse_mood, normalize_emotion


def test_normalize_emotion():
    assert normalize_emotion("Happy") == "happy"
    assert normalize_emotion("no face detected") == "no_face"


def test_fuse_agreement():
    face = {"emotion": "happy", "confidence": 0.8, "detected": True}
    voice = {"emotion": "happy", "confidence": 0.7}
    result = fuse_mood(face, voice)
    assert result["mood"] == "happy"
    assert result["mismatch"] is False
    assert result["face_signal"] == "strong"
    assert result["voice_signal"] == "strong"


def test_fuse_no_face():
    face = {"emotion": "no_face", "confidence": 0, "detected": False}
    voice = {"emotion": "sad", "confidence": 0.6}
    result = fuse_mood(face, voice)
    assert result["mood"] == "sad"
    assert result["face_offline"] is True
    assert result["face_signal"] == "offline"


def test_fuse_mismatch():
    face = {"emotion": "happy", "confidence": 0.8, "detected": True}
    voice = {"emotion": "sad", "confidence": 0.6}
    result = fuse_mood(face, voice)
    assert result["mood"] == "happy/sad"
    assert result["mismatch"] is True


def test_face_result_json_serializable():
    pytest.importorskip("cv2")
    pytest.importorskip("deepface")
    from unittest.mock import patch
    import numpy as np
    from modules.face_detector import FaceDetector

    with patch("deepface.DeepFace") as mock:
        mock.analyze.return_value = [{
            "dominant_emotion": "happy",
            "emotion": {"happy": 90.0, "sad": 5.0},
        }]
        det = FaceDetector(interval_frames=1)
        result = det.analyze_frame(np.zeros((360, 640, 3), dtype=np.uint8))
        json.dumps(result)
