"""
MotionPlay UI Styles Package
Clean separation of styles from code - each component has its own style file.
"""

from .common import COLORS
from .main_window import MAIN_WINDOW_STYLESHEET
from .recording_dialog import RECORDING_DIALOG_STYLESHEET
from .profile_manager import PROFILE_MANAGER_STYLESHEET

# Legacy compatibility functions
def get_stylesheet() -> str:
    """Get main window stylesheet."""
    return MAIN_WINDOW_STYLESHEET

def get_dialog_stylesheet() -> str:
    """Get dialog stylesheet."""
    return RECORDING_DIALOG_STYLESHEET

__all__ = [
    'COLORS',
    'MAIN_WINDOW_STYLESHEET',
    'RECORDING_DIALOG_STYLESHEET', 
    'PROFILE_MANAGER_STYLESHEET',
    'get_stylesheet',
    'get_dialog_stylesheet'
]
