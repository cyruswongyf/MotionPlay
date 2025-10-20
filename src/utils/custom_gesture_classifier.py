"""
Custom Gesture Classifier
Uses trained sklearn model for gesture recognition
"""

import joblib
import numpy as np
from utils.hand_landmarker import HandLandmarker


class CustomGestureClassifier:
    def __init__(self, model_path='custom_gesture_recognizer/gesture_classifier.pkl', 
                 hand_landmarker_path='models/hand_landmarker.task', num_hands=2):
        """
        Initialize custom gesture classifier
        
        Args:
            model_path: sklearn model file path
            hand_landmarker_path: MediaPipe hand landmarker model path
            num_hands: number of hands to detect
        """
        self.model = joblib.load(model_path)
        self.hand_landmarker = HandLandmarker(hand_landmarker_path, num_hands)
        self.gesture_results = []
        
        print(f"Loaded custom gesture classifier: {model_path}")
        print(f"Supported gesture classes: {self.model.classes_}")
    
    def detect_async(self, frame, timestamp_ms):
        """Detect hand landmarks (asynchronous)"""
        self.hand_landmarker.detect_async(frame, timestamp_ms)
    
    def predict_gestures(self):
        """
        Predict gestures based on detected hand landmarks
        
        Returns:
            list: Prediction results for each hand [{'gesture': '1', 'confidence': 0.95, 'handedness': 'Left'}, ...]
        """
        hand_result = self.hand_landmarker.get_landmark_data()
        
        if not hand_result or not hand_result.hand_landmarks:
            self.gesture_results = []
            return []
        
        results = []
        hand_landmarks_list = hand_result.hand_landmarks
        handedness_list = hand_result.handedness or []
        
        for idx, hand_landmarks in enumerate(hand_landmarks_list):
            # Extract features (63 values: 21 points * 3 coordinates)
            features = []
            for lm in hand_landmarks:
                features.extend([lm.x, lm.y, lm.z])
            features = np.array(features).reshape(1, -1)
            
            # Predict gesture
            gesture = self.model.predict(features)[0]
            confidence = np.max(self.model.predict_proba(features))
            
            # Get handedness (Left/Right)
            hand_label = None
            if idx < len(handedness_list):
                handedness_categories = handedness_list[idx]
                if isinstance(handedness_categories, list) and len(handedness_categories) > 0:
                    category = handedness_categories[0]
                    if hasattr(category, 'category_name'):
                        hand_label = category.category_name
            
            results.append({
                'gesture': gesture,
                'confidence': float(confidence),
                'handedness': hand_label
            })
        
        self.gesture_results = results
        return results
    
    def draw_on_frame(self, frame, color_left=(0, 255, 0), color_right=(0, 128, 255)):
        """
        Draw hand landmarks and gesture labels on frame
        
        Args:
            frame: Input frame
            color_left: Left hand color (B, G, R)
            color_right: Right hand color (B, G, R)
            
        Returns:
            Annotated frame
        """
        import cv2
        
        # First draw hand landmarks
        annotated = self.hand_landmarker.draw_landmarks_on_frame(frame, color_left, color_right)
        
        # Get hand data
        hand_result = self.hand_landmarker.get_landmark_data()
        if not hand_result or not hand_result.hand_landmarks:
            return annotated
        
        hand_landmarks_list = hand_result.hand_landmarks
        
        # Draw gesture labels
        for idx, gesture_info in enumerate(self.gesture_results):
            if idx >= len(hand_landmarks_list):
                break
            
            hand_landmarks = hand_landmarks_list[idx]
            wrist = hand_landmarks[0]
            h, w, _ = annotated.shape
            cx, cy = int(wrist.x * w), int(wrist.y * h)
            
            # Choose color
            handedness = gesture_info.get('handedness', 'Unknown')
            color = color_left if handedness == 'Left' else color_right
            
            # Display gesture and confidence
            gesture = gesture_info['gesture']
            confidence = gesture_info['confidence']
            text = f"{gesture} ({confidence:.2f})"
            
            # Draw text (with shadow effect)
            cv2.putText(annotated, text, (cx + 12, cy - 12),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 3)
            cv2.putText(annotated, text, (cx + 10, cy - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        return annotated
    
    def get_gestures(self):
        """Get latest gesture recognition results"""
        return self.gesture_results
    
    def release(self):
        """Release resources"""
        self.hand_landmarker.release()
