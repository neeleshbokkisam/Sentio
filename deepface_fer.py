import cv2
from deepface import DeepFace

# Start webcam
cap = cv2.VideoCapture(0)
print("Press 'q' to quit")

frame_count = 0
emotion_label = "Detecting..."

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    frame_count += 1

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Run detection every 10 frames
    if frame_count % 10 == 0:
        try:
            result = DeepFace.analyze(
                small_frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'  # Faster than default
            )
            emotion_label = result[0]['dominant_emotion']
            print("✅ Emotion:", emotion_label)
        except Exception as e:
            print("⚠️ Detection error:", e)
            emotion_label = "No face"

    # Show last known emotion on full frame
    cv2.putText(frame, f'Emotion: {emotion_label}', (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("VibeCheck.AI - Fast Mode", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
