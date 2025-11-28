"""
MediaPipe Processor for MotionPlay
Handles hand and pose landmark detection and normalization.
Pure logic - no UI dependencies.
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from . import model_manager

logger = logging.getLogger(__name__)


@dataclass
class HandLandmarks:
    """Hand landmarks data with normalized coordinates."""
    landmarks: List[tuple]  # List of (x, y, z) normalized coordinates
    handedness: str  # "Left" or "Right"
    score: float  # Confidence score


@dataclass
class PoseLandmarks:
    """Pose landmarks data with normalized coordinates."""
    landmarks: List[tuple]  # List of (x, y, z, visibility) normalized coordinates
    score: float  # Confidence score


class MediaPipeProcessor:
    """
    MediaPipe processing for hands and pose detection.
    Normalizes landmarks and provides clean interfaces.
    
    Attributes:
        num_hands: Maximum number of hands to detect
        min_detection_confidence: Minimum detection confidence (0.0-1.0)
        min_tracking_confidence: Minimum tracking confidence (0.0-1.0)
        enable_pose: Whether to enable pose detection
    """
    
    def __init__(
        self,
        hand_model_path: str = 'models/hand_landmarker.task',
        pose_model_path: str = 'models/pose_landmarker.task',
        gesture_model_path: str = 'models/gesture_recognizer.task',
        num_hands: int = 2,
        enable_pose: bool = False,
        enable_gestures: bool = True,
        offline_mode: bool = False,
        prefer_custom_gesture: bool = True
    ):
        """
        Initialize MediaPipe processors.
        
        Args:
            hand_model_path: Path to hand landmarker model
            pose_model_path: Path to pose landmarker model
            gesture_model_path: Path to gesture recognizer model
            num_hands: Maximum number of hands to detect
            enable_pose: Whether to enable pose detection
            enable_gestures: Whether to enable gesture recognition
            offline_mode: Skip auto-download checks (for air-gapped systems)
            prefer_custom_gesture: Auto-detect and use custom gesture model if available
        """
        # Ensure models are downloaded before initialization
        try:
            model_manager.ensure_models_exist(offline_mode=offline_mode)
        except RuntimeError as e:
            logger.error(f"Model initialization failed: {e}")
            raise
        
        # Auto-detect custom gesture recognizer
        if prefer_custom_gesture:
            custom_gesture_path = 'models/custom_gesture_recognizer.task'
            if Path(custom_gesture_path).exists():
                logger.info(f"Custom gesture recognizer detected: {custom_gesture_path}")
                gesture_model_path = custom_gesture_path
            else:
                logger.info("Using official gesture recognizer (no custom model found)")
        
        self.num_hands = num_hands
        self.enable_pose = enable_pose
        self.enable_gestures = enable_gestures
        self.gesture_model_path = gesture_model_path
        
        # Results storage
        self.hand_results: Optional[Any] = None
        self.pose_results: Optional[Any] = None
        self.gesture_results: Optional[Any] = None
        
        # Initialize processors
        self._init_hand_landmarker(hand_model_path)
        
        if enable_pose:
            self._init_pose_landmarker(pose_model_path)
        
        if enable_gestures:
            self._init_gesture_recognizer(gesture_model_path)
        
        logger.info("All MediaPipe models ready")
        logger.info(f"MediaPipeProcessor initialized (hands={num_hands}, pose={enable_pose}, gestures={enable_gestures})")
    
    def _init_hand_landmarker(self, model_path: str) -> None:
        """Initialize hand landmarker."""
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.LIVE_STREAM,
                num_hands=self.num_hands,
                result_callback=self._hand_callback,
            )
            self.hand_landmarker = vision.HandLandmarker.create_from_options(options)
            logger.info(f"Hand landmarker loaded: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize hand landmarker: {e}")
            raise
    
    def _init_pose_landmarker(self, model_path: str) -> None:
        """Initialize pose landmarker."""
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.PoseLandmarkerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.LIVE_STREAM,
                result_callback=self._pose_callback,
            )
            self.pose_landmarker = vision.PoseLandmarker.create_from_options(options)
            logger.info(f"Pose landmarker loaded: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize pose landmarker: {e}")
            raise
    
    def _init_gesture_recognizer(self, model_path: str) -> None:
        """Initialize gesture recognizer."""
        try:
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            base_options = python.BaseOptions(model_asset_path=model_path)
            options = vision.GestureRecognizerOptions(
                base_options=base_options,
                running_mode=vision.RunningMode.LIVE_STREAM,
                num_hands=self.num_hands,
                result_callback=self._gesture_callback,
            )
            self.gesture_recognizer = vision.GestureRecognizer.create_from_options(options)
            logger.info(f"Gesture recognizer loaded: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize gesture recognizer: {e}")
            raise
    
    def _hand_callback(self, result, image, timestamp):
        """Callback for hand landmarker."""
        self.hand_results = result
    
    def _pose_callback(self, result, image, timestamp):
        """Callback for pose landmarker."""
        self.pose_results = result
    
    def _gesture_callback(self, result, image, timestamp):
        """Callback for gesture recognizer."""
        self.gesture_results = result
    
    def process_frame(self, frame: np.ndarray, timestamp_ms: int) -> None:
        """
        Process a frame with MediaPipe.
        
        Args:
            frame: BGR frame from camera
            timestamp_ms: Timestamp in milliseconds
        """
        if frame is None:
            return
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Process with hand landmarker
        self.hand_landmarker.detect_async(mp_image, timestamp_ms)
        
        # Process with pose landmarker if enabled
        if self.enable_pose and hasattr(self, 'pose_landmarker'):
            self.pose_landmarker.detect_async(mp_image, timestamp_ms)
        
        # Process with gesture recognizer if enabled
        if self.enable_gestures and hasattr(self, 'gesture_recognizer'):
            self.gesture_recognizer.recognize_async(mp_image, timestamp_ms)
    
    def get_hand_landmarks(self) -> List[HandLandmarks]:
        """
        Get detected hand landmarks.
        
        Returns:
            List of HandLandmarks objects
        """
        if not self.hand_results or not self.hand_results.hand_landmarks:
            return []
        
        results = []
        handedness_list = self.hand_results.handedness or []
        
        for idx, hand_landmarks in enumerate(self.hand_results.hand_landmarks):
            # Extract landmarks
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks]
            
            # Get handedness
            handedness = "Unknown"
            score = 0.0
            if idx < len(handedness_list):
                hand_category = handedness_list[idx][0]
                handedness = hand_category.category_name
                score = hand_category.score
            
            results.append(HandLandmarks(
                landmarks=landmarks,
                handedness=handedness,
                score=score
            ))
        
        return results
    
    def get_gestures(self) -> List[Dict[str, Any]]:
        """
        Get recognized gestures.
        
        Returns:
            List of dicts with keys: gesture, confidence, handedness
        """
        if not self.gesture_results or not self.gesture_results.gestures:
            return []
        
        results = []
        gestures = self.gesture_results.gestures or []
        handedness_list = self.gesture_results.handedness or []
        
        for idx, gesture_list in enumerate(gestures):
            if not gesture_list:
                continue
            
            gesture = gesture_list[0]
            
            # Get handedness
            hand_label = "Unknown"
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
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw hand landmarks on frame.
        
        Args:
            frame: BGR frame to draw on
            
        Returns:
            Annotated frame
        """
        if frame is None:
            return frame
        
        annotated = frame.copy()
        
        # Draw hand landmarks
        if self.hand_results and self.hand_results.hand_landmarks:
            for hand_landmarks in self.hand_results.hand_landmarks:
                # Draw landmarks
                for landmark in hand_landmarks:
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(annotated, (x, y), 3, (0, 255, 0), -1)
        
        return annotated
    
    def release(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, 'hand_landmarker'):
            self.hand_landmarker.close()
        
        if hasattr(self, 'pose_landmarker'):
            self.pose_landmarker.close()
        
        if hasattr(self, 'gesture_recognizer'):
            self.gesture_recognizer.close()
        
        logger.info("MediaPipe processors released")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
