import sqlite3
import threading
import time
from datetime import datetime

from modules.config import DB_PATH, SENTIO_DIR


class MoodLogger:
    def __init__(self, mode: str = "desktop", calibrated: bool = False):
        SENTIO_DIR.mkdir(parents=True, exist_ok=True)
        self.mode = mode
        self.session_id = None
        self._lock = threading.Lock()
        self._buffer = []
        self._last_flush = time.time()
        self._init_db()
        self.start_session(calibrated=calibrated)

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                mode TEXT,
                calibrated INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                face TEXT,
                face_conf REAL,
                voice TEXT,
                voice_conf REAL,
                mood TEXT,
                mismatch INTEGER DEFAULT 0,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );
        """)
        conn.commit()
        conn.close()

    def start_session(self, calibrated: bool = False):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sessions (started_at, mode, calibrated) VALUES (?, ?, ?)",
            (datetime.now().isoformat(), self.mode, int(calibrated)),
        )
        self.session_id = cur.lastrowid
        conn.commit()
        conn.close()

    def log(self, face: dict, voice: dict, fused: dict):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "face": fused.get("face_emotion", face.get("emotion")),
            "face_conf": fused.get("face_confidence", face.get("confidence", 0)),
            "voice": fused.get("voice_emotion", voice.get("emotion")),
            "voice_conf": fused.get("voice_confidence", voice.get("confidence", 0)),
            "mood": fused.get("mood"),
            "mismatch": int(fused.get("mismatch", False)),
        }
        with self._lock:
            self._buffer.append(entry)
        if time.time() - self._last_flush > 10:
            self.flush()

    def flush(self):
        with self._lock:
            if not self._buffer or self.session_id is None:
                return
            rows = list(self._buffer)
            self._buffer.clear()

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        for row in rows:
            cur.execute(
                """INSERT INTO readings
                   (session_id, timestamp, face, face_conf, voice, voice_conf, mood, mismatch)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self.session_id,
                    row["timestamp"],
                    row["face"],
                    row["face_conf"],
                    row["voice"],
                    row["voice_conf"],
                    row["mood"],
                    row["mismatch"],
                ),
            )
        conn.commit()
        conn.close()
        self._last_flush = time.time()

    def end_session(self):
        self.flush()
        if self.session_id is None:
            return
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE sessions SET ended_at = ? WHERE id = ?",
            (datetime.now().isoformat(), self.session_id),
        )
        conn.commit()
        conn.close()

    def get_current_session_readings(self):
        self.flush()
        if self.session_id is None:
            return []
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM readings WHERE session_id = ? ORDER BY timestamp",
            (self.session_id,),
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
