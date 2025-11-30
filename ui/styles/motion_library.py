"""
Motion Library Dialog Styles
All styles for the Motion Library dialog.
"""

from .common import COLORS

# Motion Library Complete Stylesheet
MOTION_LIBRARY_STYLESHEET = f"""
    QDialog {{
        background-color: {COLORS['PURE_BLACK']};
    }}
    
    QLineEdit {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 8px;
        padding: 10px 15px;
    }}
    QLineEdit:focus {{
        border: 3px solid {COLORS['RED_BRIGHT']};
    }}
    
    QScrollArea {{
        background-color: {COLORS['PURE_BLACK']};
        border: none;
    }}
    
    QScrollBar:vertical {{
        background-color: {COLORS['GRAY_DARK']};
        width: 12px;
        border-radius: 6px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {COLORS['RED_DARK']};
        border-radius: 6px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {COLORS['RED_PRIMARY']};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
"""

# Motion Card Styles
MOTION_CARD_STYLE = f"""
    QFrame#motionCard {{
        background-color: {COLORS['BG_BLACK']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 8px;
    }}
    QFrame#motionCard:hover {{
        background-color: {COLORS['GRAY_DARK']};
        border: 3px solid {COLORS['RED_BRIGHT']};
    }}
"""

MOTION_CARD_HOVER_STYLE = f"""
    QFrame#motionCard {{
        background-color: {COLORS['GRAY_DARK']};
        border: 3px solid {COLORS['RED_BRIGHT']};
    }}
"""

# Close button style
CLOSE_BTN_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['GRAY']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['GRAY_LIGHT']};
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['GRAY_LIGHT']};
    }}
"""

# Floating add button style
FLOATING_ADD_BTN_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['RED_PRIMARY']};
        color: {COLORS['WHITE']};
        border: 4px solid {COLORS['RED_BRIGHT']};
        border-radius: 35px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['RED_BRIGHT']};
        border: 4px solid {COLORS['WHITE']};
    }}
"""

# Tag filter checkbox style
TAG_CHECKBOX_STYLE = f"""
    QCheckBox {{
        color: {COLORS['WHITE']};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 3px;
        background-color: {COLORS['GRAY_DARK']};
    }}
    QCheckBox::indicator:checked {{
        background-color: {COLORS['RED_PRIMARY']};
        border: 2px solid {COLORS['RED_BRIGHT']};
    }}
"""

# Clear filters button style
CLEAR_FILTERS_BTN_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['RED_DARK']};
    }}
"""
