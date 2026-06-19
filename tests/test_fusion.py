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


def test_fuse_no_face():
    face = {"emotion": "no_face", "confidence": 0, "detected": False}
    voice = {"emotion": "sad", "confidence": 0.6}
    result = fuse_mood(face, voice)
    assert result["mood"] == "sad"


def test_fuse_mismatch():
    face = {"emotion": "happy", "confidence": 0.8, "detected": True}
    voice = {"emotion": "sad", "confidence": 0.6}
    result = fuse_mood(face, voice)
    assert result["mood"] == "happy/sad"
    assert result["mismatch"] is True
