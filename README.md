# 🧠 VibeCheck.AI

> Real-time emotion detection from your **face** and **voice** — fused into one final vibe 🎭

VibeCheck.AI is a fun and powerful multimodal AI tool that uses your **webcam** and **microphone** to detect how you're feeling — based on **facial expressions** and **tone of voice**. It shows everything in a live OpenCV window with instant updates.

---

<!-- ## 🎬 Demo

![Demo GIF](assets/demo.gif)  
*(Optional — add a screen recording or screenshot here)*

--- -->

## 💡 Features

- 🧠 **Facial Emotion Detection** using DeepFace
- 🎤 **Voice Emotion Detection** from MFCC features (librosa)
- 🔀 **Fusion Logic** to combine both inputs into a final "vibe"
- 🪞 Live webcam feed with overlaid emotions
- 💻 Cross-platform and real-time (no browser, no freezing!)

---

## 🛠️ Tech Stack

- `Python 3.10`
- `OpenCV` — webcam + display
- `DeepFace` — facial emotion recognition
- `librosa` + `sounddevice` — real-time voice capture + analysis
- `NumPy`, `threading` — smooth and async logic

---

## 🚀 Getting Started


```bash
1. Clone this repo

git clone https://github.com/YOUR_USERNAME/VibeCheck.AI.git
cd VibeCheck.AI

2. Create a virtual environment (optional)

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Run the app

python3 vibecheck_cv.py
Press Q to quit

