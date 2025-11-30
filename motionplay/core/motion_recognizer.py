"""
Motion Recognizer for MotionPlay
Loads trained gesture models and recognizes motion patterns.
Pure logic - no UI dependencies.
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class MotionRecognizer:
    """
    Motion recognition using MediaPipe gesture recognizer or custom models.
    
    Supports:
    - MediaPipe .task models (recommended)
    - Custom trained models (DTW, ML classifiers)
    - Temporal sequence recognition for complex motions
    """
    
    def __init__(
        self,
        gesture_model_path: str = 'models/gesture_recognizer.task',
        custom_classifier_path: Optional[str] = None,
        confidence_threshold: float = 0.7,
        cooldown_ms: int = 500
    ):
        """
        Initialize motion recognizer.
        
        Args:
            gesture_model_path: Path to MediaPipe gesture model (.task)
            custom_classifier_path: Optional path to custom classifier (.pkl)
            confidence_threshold: Minimum confidence to trigger detection
            cooldown_ms: Cooldown period between detections (milliseconds)
        """
        self.confidence_threshold = confidence_threshold
        self.cooldown_ms = cooldown_ms
        
        # Last detection tracking for cooldown
        self.last_detection_time: Dict[str, int] = {}
        
        # Load custom classifier if provided
        self.custom_classifier = None
        if custom_classifier_path and Path(custom_classifier_path).exists():
            self._load_custom_classifier(custom_classifier_path)
        
        logger.info(f"MotionRecognizer initialized (threshold={confidence_threshold})")
    
    def _load_custom_classifier(self, path: str) -> None:
        """Load custom classifier from file."""
        try:
            import joblib
            self.custom_classifier = joblib.load(path)
            logger.info(f"Custom classifier loaded: {path}")
        except Exception as e:
            logger.warning(f"Failed to load custom classifier: {e}")
    
    def recognize_from_gestures(
        self,
        gestures: List[Dict[str, Any]],
        current_time_ms: int
    ) -> Optional[Dict[str, Any]]:
        """
        Recognize motion from MediaPipe gesture results.
        
        Args:
            gestures: List of gesture dicts from MediaPipeProcessor
            current_time_ms: Current timestamp in milliseconds
            
        Returns:
            Dict with keys: motion, confidence, handedness, or None if no detection
        """
        if not gestures:
            return None
        
        # Process each detected gesture
        for gesture_data in gestures:
            gesture_name = gesture_data['gesture']
            confidence = gesture_data['confidence']
            handedness = gesture_data['handedness']
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                continue
            
            # Check cooldown
            if not self._check_cooldown(gesture_name, current_time_ms):
                continue
            
            # Valid detection
            self.last_detection_time[gesture_name] = current_time_ms
            
            return {
                'motion': gesture_name,
                'confidence': confidence,
                'handedness': handedness
            }
        
        return None
    
    def recognize_from_landmarks(
        self,
        hand_landmarks: List[Any],
        current_time_ms: int
    ) -> Optional[Dict[str, Any]]:
        """
        Recognize motion from hand landmarks using custom classifier.
        
        Args:
            hand_landmarks: List of HandLandmarks from MediaPipeProcessor
            current_time_ms: Current timestamp in milliseconds
            
        Returns:
            Dict with keys: motion, confidence, handedness, or None if no detection
        """
        if not self.custom_classifier or not hand_landmarks:
            return None
        
        try:
            # Convert landmarks to feature vector
            # This would depend on your custom classifier's expected input format
            # Example: flatten all landmarks into a single vector
            features = []
            for hand in hand_landmarks:
                for landmark in hand.landmarks:
                    features.extend(landmark[:2])  # x, y only
            
            features = np.array(features).reshape(1, -1)
            
            # Predict
            prediction = self.custom_classifier.predict(features)[0]
            
            # Get confidence if available
            if hasattr(self.custom_classifier, 'predict_proba'):
                proba = self.custom_classifier.predict_proba(features)[0]
                confidence = float(np.max(proba))
            else:
                confidence = 1.0
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                return None
            
            # Check cooldown
            motion_name = str(prediction)
            if not self._check_cooldown(motion_name, current_time_ms):
                return None
            
            self.last_detection_time[motion_name] = current_time_ms
            
            return {
                'motion': motion_name,
                'confidence': confidence,
                'handedness': hand_landmarks[0].handedness if hand_landmarks else 'Unknown'
            }
            
        except Exception as e:
            logger.error(f"Error in custom recognition: {e}")
            return None
    
    def _check_cooldown(self, motion_name: str, current_time_ms: int) -> bool:
        """
        Check if cooldown period has passed for a motion.
        
        Args:
            motion_name: Name of the motion
            current_time_ms: Current timestamp in milliseconds
            
        Returns:
            True if cooldown has passed, False otherwise
        """
        if motion_name not in self.last_detection_time:
            return True
        
        elapsed = current_time_ms - self.last_detection_time[motion_name]
        return elapsed >= self.cooldown_ms
    
    def reset_cooldowns(self) -> None:
        """Reset all cooldown timers."""
        self.last_detection_time.clear()
    
    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set the confidence threshold.
        
        Args:
            threshold: New threshold (0.0-1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold}")
    
    def set_cooldown(self, cooldown_ms: int) -> None:
        """
        Set the cooldown period.
        
        Args:
            cooldown_ms: Cooldown in milliseconds
        """
        self.cooldown_ms = max(0, cooldown_ms)
        logger.info(f"Cooldown set to {self.cooldown_ms}ms")
