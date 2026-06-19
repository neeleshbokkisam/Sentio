import subprocess
import sys
import threading
import time
import webbrowser

import cv2
import rumps

from modules.calibration import apply_calibration, load_profile
from modules.config import AUDIO_DURATION, CAMERA_INDEX, DEEPFACE_INTERVAL_BACKGROUND, RECORD_SAMPLE_RATE
from modules.face_detector import FaceDetector
from modules.fusion import fuse_mood
from modules.voice_detector import detect_voice_emotion, record_audio


class SentioMenuBar:
    def __init__(self):
        self._rumps = rumps
        self.app = rumps.App("Sentio", quit_button=None)
        self._history_items = [
            rumps.MenuItem("—", callback=None) for _ in range(5)
        ]
        self.app.menu = [
            rumps.MenuItem("Loading...", callback=None),
            None,
            *self._history_items,
            None,
            rumps.MenuItem("Open Dashboard", callback=self.open_dashboard),
            rumps.MenuItem("Calibrate", callback=self.calibrate),
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]

        self.state = {"face": {}, "voice": {}, "fused": {}}
        self.history = []
        self._stop = threading.Event()
        self._status_item = self.app.menu["Loading..."]

    def _capture_loop(self):
        detector = FaceDetector(interval_frames=DEEPFACE_INTERVAL_BACKGROUND)
        profile = load_profile()
        cap = cv2.VideoCapture(CAMERA_INDEX)

        while not self._stop.is_set():
            try:
                ret, frame = cap.read()
                if ret:
                    face = detector.analyze_frame(frame)
                    face, _ = apply_calibration(face, {}, profile)
                else:
                    face = {"emotion": "no_face", "confidence": 0, "detected": False}

                audio, sr = record_audio(AUDIO_DURATION, RECORD_SAMPLE_RATE)
                voice = detect_voice_emotion(audio, sr)
                face, voice = apply_calibration(face, voice, profile)
                fused = fuse_mood(face, voice)

                self.state = {"face": face, "voice": voice, "fused": fused}
                self.history = ([{"face": face, "voice": voice, "fused": fused}] + self.history)[:5]
                mood = fused.get("mood", "?").split("/")[0]
                self._status_item.title = f"● {mood}"
                for i, item in enumerate(self._history_items):
                    if i < len(self.history):
                        h = self.history[i]["fused"]
                        item.title = f"{h.get('mood')} (f:{self.history[i]['face'].get('emotion')} v:{self.history[i]['voice'].get('emotion')})"
                    else:
                        item.title = "—"
            except Exception as e:
                self._status_item.title = f"error: {e}"
            time.sleep(3)

        cap.release()

    def open_dashboard(self, _):
        webbrowser.open("http://127.0.0.1:5000")

    def calibrate(self, _):
        subprocess.Popen([sys.executable, "run.py", "calibrate"])

    def quit_app(self, _):
        self._stop.set()
        self._rumps.quit_application()

    def run(self):
        t = threading.Thread(target=self._capture_loop, daemon=True)
        t.start()
        self.app.run()


def run_menu_bar():
    bar = SentioMenuBar()
    bar.run()
