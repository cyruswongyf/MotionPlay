"""
MotionPlay Styles Package
Centralized styling for the entire application.
"""

# Export colors directly (no PyQt6 dependency)
from .colors import *

# Lazy imports for UI-dependent modules to avoid PyQt6 import issues
# Use: from motionplay.styles.themes import apply_dark_theme
# Use: from motionplay.styles.stylesheets import MAIN_WINDOW_STYLESHEET

__all__ = ['COLORS', 'BLACK', 'WHITE', 'RED']
