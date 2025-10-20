import cv2
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.hand_landmarker import HandLandmarker

# Parameters
CSV_FILENAME = '../data/gesture_landmarks.csv'
GESTURE_LABEL = '5'

# Initialize camera and hand_landmarker
cap = cv2.VideoCapture(0)
hand_landmarker = HandLandmarker()

print("Press 's' to save current hand landmarks, press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    timestamp_ms = int(time.time() * 1000)
    hand_landmarker.detect_async(frame, timestamp_ms)
    annotated = hand_landmarker.draw_landmarks_on_frame(frame)
    cv2.imshow('Hand Landmarks', annotated)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        # Save landmarks
        hand_landmarker.save_landmarks_to_csv(CSV_FILENAME, gesture_label=GESTURE_LABEL)
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hand_landmarker.release()
print("Finished.")
