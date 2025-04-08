import cv2
from fer import FER

# Initialize webcam
cap = cv2.VideoCapture(0)
detector = FER(mtcnn=True)  # More accurate with mtcnn=True

print("Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect emotion
    result = detector.detect_emotions(frame)

    # Display results
    for face in result:
        (x, y, w, h) = face["box"]
        emotions = face["emotions"]
        top_emotion = max(emotions, key=emotions.get)

        # Draw box & emotion
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(frame, f'{top_emotion}', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("VibeCheck.AI - Facial Emotion Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
