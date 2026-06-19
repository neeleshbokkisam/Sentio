import sys


def run_calibration_wizard():
    import cv2
    from modules.calibration import run_calibration
    from modules.config import CAMERA_INDEX

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("couldn't open camera")
        sys.exit(1)

    def on_step(step, message):
        print(f"[{step}] {message}")

    print("Sentio calibration — follow the prompts. Press Q anytime to cancel.")
    try:
        profile = run_calibration(cap, steps_callback=on_step)
        print("calibration saved:", profile.created_at)
    except KeyboardInterrupt:
        print("cancelled")
    finally:
        cap.release()


def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [desktop|web|menu|calibrate]")
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "desktop":
        from desktop.main import run_desktop
        run_desktop()
    elif cmd == "web":
        from app.routes import create_app
        from modules.config import FLASK_HOST, FLASK_PORT
        app = create_app()
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, threaded=True)
    elif cmd == "menu":
        from desktop.menu_bar import run_menu_bar
        run_menu_bar()
    elif cmd == "calibrate":
        run_calibration_wizard()
    else:
        print(f"unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
