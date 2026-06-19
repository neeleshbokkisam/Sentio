import threading
import time

import cv2

from app.mood_logger import MoodLogger
from desktop.overlay import draw_dashboard
from modules.calibration import apply_calibration, load_profile
from modules.config import AUDIO_DURATION, CAMERA_INDEX, LOG_INTERVAL_SEC, RECORD_SAMPLE_RATE
from modules.face_detector import FaceDetector
from modules.fusion import fuse_mood
from modules.voice_detector import detect_voice_emotion, record_audio


class EmotionState:
    def __init__(self):
        self._lock = threading.Lock()
        self.face = {"emotion": "detecting", "confidence": 0.0, "detected": False}
        self.voice = {"emotion": "detecting", "confidence": 0.0}
        self.fused = {"mood": "calculating", "mismatch": False}

    def update(self, face, voice, fused):
        with self._lock:
            self.face = face
            self.voice = voice
            self.fused = fused

    def snapshot(self):
        with self._lock:
            return dict(self.face), dict(self.voice), dict(self.fused)


def _voice_loop(state: EmotionState, stop_event: threading.Event):
    profile = load_profile()
    while not stop_event.is_set():
        try:
            audio, sr = record_audio(AUDIO_DURATION, RECORD_SAMPLE_RATE)
            voice = detect_voice_emotion(audio, sr)
            face, _, _ = state.snapshot()
            face, voice = apply_calibration(face, voice, profile)
            fused = fuse_mood(face, voice)
            state.update(face, voice, fused)
        except Exception as e:
            print("voice thread error:", e)
        time.sleep(0.5)


def run_desktop(interval_frames: int = 10):
    state = EmotionState()
    stop_event = threading.Event()
    detector = FaceDetector(interval_frames=interval_frames)
    profile = load_profile()
    logger = MoodLogger(mode="desktop", calibrated=profile is not None)

    voice_thread = threading.Thread(
        target=_voice_loop, args=(state, stop_event), daemon=True
    )
    voice_thread.start()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    last_log = time.time()

    print("Sentio desktop running. Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("failed to grab frame")
            break

        frame = cv2.resize(frame, (640, 360))
        face = detector.analyze_frame(frame)
        face, _ = apply_calibration(face, {}, profile)
        _, voice, fused = state.snapshot()
        fused = fuse_mood(face, voice)
        state.update(face, voice, fused)

        frame = draw_dashboard(frame, face, voice, fused)
        cv2.imshow("Sentio - Live Mood", frame)

        if time.time() - last_log > LOG_INTERVAL_SEC:
            logger.log(face, voice, fused)
            last_log = time.time()

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    stop_event.set()
    cap.release()
    cv2.destroyAllWindows()
    logger.end_session()
    print("session saved")
