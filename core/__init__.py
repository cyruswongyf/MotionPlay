"""
MotionPlay Core Package
Pure logic for camera, MediaPipe processing, motion recognition, and action mapping.
No UI dependencies.
"""

from .camera import Camera
from .mediapipe_processor import MediaPipeProcessor
from .motion_recognizer import MotionRecognizer
from .action_mapper import ActionMapper
from .motion_recorder import MotionRecorder

__all__ = [
    'Camera',
    'MediaPipeProcessor',
    'MotionRecognizer',
    'ActionMapper',
    'MotionRecorder',
]
