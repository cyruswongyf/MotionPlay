"""
MotionPlay UI Styles Package
Clean separation of styles from code - each component has its own style file.
"""

from .common import COLORS
from .main_window import MAIN_WINDOW_STYLESHEET
from .recording_dialog import RECORDING_DIALOG_STYLESHEET
from .profile_manager import PROFILE_MANAGER_STYLESHEET
from .black_theme import (
    UNIVERSAL_BLACK_STYLESHEET,
    COMMON_BUTTON_STYLE,
    PRIMARY_ACTION_BUTTON_STYLE,
    DANGER_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE
)

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
    'UNIVERSAL_BLACK_STYLESHEET',
    'COMMON_BUTTON_STYLE',
    'PRIMARY_ACTION_BUTTON_STYLE',
    'DANGER_BUTTON_STYLE',
    'SECONDARY_BUTTON_STYLE',
    'get_stylesheet',
    'get_dialog_stylesheet'
]
