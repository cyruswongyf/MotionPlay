import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np


class GestureRecognizer:
    def __init__(self, model_path='models/gesture_recognizer.task', num_hands=2):
        self.gesture_result = None
        self.gesture_recognizer = None
        self.num_hands = num_hands
        self._initialize_recognizer(model_path)

    def _initialize_recognizer(self, model_path):
        base_opt = python.BaseOptions(model_asset_path=model_path)

        options = vision.GestureRecognizerOptions(
            base_options=base_opt,
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=self.num_hands,
            result_callback=self._gesture_callback,
        )

        self.gesture_recognizer = vision.GestureRecognizer.create_from_options(options)

    def _gesture_callback(self, result, image, timestamp):
        self.gesture_result = result

    def detect_async(self, frame, timestamp_ms):
        if frame is not None:
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            self.gesture_recognizer.recognize_async(mp_image, timestamp_ms)

    def draw_gestures_on_frame(self, frame, color_left=(0, 255, 0), color_right=(0, 128, 255)):
        if frame is None or self.gesture_result is None:
            return frame

        annotated = frame.copy()
        
        gestures = self.gesture_result.gestures or []
        handedness_list = self.gesture_result.handedness or []
        hand_landmarks_list = self.gesture_result.hand_landmarks or []

        for idx, gesture_list in enumerate(gestures):
            if not gesture_list:
                continue
                
            # Get the top gesture
            gesture = gesture_list[0]
            gesture_name = gesture.category_name
            confidence = gesture.score

            # Get handedness
            hand_label = None
            color = (0, 255, 0)
            if idx < len(handedness_list):
                handedness_categories = handedness_list[idx]
                if isinstance(handedness_categories, list) and len(handedness_categories) > 0:
                    category = handedness_categories[0]
                    if hasattr(category, 'category_name'):
                        hand_label = category.category_name
                        color = color_left if hand_label == 'Left' else color_right

            # Get wrist position to display text
            if idx < len(hand_landmarks_list):
                hand_landmarks = hand_landmarks_list[idx]
                if hand_landmarks:
                    wrist = hand_landmarks[0]
                    h, w, _ = annotated.shape
                    cx, cy = int(wrist.x * w), int(wrist.y * h)
                    
                    # Display gesture name and confidence
                    text = f"{gesture_name} ({confidence:.2f})"
                    if hand_label:
                        text = f"{hand_label}: {text}"
                    
                    cv2.putText(annotated, text, (cx + 10, cy - 10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return annotated

    def get_gesture_data(self):
        return self.gesture_result

    def get_gestures(self):
        """Return list of gestures formatted as easy-to-use dictionaries"""
        if not self.gesture_result or not self.gesture_result.gestures:
            return []
        
        results = []
        gestures = self.gesture_result.gestures or []
        handedness_list = self.gesture_result.handedness or []
        
        for idx, gesture_list in enumerate(gestures):
            if not gesture_list:
                continue
            
            gesture = gesture_list[0]
            hand_label = None
            
            if idx < len(handedness_list):
                handedness_categories = handedness_list[idx]
                if isinstance(handedness_categories, list) and len(handedness_categories) > 0:
                    category = handedness_categories[0]
                    if hasattr(category, 'category_name'):
                        hand_label = category.category_name
            
            results.append({
                'gesture': gesture.category_name,
                'confidence': gesture.score,
                'handedness': hand_label
            })
        
        return results

    def release(self):
        if self.gesture_recognizer:
            self.gesture_recognizer.close()
