import sounddevice as sd
import numpy as np
import librosa
import time
from sklearn.preprocessing import StandardScaler
from joblib import load

# CONFIG
DURATION = 3  # seconds
SAMPLE_RATE = 22050  # Hz

# ====== Dummy Classifier (Replace with real ML model later) ======
def simple_emotion_classifier(mfcc):
    avg_mfcc = np.mean(mfcc)
    if avg_mfcc > 0.1:
        return "happy 😄"
    elif avg_mfcc < -0.1:
        return "sad 😢"
    else:
        return "neutral 😐"

# ====== Record + Predict ======
def record_and_predict():
    print("🎙️ Listening...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
    sd.wait()

    # Convert to 1D array
    audio = audio.flatten()

    # Extract MFCCs
    mfcc = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=13)
    
    # Optional: scale features
    mfcc_scaled = StandardScaler().fit_transform(mfcc)

    # Predict emotion (placeholder logic for now)
    emotion = simple_emotion_classifier(mfcc_scaled)

    print(f"🧠 Voice Emotion: {emotion}")
    return emotion

# ====== Real-time loop ======
try:
    while True:
        record_and_predict()
        time.sleep(0.5)  # brief pause between chunks

except KeyboardInterrupt:
    print("\n🚪 Exiting voice emotion detection.")
