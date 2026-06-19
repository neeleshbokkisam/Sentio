import time
from pathlib import Path

from modules.config import SENTIO_DIR

LOG_PATH = SENTIO_DIR / "sentio.log"

_state = {
    "last_face": None,
    "last_voice": None,
    "last_face_error": None,
    "last_voice_error": None,
    "face_latency_ms": 0,
    "voice_latency_ms": 0,
    "voice_backend": "unknown",
}


def log(msg: str):
    SENTIO_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n"
    with open(LOG_PATH, "a") as f:
        f.write(line)


def record_face(result: dict, latency_ms: float, error: str = None):
    _state["last_face"] = result
    _state["face_latency_ms"] = round(latency_ms, 1)
    _state["last_face_error"] = error
    if error:
        log(f"face error: {error}")


def record_voice(result: dict, latency_ms: float, backend: str = "unknown", error: str = None):
    _state["last_voice"] = result
    _state["voice_latency_ms"] = round(latency_ms, 1)
    _state["voice_backend"] = backend
    _state["last_voice_error"] = error
    if error:
        log(f"voice error: {error}")


def get_status(extra: dict = None) -> dict:
    out = dict(_state)
    if extra:
        out.update(extra)
    return out
