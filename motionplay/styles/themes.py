"""
MotionPlay Theme Manager
Unified theme application for the entire application.
"""

import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from .colors import BLACK, WHITE, RED, RED_PRIMARY, GRAY


def apply_dark_theme(app: QApplication) -> None:
    """Apply the unified dark theme to the entire application."""
    # Block system theme interference
    os.environ["QT_QPA_PLATFORMTHEME"] = ""
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app.setStyle('Fusion')
    
    palette = QPalette()
    black = QColor(BLACK)
    white = QColor(WHITE)
    red = QColor(RED)
    
    # Force ALL background roles to nuclear black
    for role in [
        QPalette.ColorRole.Window,
        QPalette.ColorRole.Base,
        QPalette.ColorRole.AlternateBase,
        QPalette.ColorRole.Button,
        QPalette.ColorRole.Light,
        QPalette.ColorRole.Midlight,
        QPalette.ColorRole.Dark,
        QPalette.ColorRole.Shadow,
        QPalette.ColorRole.ToolTipBase
    ]:
        palette.setColor(role, black)
    
    # Force ALL text roles to white
    for role in [
        QPalette.ColorRole.Text,
        QPalette.ColorRole.WindowText,
        QPalette.ColorRole.ButtonText,
        QPalette.ColorRole.HighlightedText,
        QPalette.ColorRole.ToolTipText,
        QPalette.ColorRole.BrightText
    ]:
        palette.setColor(role, white)
    
    # Red highlights
    for role in [QPalette.ColorRole.Highlight, QPalette.ColorRole.Link]:
        palette.setColor(role, red)
    
    app.setPalette(palette)
    
    # Global stylesheet - the final kill
    app.setStyleSheet(f"""
        QMainWindow, QDialog, QWidget {{ 
            background-color: {BLACK}; 
            color: {WHITE}; 
        }}
        QLabel, QLineEdit, QComboBox, QTextEdit {{ 
            color: {WHITE}; 
            background-color: #111111; 
        }}
        QToolTip {{ 
            background-color: {BLACK}; 
            color: {WHITE}; 
            border: 1px solid {RED}; 
        }}
        QSplitter {{
            background-color: {BLACK};
        }}
        QSplitter::handle {{
            background: #1a1a1a;
        }}
    """)
