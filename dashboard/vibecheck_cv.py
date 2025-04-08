import cv2
import numpy as np
import threading
import sounddevice as sd
import librosa
from sklearn.preprocessing import StandardScaler
from deepface import DeepFace
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import time

# === CONFIG ===
SAMPLE_RATE = 22050
DURATION = 3  # seconds

voice_emotion = "Detecting..."
face_emotion = "Detecting..."
final_mood = "Calculating..."
mood_log = []

# === Voice emotion detection thread ===
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

# === Start voice detection thread
voice_thread = threading.Thread(target=get_voice_emotion, daemon=True)
voice_thread.start()

cap = cv2.VideoCapture(0)
frame_count = 0
last_log_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("⚠️ Failed to grab frame.")
        break

    # === Resize frame to improve speed (optional)
    frame = cv2.resize(frame, (640, 360))

    # === Limit DeepFace to every 10 frames
    frame_count += 1
    if frame_count % 10 == 0:
        try:
            small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            result = DeepFace.analyze(small, actions=['emotion'], enforce_detection=False, detector_backend='opencv')
            face_emotion = result[0]['dominant_emotion']
        except Exception as e:
            print("🧠 Face detection error:", e)
            face_emotion = "no face"

    # === Mood fusion
    if face_emotion == voice_emotion:
        final_mood = face_emotion
    elif "no face" in face_emotion:
        final_mood = voice_emotion
    else:
        final_mood = f"{face_emotion}/{voice_emotion}"

    # === Draw overlays
    cv2.putText(frame, f"🧠 Face: {face_emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 255), 2)
    cv2.putText(frame, f"🎤 Voice: {voice_emotion}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    cv2.putText(frame, f"🎭 Mood: {final_mood}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 3)

    # === Log every 2 seconds only
    if time.time() - last_log_time > 2:
        timestamp = datetime.now().strftime("%H:%M:%S")
        mood_log.append({
            "time": timestamp,
            "face": face_emotion,
            "voice": voice_emotion,
            "final": final_mood
        })
        last_log_time = time.time()

    # === Display the feed
    cv2.imshow("VibeCheck.AI - Real-Time Fusion", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# === Plot mood timeline
df = pd.DataFrame(mood_log)
plt.figure(figsize=(12, 5))
plt.plot(df["time"], df["final"], marker="o", linestyle='-', color="purple", label="Fused Mood")
plt.xticks(rotation=45)
plt.xlabel("Time")
plt.ylabel("Mood")
plt.title("Mood Timeline (Face + Voice Fusion)")
plt.grid(True)
plt.tight_layout()
plt.legend()
plt.show()
