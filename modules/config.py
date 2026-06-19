import os
from pathlib import Path

# === CONFIG ===
SAMPLE_RATE = 16000  # speechbrain wants 16kHz
RECORD_SAMPLE_RATE = 22050
AUDIO_DURATION = 3  # seconds
DEEPFACE_INTERVAL_FRAMES = 10
DEEPFACE_INTERVAL_BACKGROUND = 30  # menu bar — less CPU
CAMERA_INDEX = int(os.getenv("SENTIO_CAMERA", "0"))
LOG_INTERVAL_SEC = 2

SENTIO_DIR = Path.home() / ".sentio"
SESSIONS_DIR = SENTIO_DIR / "sessions"
CALIBRATION_FILE = SENTIO_DIR / "calibration.json"
DB_PATH = SENTIO_DIR / "sentio.db"

FLASK_HOST = os.getenv("SENTIO_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("SENTIO_PORT", "5000"))

EMOTIONS = ("angry", "disgust", "fear", "happy", "sad", "surprise", "neutral")

MOOD_COLORS = {
    "angry": {"bgr": (0, 0, 255), "hex": "#ef4444"},
    "disgust": {"bgr": (0, 128, 128), "hex": "#84cc16"},
    "fear": {"bgr": (128, 0, 128), "hex": "#a855f7"},
    "happy": {"bgr": (0, 200, 255), "hex": "#f59e0b"},
    "sad": {"bgr": (255, 150, 0), "hex": "#3b82f6"},
    "surprise": {"bgr": (0, 255, 0), "hex": "#22c55e"},
    "neutral": {"bgr": (180, 180, 180), "hex": "#6b7280"},
    "unknown": {"bgr": (128, 128, 128), "hex": "#9ca3af"},
}

SPEECHBRAIN_MODEL = "speechbrain/emotion-recognition-wav2vec2-IEMOCAP"

VOICE_LABEL_MAP = {
    "ang": "angry",
    "angry": "angry",
    "hap": "happy",
    "happy": "happy",
    "sad": "sad",
    "neu": "neutral",
    "neutral": "neutral",
    "exc": "happy",
    "fru": "angry",
}
