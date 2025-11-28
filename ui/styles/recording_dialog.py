"""
Recording Dialog Styles
All styles for the Recording Dialog.
"""

from .common import COLORS

# Recording Dialog Complete Stylesheet
RECORDING_DIALOG_STYLESHEET = f"""
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
    
    QProgressBar {{
        background-color: {COLORS['GRAY_DARK']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 8px;
        text-align: center;
        color: {COLORS['WHITE']};
        font-weight: bold;
    }}
    
    QProgressBar::chunk {{
        background-color: {COLORS['RED_PRIMARY']};
        border-radius: 6px;
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
