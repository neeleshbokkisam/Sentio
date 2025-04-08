import cv2
import numpy as np
import threading
import sounddevice as sd
import librosa
from sklearn.preprocessing import StandardScaler
from deepface import DeepFace
from PIL import Image, ImageTk
import tkinter as tk
import time

# === CONFIG ===
SAMPLE_RATE = 22050
DURATION = 3  # seconds

# === SHARED STATE ===
voice_emotion = "Detecting..."
face_emotion = "Detecting..."
final_mood = "Calculating..."

# === Dummy Voice Emotion Detection ===
def get_voice_emotion():
    global voice_emotion
    while True:
        try:
            audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()
            audio = audio.flatten()
            mfcc = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=40)
            mfcc_scaled = np.mean(mfcc.T, axis=0)

            avg = np.mean(mfcc_scaled)
            if avg > 0.1:
                voice_emotion = "happy"
            elif avg < -0.1:
                voice_emotion = "sad"
            else:
                voice_emotion = "neutral"
        except Exception as e:
            print("🎤 Voice error:", e)
            voice_emotion = "unknown"

        time.sleep(0.5)

# === Main App Window ===
class VibeCheckApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VibeCheck.AI")
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            print("🚫 Cannot access webcam.")
            self.cap = None

        self.label = tk.Label(root, text="🔄 Initializing webcam...")
        self.label.pack()

        self.face_label = tk.Label(root, text="🧠 Face: ...", font=("Helvetica", 14))
        self.face_label.pack()

        self.voice_label = tk.Label(root, text="🎤 Voice: ...", font=("Helvetica", 14))
        self.voice_label.pack()

        self.mood_label = tk.Label(root, text="🎭 Mood: ...", font=("Helvetica", 16, "bold"))
        self.mood_label.pack()

        self.update_frame()

    def update_frame(self):
        global face_emotion, final_mood

        if self.cap:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                try:
                    small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                    result = DeepFace.analyze(small, actions=['emotion'], enforce_detection=False, detector_backend='opencv')
                    face_emotion = result[0]['dominant_emotion']
                except Exception as e:
                    print("🧠 Face error:", e)
                    face_emotion = "no face"

                if face_emotion == voice_emotion:
                    final_mood = face_emotion
                elif "no face" in face_emotion:
                    final_mood = voice_emotion
                else:
                    final_mood = f"mixed ({face_emotion}/{voice_emotion})"

                try:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.label.imgtk = imgtk
                    self.label.configure(image=imgtk, text="")
                except Exception as e:
                    print("🖼️ Image error:", e)
                    self.label.configure(text="⚠️ Error rendering webcam")

            else:
                print("⚠️ Failed to grab frame.")
                self.label.configure(text="⚠️ No frame from webcam")

        # Update labels regardless
        self.face_label.config(text=f"🧠 Face: {face_emotion}")
        self.voice_label.config(text=f"🎤 Voice: {voice_emotion}")
        self.mood_label.config(text=f"🎭 Mood: {final_mood}")

        self.root.after(1000, self.update_frame)

    def on_close(self):
        if self.cap:
            self.cap.release()
        self.root.destroy()

# === Start App ===
if __name__ == "__main__":
    voice_thread = threading.Thread(target=get_voice_emotion, daemon=True)
    voice_thread.start()

    root = tk.Tk()
    app = VibeCheckApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
