"""
Complete Stylesheets for MotionPlay UI Components
Consolidated from old ui/styles/ directory.
"""

from .colors import (
    BLACK, WHITE, RED, RED_PRIMARY, RED_BRIGHT, RED_DARK, 
    RED_GLOW, RED_LIGHT, GRAY, GRAY_DARK, GRAY_DARKEST, PURE_BLACK
)

# Main Window Complete Stylesheet
MAIN_WINDOW_STYLESHEET = f"""
    /* Main Window */
    QMainWindow {{
        background-color: {BLACK};
    }}
    
    QWidget#central {{
        background-color: {BLACK};
    }}
    
    QWidget#cameraContainer {{
        background-color: {PURE_BLACK};
        border-right: 3px solid {RED_DARK};
    }}
    
    QLabel#cameraLabel {{
        background-color: {PURE_BLACK};
        border: none;
    }}
    
    QWidget#controlPanel {{
        background-color: {BLACK};
    }}
    
    /* Labels */
    QLabel#title {{
        color: {RED_PRIMARY};
        background-color: transparent;
        padding: 10px;
        font-family: "Segoe UI", "Arial";
    }}
    
    QLabel#sectionLabel {{
        color: {WHITE};
        background-color: transparent;
        font-weight: bold;
    }}
    
    QLabel#motion_name {{
        color: {RED_PRIMARY};
        background-color: transparent;
        border: 2px solid {RED_DARK};
        border-radius: 8px;
        padding: 20px;
        font-size: 52pt;
        font-weight: bold;
    }}
    
    QLabel#triggerLabel {{
        color: {WHITE};
        background-color: transparent;
    }}
    
    QLabel#key_action {{
        color: {RED_LIGHT};
        background-color: transparent;
        font-size: 40pt;
    }}
    
    QLabel#statusBar {{
        background-color: {PURE_BLACK};
        color: {RED_LIGHT};
        padding: 8px;
        font-family: "Segoe UI", "Arial";
    }}
    
    /* ComboBox */
    QComboBox#profileCombo {{
        background-color: {GRAY};
        color: {RED_BRIGHT};
        border: 2px solid {RED_DARK};
        border-radius: 6px;
        padding: 8px 15px;
        font-weight: bold;
    }}
    
    QComboBox#profileCombo::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 30px;
        border: none;
        background-color: {RED_DARK};
    }}
    
    QComboBox#profileCombo::down-arrow {{
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 8px solid {RED_BRIGHT};
    }}
    
    QComboBox#profileCombo:hover {{
        border: 2px solid {RED_BRIGHT};
    }}
    
    QComboBox#profileCombo QAbstractItemView {{
        background-color: {GRAY};
        color: {WHITE};
        selection-background-color: {RED_DARK};
        selection-color: {WHITE};
        border: 2px solid {RED_DARK};
        outline: none;
    }}
    
    /* Buttons */
    QPushButton#recordButton {{
        background-color: {RED_PRIMARY};
        color: {WHITE};
        border: 2px solid {RED_PRIMARY};
        border-radius: 8px;
        font-weight: bold;
        letter-spacing: 1px;
        padding: 14px;
    }}
    
    QPushButton#recordButton:hover {{
        background-color: {RED_BRIGHT};
        border: 2px solid {RED_BRIGHT};
    }}
    
    QPushButton#recordButton:pressed {{
        background-color: {RED_DARK};
    }}
    
    QPushButton#actionButton {{
        background-color: {GRAY};
        color: {WHITE};
        border: 2px solid {RED_DARK};
        border-radius: 8px;
        font-weight: bold;
        padding: 14px;
    }}
    
    QPushButton#actionButton:hover {{
        background-color: {RED_DARK};
        color: {WHITE};
        border: 2px solid {RED_BRIGHT};
    }}
    
    QPushButton#actionButton:pressed {{
        background-color: {PURE_BLACK};
    }}
    
    QPushButton#exitButton {{
        background-color: {GRAY};
        color: {WHITE};
        border: 2px solid {RED_DARK};
        border-radius: 8px;
        padding: 14px;
    }}
    
    QPushButton#exitButton:hover {{
        background-color: {RED_DARK};
        color: {WHITE};
    }}
"""
