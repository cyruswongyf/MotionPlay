"""
Enhanced gesture recognition with keyboard control

Features:
- Recognizes custom gestures and types corresponding keys
- Configurable gesture-to-key mapping
- Adjustable confidence threshold and cooldown time
- Support for special keys (Enter, Space, Backspace, etc.)

Press 'q' to quit
"""

import cv2
import time
import sys
import os
from pynput.keyboard import Controller, Key

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.custom_gesture_classifier import CustomGestureClassifier


# ============= CONFIGURATION =============
# Gesture to key mapping
# You can map gestures to characters or special keys
GESTURE_MAPPING = {
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    'thumbs_up': Key.enter,    # Example: map gesture to Enter key
    'peace': Key.space,         # Example: map gesture to Space key
    'fist': Key.backspace,      # Example: map gesture to Backspace
}

# Confidence threshold (0.0 - 1.0)
# Only trigger keyboard input if confidence is above this value
CONFIDENCE_THRESHOLD = 0.7

# Cooldown time in seconds
# Prevents repeated typing of the same gesture
COOLDOWN_TIME = 1.0

# Enable/Disable keyboard typing
ENABLE_KEYBOARD = True
# ========================================


def main():
    # Initialize keyboard controller
    keyboard = Controller()
    
    # Track last gesture to avoid repeated typing
    last_gesture = None
    last_gesture_time = 0
    
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
    
    print("\n" + "="*60)
    print("Gesture Keyboard Control Started")
    print("="*60)
    print(f"Keyboard typing: {'ENABLED' if ENABLE_KEYBOARD else 'DISABLED'}")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}")
    print(f"Cooldown time: {COOLDOWN_TIME}s")
    print("\nGesture Mapping:")
    for gesture, key in GESTURE_MAPPING.items():
        key_name = key if isinstance(key, str) else f"Key.{key.name}"
        print(f"  {gesture} -> {key_name}")
    print("\nPress 'q' to quit")
    print("="*60 + "\n")
    
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
            
            # Handle keyboard input based on recognized gestures
            current_time = time.time()
            if gestures and ENABLE_KEYBOARD:
                # Process each detected hand
                for gesture_data in gestures:
                    gesture_name = gesture_data['gesture']
                    confidence = gesture_data['confidence']
                    handedness = gesture_data['handedness']
                    
                    # Convert gesture_name to string (in case it's numpy.int64 or other type)
                    gesture_name = str(gesture_name)
                    
                    # Check if gesture is in mapping and meets confidence threshold
                    if gesture_name in GESTURE_MAPPING and confidence >= CONFIDENCE_THRESHOLD:
                        # Check cooldown
                        if gesture_name != last_gesture or (current_time - last_gesture_time) > COOLDOWN_TIME:
                            # Get the key to press
                            key_to_press = GESTURE_MAPPING[gesture_name]
                            
                            # Press the key
                            if isinstance(key_to_press, str):
                                keyboard.type(key_to_press)
                                print(f"✓ Typed '{key_to_press}' | Gesture: {gesture_name} ({handedness}) | Confidence: {confidence:.2f}")
                            else:
                                keyboard.press(key_to_press)
                                keyboard.release(key_to_press)
                                print(f"✓ Pressed Key.{key_to_press.name} | Gesture: {gesture_name} ({handedness}) | Confidence: {confidence:.2f}")
                            
                            # Update tracking
                            last_gesture = gesture_name
                            last_gesture_time = current_time
                            
                            # Only process first hand to avoid multiple inputs
                            break
            
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
            info_lines = []
            info_lines.append(f"FPS: {current_fps:.0f} | Keyboard: {'ON' if ENABLE_KEYBOARD else 'OFF'}")
            
            if gestures:
                for g in gestures:
                    gesture_text = f"{g['handedness']}: {g['gesture']} ({g['confidence']:.2f})"
                    if g['gesture'] in GESTURE_MAPPING and g['confidence'] >= CONFIDENCE_THRESHOLD:
                        gesture_text += " ✓"
                    info_lines.append(gesture_text)
            
            # Draw info text
            y_pos = 30
            for line in info_lines:
                cv2.putText(annotated, line, (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_pos += 30
            
            cv2.imshow('Gesture Keyboard Control', annotated)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        cap.release()
        gesture_classifier.release()
        cv2.destroyAllWindows()
        print("\n" + "="*60)
        print("Program finished")
        print("="*60)


if __name__ == "__main__":
    main()
