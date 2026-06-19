# Sentio

Webcam + mic → mood. DeepFace + SpeechBrain. Local only.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```bash
python run.py desktop
python run.py web
python run.py menu      # macOS only
python run.py calibrate
```

Python 3.10+, webcam, mic. First run downloads models (~2GB). Press Q to quit desktop.

Not a medical tool. Legacy prototype in `archive/`.
