import streamlit as st
st.set_page_config(page_title="VibeCheck.AI", layout="centered")

import sounddevice as sd
import numpy as np
import librosa
from deepface import DeepFace
from PIL import Image
import cv2
from sklearn.preprocessing import StandardScaler
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 5 seconds
st_autorefresh(interval=5000, key="vibecheck_autorefresh")

# === CONFIG ===
DURATION = 3
SAMPLE_RATE = 22050

st.title("🧠 VibeCheck.AI")
st.markdown("Real-time emotion detection from your face + voice")

frame_container = st.empty()
face_text = st.empty()
voice_text = st.empty()
fused_text = st.empty()

# === Voice detection ===
def detect_voice_emotion():
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()
    audio = audio.flatten()
    mfcc = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=40)
    mfcc_scaled = np.mean(mfcc.T, axis=0)

    avg = np.mean(mfcc_scaled)
    if avg > 0.1:
        return "happy"
    elif avg < -0.1:
        return "sad"
    else:
        return "neutral"

# === Face detection ===
def get_face_emotion():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None, "no face"
    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return None, "no face"

    try:
        small = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        result = DeepFace.analyze(small, actions=['emotion'], enforce_detection=False, detector_backend='opencv')
        emotion = result[0]['dominant_emotion']
    except Exception as e:
        print("Face detection error:", e)
        emotion = "no face"

    return frame, emotion

# === Run detection once per refresh
frame, face_emotion = get_face_emotion()
voice_emotion = detect_voice_emotion()

if face_emotion == voice_emotion:
    final_mood = face_emotion
elif "no face" in face_emotion:
    final_mood = voice_emotion
else:
    final_mood = f"mixed ({face_emotion}/{voice_emotion})"

if frame is not None:
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_pil = Image.fromarray(frame_rgb)
    frame_container.image(frame_pil, caption="Live Webcam", use_container_width=True)

face_text.markdown(f"**🧠 Face Emotion:** `{face_emotion}`")
voice_text.markdown(f"**🎤 Voice Emotion:** `{voice_emotion}`")
fused_text.markdown(f"**🎭 Final Mood:** `{final_mood}`")
