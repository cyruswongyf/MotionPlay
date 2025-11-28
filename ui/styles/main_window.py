"""
Main Window Styles
All styles for the main MotionPlay window.
"""

from .common import COLORS

# Main Window Complete Stylesheet
MAIN_WINDOW_STYLESHEET = f"""
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
