"""
Base UI Classes for MotionPlay
Provides themed base classes for windows and dialogs.
"""

from PyQt6.QtWidgets import QMainWindow
from .dark_dialogs import BlackWindow


class BlackMainWindow(QMainWindow, BlackWindow):
    """
    Nuclear black main window base class.
    Main application window MUST inherit from this.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        BlackWindow.__init__(self)
