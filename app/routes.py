import base64
import io
import wave

import numpy as np
from flask import Flask, jsonify, render_template, request, Response

from app.insights import daily_insights, export_session_csv, get_session_replay, list_sessions, weekly_insights
from app.mood_logger import MoodLogger
from modules.calibration import apply_calibration, load_profile, save_profile, CalibrationProfile
from modules.face_detector import FaceDetector
from modules.fusion import fuse_mood
from modules.voice_detector import detect_voice_emotion

face_detector = FaceDetector()
mood_logger = MoodLogger(mode="web", calibrated=load_profile() is not None)


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/insights")
    def insights_page():
        return render_template("insights.html")

    @app.route("/calibrate")
    def calibrate_page():
        return render_template("calibrate.html")

    @app.route("/api/analyze/face", methods=["POST"])
    def analyze_face():
        data = request.get_json(silent=True) or {}
        image_b64 = data.get("image", "")
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]
        try:
            image_bytes = base64.b64decode(image_b64)
            result = face_detector.analyze_image_bytes(image_bytes)
            profile = load_profile()
            if profile:
                result, _ = apply_calibration(result, {}, profile)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e), "emotion": "unknown", "confidence": 0, "detected": False}), 400

    @app.route("/api/analyze/voice", methods=["POST"])
    def analyze_voice():
        try:
            data = request.get_json(silent=True) or {}
            if "samples" in data:
                audio = np.array(data["samples"], dtype=np.float32)
                sr = int(data.get("sample_rate", 16000))
            else:
                raw = request.get_data()
                audio, sr = _parse_wav(raw)

            result = detect_voice_emotion(audio, sr)
            profile = load_profile()
            if profile:
                _, result = apply_calibration({}, result, profile)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e), "emotion": "unknown", "confidence": 0}), 400

    @app.route("/api/analyze/fusion", methods=["POST"])
    def analyze_fusion():
        data = request.get_json(silent=True) or {}
        face = data.get("face", {})
        voice = data.get("voice", {})
        profile = load_profile()
        if profile:
            face, voice = apply_calibration(face, voice, profile)
        fused = fuse_mood(face, voice)
        mood_logger.log(face, voice, fused)
        return jsonify({"face": face, "voice": voice, **fused})

    @app.route("/api/session")
    def current_session():
        return jsonify(mood_logger.get_current_session_readings())

    @app.route("/api/sessions")
    def sessions():
        return jsonify(list_sessions())

    @app.route("/api/sessions/<int:session_id>/replay")
    def session_replay(session_id):
        data = get_session_replay(session_id)
        if not data:
            return jsonify({"error": "not found"}), 404
        return jsonify(data)

    @app.route("/api/insights/daily")
    def insights_daily():
        return jsonify(daily_insights())

    @app.route("/api/insights/weekly")
    def insights_weekly():
        return jsonify(weekly_insights())

    @app.route("/api/export/<int:session_id>")
    def export_session(session_id):
        csv_data = export_session_csv(session_id)
        if not csv_data:
            return jsonify({"error": "not found"}), 404
        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sentio_session_{session_id}.csv"},
        )

    @app.route("/api/calibrate", methods=["POST"])
    def calibrate_api():
        data = request.get_json(silent=True) or {}
        step = data.get("step")
        samples = data.get("samples", {})

        if step == "save":
            profile = CalibrationProfile(
                neutral_face=samples.get("neutral_face", {}),
                happy_face=samples.get("happy_face", {}),
                neutral_voice=samples.get("neutral_voice", {}),
                created_at=data.get("created_at", ""),
            )
            save_profile(profile)
            return jsonify({"ok": True, "profile": profile.to_dict()})

        return jsonify({"ok": True, "step": step})

    @app.route("/api/calibration/status")
    def calibration_status():
        profile = load_profile()
        return jsonify({"calibrated": profile is not None, "profile": profile.to_dict() if profile else None})

    return app


def _parse_wav(raw: bytes):
    buf = io.BytesIO(raw)
    with wave.open(buf, "rb") as wf:
        sr = wf.getframerate()
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
    return audio, sr
