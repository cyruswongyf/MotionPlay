"""
MotionPlay - Professional Air Gesture Recognition for Gaming
A clean, maintainable, open-source ready application.
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

# UI and styles are imported lazily to avoid PyQt6 import issues
# Use: from motionplay.ui import MotionPlayMainWindow
# Use: from motionplay.styles import apply_dark_theme

__all__ = [
    'Camera',
    'MediaPipeProcessor',
    'MotionRecognizer',
    'ActionMapper',
    'MotionRecorder',
    'ensure_models_exist',
]
