import cv2
import time
import os
from utils.pose_landmarker import PoseLandmarker
from utils.hand_landmarker import HandLandmarker
from utils.custom_gesture_classifier import CustomGestureClassifier
from pynput.keyboard import Controller, Key


def main():
    # Check if custom trained gesture model exists
    custom_model_path = 'custom_gesture_recognizer/gesture_classifier.pkl'
    use_custom_gesture = os.path.exists(custom_model_path)
    
    # Initialize keyboard controller
    keyboard = Controller()
    
    # Track last gesture to avoid repeated typing
    last_gesture = None
    last_gesture_time = 0
    gesture_cooldown = 1.0  # seconds between same gesture inputs
    
    # Initialize landmarkers
    pose_detector = PoseLandmarker('models/pose_landmarker.task')
    
    # Choose gesture recognition mode based on model availability
    if use_custom_gesture:
        print("Using custom trained gesture recognition model")
        gesture_classifier = CustomGestureClassifier(
            model_path=custom_model_path,
            hand_landmarker_path='models/hand_landmarker.task'
        )
        hand_detector = None
    else:
        print("Using basic hand landmark detection")
        hand_detector = HandLandmarker('models/hand_landmarker.task')
        gesture_classifier = None

    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    # Minimize camera buffer to reduce latency
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    timestamp_ms = 0
    frame_count = 0
    fps_start_time = time.time()
    fps_counter = 0
    current_fps = 0
    grab_count = 1

    print("Starting pose + hand detection... Press 'q' to quit")
    if use_custom_gesture:
        print("Custom gestures: 1, 2, 3, 4, 5")

    try:
        while True:
            # Clear camera buffer by skipping old frames
            for _ in range(grab_count):
                cap.grab()
            ret, frame = cap.retrieve()
            
            if not ret:
                print("Error: Could not read frame")
                break

            timestamp_ms += 33

            # Detect poses and hands asynchronously
            pose_detector.detect_async(frame, timestamp_ms)
            
            if use_custom_gesture:
                # Use custom gesture recognition
                gesture_classifier.detect_async(frame, timestamp_ms)
                gestures = gesture_classifier.predict_gestures()
                
                # Handle keyboard input based on recognized gestures
                current_time = time.time()
                if gestures:
                    # Get the first hand's gesture (you can modify to handle multiple hands)
                    primary_gesture = gestures[0]['gesture']
                    confidence = gestures[0]['confidence']
                    
                    # Only type if confidence is high enough and cooldown period has passed
                    if confidence > 0.7:  # confidence threshold
                        if primary_gesture != last_gesture or (current_time - last_gesture_time) > gesture_cooldown:
                            # Convert gesture to string (in case it's numpy.int64 or other type)
                            gesture_str = str(primary_gesture)
                            
                            # Type the gesture
                            keyboard.type(gesture_str)
                            print(f"Typed: {gesture_str} (confidence: {confidence:.2f})")
                            
                            # Update tracking
                            last_gesture = primary_gesture
                            last_gesture_time = current_time
            else:
                # Use basic hand detection
                hand_detector.detect_async(frame, timestamp_ms)

            # Draw landmarks on frame
            annotated_frame = pose_detector.draw_landmarks_on_frame(frame)
            
            if use_custom_gesture:
                annotated_frame = gesture_classifier.draw_on_frame(annotated_frame)
            else:
                annotated_frame = hand_detector.draw_landmarks_on_frame(annotated_frame)

            # Mirror the frame horizontally
            annotated_frame = cv2.flip(annotated_frame, 1)

            # Get detection status
            pose_data = pose_detector.get_landmark_data()
            
            if use_custom_gesture:
                # Display gesture recognition results
                gesture_info = []
                for g in gestures:
                    gesture_info.append(f"{g['handedness']}: {g['gesture']} ({g['confidence']:.2f})")
                hands_status = " | ".join(gesture_info) if gesture_info else "No hands"
            else:
                hand_data = hand_detector.get_landmark_data()
                num_hands = len(hand_data.hand_landmarks) if hand_data and hand_data.hand_landmarks else 0
                hands_status = f"Hands:{num_hands}"
            
            # Calculate FPS
            fps_counter += 1
            elapsed_time = time.time() - fps_start_time
            if elapsed_time > 1.0:
                current_fps = fps_counter / elapsed_time
                fps_counter = 0
                fps_start_time = time.time()
                
                # Auto-adjust grab count based on FPS
                if current_fps > 28:
                    grab_count = 1
                elif current_fps > 25:
                    grab_count = 2
                else:
                    grab_count = 3

            pose_status = "Pose" if pose_data and pose_data.pose_landmarks else "No pose"
            info_text = f"{pose_status} | {hands_status} | FPS: {current_fps:.0f}"
            cv2.putText(annotated_frame, info_text, (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)  # White text
            
            frame_count += 1

            window_title = 'Pose + Custom Gesture Recognition' if use_custom_gesture else 'Pose + Hand Detection'
            cv2.imshow(window_title, annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        # Clean up
        cap.release()
        pose_detector.release()
        if use_custom_gesture:
            gesture_classifier.release()
        else:
            hand_detector.release()
        cv2.destroyAllWindows()
        print("Application closed successfully")


if __name__ == "__main__":
    main()