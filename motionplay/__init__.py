"""
MotionPlay - Air Gesture Recognition for Gaming
"""

__version__ = "3.1.0"
__author__ = "MotionPlay Team"

# Core functionality (no UI dependencies)
from .core import (
    Camera,
    MediaPipeProcessor,
    MotionRecognizer,
    ActionMapper,
    MotionRecorder
)
from .models import ensure_models_exist

__all__ = [
    'Camera',
    'MediaPipeProcessor',
    'MotionRecognizer',
    'ActionMapper',
    'MotionRecorder',
    'ensure_models_exist',
]
