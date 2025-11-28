"""
MotionPlay UI Styles
Pure Black + Aggressive Red Cyberpunk Theme
Centralized styling for the entire application.
"""

from typing import Dict

# Color Palette - Pure Black + Aggressive Red
COLORS = {
    'BG_BLACK': '#0d0d0d',
    'PURE_BLACK': '#000000',
    'RED_PRIMARY': '#ff1a1a',
    'RED_BRIGHT': '#ff3333',
    'RED_DARK': '#cc0000',
    'RED_GLOW': '#ff0000',
    'RED_LIGHT': '#ff6666',
    'WHITE': '#ffffff',
    'GRAY': '#333333',
    'GRAY_LIGHT': '#555555',
    'GRAY_DARK': '#1a1a1a',
}


def get_stylesheet() -> str:
    """
    Get the main application stylesheet.
    Pure black background with aggressive red accents.
    
    Returns:
        Complete PyQt6 stylesheet string
    """
    return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {COLORS['BG_BLACK']};
        }}
        
        QWidget#central {{
            background-color: {COLORS['BG_BLACK']};
        }}
        
        QWidget#cameraContainer {{
            background-color: {COLORS['PURE_BLACK']};
            border-right: 3px solid {COLORS['RED_DARK']};
        }}
        
        QLabel#cameraLabel {{
            background-color: {COLORS['PURE_BLACK']};
            border: none;
        }}
        
        QWidget#controlPanel {{
            background-color: {COLORS['BG_BLACK']};
        }}
        
        /* Labels */
        QLabel#title {{
            color: {COLORS['RED_PRIMARY']};
            background-color: transparent;
            padding: 10px;
            font-family: "Segoe UI", "Arial";
        }}
        
        QLabel#sectionLabel {{
            color: {COLORS['WHITE']};
            background-color: transparent;
            font-weight: bold;
        }}
        
        QLabel#motion_name {{
            color: {COLORS['RED_PRIMARY']};
            background-color: transparent;
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 8px;
            padding: 20px;
            font-size: 52pt;
            font-weight: bold;
        }}
        
        QLabel#triggerLabel {{
            color: {COLORS['WHITE']};
            background-color: transparent;
        }}
        
        QLabel#key_action {{
            color: {COLORS['RED_LIGHT']};
            background-color: transparent;
            font-size: 40pt;
        }}
        
        QLabel#statusBar {{
            background-color: {COLORS['PURE_BLACK']};
            color: {COLORS['RED_LIGHT']};
            padding: 8px;
            font-family: "Segoe UI", "Arial";
        }}
        
        /* ComboBox */
        QComboBox#profileCombo {{
            background-color: {COLORS['GRAY']};
            color: {COLORS['RED_BRIGHT']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 6px;
            padding: 8px 15px;
            font-weight: bold;
        }}
        
        QComboBox#profileCombo::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: center right;
            width: 30px;
            border: none;
            background-color: {COLORS['RED_DARK']};
        }}
        
        QComboBox#profileCombo::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid {COLORS['RED_BRIGHT']};
        }}
        
        QComboBox#profileCombo:hover {{
            border: 2px solid {COLORS['RED_BRIGHT']};
        }}
        
        QComboBox#profileCombo QAbstractItemView {{
            background-color: {COLORS['GRAY']};
            color: {COLORS['WHITE']};
            selection-background-color: {COLORS['RED_DARK']};
            selection-color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_DARK']};
            outline: none;
        }}
        
        /* Buttons */
        QPushButton#recordButton {{
            background-color: {COLORS['RED_PRIMARY']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_PRIMARY']};
            border-radius: 8px;
            font-weight: bold;
            letter-spacing: 1px;
            padding: 14px;
        }}
        
        QPushButton#recordButton:hover {{
            background-color: {COLORS['RED_BRIGHT']};
            border: 2px solid {COLORS['RED_BRIGHT']};
        }}
        
        QPushButton#recordButton:pressed {{
            background-color: {COLORS['RED_DARK']};
        }}
        
        QPushButton#actionButton {{
            background-color: {COLORS['GRAY']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 8px;
            font-weight: bold;
            padding: 14px;
        }}
        
        QPushButton#actionButton:hover {{
            background-color: {COLORS['RED_DARK']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_BRIGHT']};
        }}
        
        QPushButton#actionButton:pressed {{
            background-color: {COLORS['PURE_BLACK']};
        }}
        
        QPushButton#exitButton {{
            background-color: {COLORS['GRAY']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 8px;
            padding: 14px;
        }}
        
        QPushButton#exitButton:hover {{
            background-color: {COLORS['RED_DARK']};
            color: {COLORS['WHITE']};
        }}
    """


def get_dialog_stylesheet() -> str:
    """Get stylesheet for dialogs."""
    return f"""
        QDialog {{
            background-color: {COLORS['BG_BLACK']};
        }}
        
        QWidget#leftPanel, QWidget#rightPanel {{
            background-color: {COLORS['GRAY_DARK']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 10px;
            padding: 15px;
        }}
        
        QLabel#panelTitle {{
            color: {COLORS['RED_PRIMARY']};
            background-color: transparent;
            padding: 5px;
        }}
        
        QListWidget {{
            background-color: {COLORS['PURE_BLACK']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 8px;
            padding: 5px;
            outline: none;
        }}
        
        QListWidget::item {{
            padding: 12px 10px;
            border-radius: 5px;
            margin: 2px 0px;
        }}
        
        QListWidget::item:hover {{
            background-color: {COLORS['GRAY']};
        }}
        
        QListWidget::item:selected {{
            background-color: {COLORS['RED_DARK']};
            color: {COLORS['WHITE']};
            border: 1px solid {COLORS['RED_PRIMARY']};
        }}
        
        QLineEdit {{
            background-color: {COLORS['GRAY']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['GRAY_LIGHT']};
            border-radius: 8px;
            padding: 10px 15px;
        }}
        
        QLineEdit:focus {{
            border: 2px solid {COLORS['RED_PRIMARY']};
            background-color: {COLORS['PURE_BLACK']};
        }}
        
        QPushButton {{
            background-color: {COLORS['GRAY']};
            color: {COLORS['RED_BRIGHT']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 6px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {COLORS['RED_DARK']};
            color: {COLORS['WHITE']};
            border: 2px solid {COLORS['RED_BRIGHT']};
        }}
        
        QPushButton:pressed {{
            background-color: {COLORS['PURE_BLACK']};
        }}
    """
