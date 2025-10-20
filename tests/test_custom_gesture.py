"""
Test custom gesture classifier

Run this script to test the trained gesture recognition model
Press 'q' to quit
"""

import cv2
import time
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.custom_gesture_classifier import CustomGestureClassifier

def main():
    # Initialize custom gesture classifier
    try:
        gesture_classifier = CustomGestureClassifier(
            model_path='../custom_gesture_recognizer/gesture_classifier.pkl',
            hand_landmarker_path='../models/hand_landmarker.task'
        )
    except Exception as e:
        print(f"Error: Unable to load model")
        print(f"Details: {e}")
        print("\nPlease ensure:")
        print("1. You have collected data using collect_gesture_data.py")
        print("2. You have trained the model using train_custom_gesture_classifier.py")
        return
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to open camera")
        return
    
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    timestamp_ms = 0
    fps_start_time = time.time()
    fps_counter = 0
    current_fps = 0
    
    print("\nStarting gesture recognition...")
    print("Press 'q' to quit")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to read frame")
                break
            
            timestamp_ms += 33
            
            # Detect hands and predict gestures
            gesture_classifier.detect_async(frame, timestamp_ms)
            gestures = gesture_classifier.predict_gestures()
            
            # Draw results
            annotated = gesture_classifier.draw_on_frame(frame)
            
            # Mirror flip
            annotated = cv2.flip(annotated, 1)
            
            # Calculate FPS
            fps_counter += 1
            elapsed_time = time.time() - fps_start_time
            if elapsed_time > 1.0:
                current_fps = fps_counter / elapsed_time
                fps_counter = 0
                fps_start_time = time.time()
            
            # Display information
            info_text = f"FPS: {current_fps:.0f}"
            if gestures:
                gesture_text = " | ".join([f"{g['handedness']}: {g['gesture']}" for g in gestures])
                info_text += f" | {gesture_text}"
            
            cv2.putText(annotated, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Custom Gesture Recognition', annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        gesture_classifier.release()
        cv2.destroyAllWindows()
        print("Program finished")

if __name__ == "__main__":
    main()
