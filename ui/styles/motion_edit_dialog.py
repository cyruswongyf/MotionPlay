"""
Motion Edit Dialog Styles
All styles for the Motion Edit dialog.
"""

from .common import COLORS

# Motion Edit Dialog Complete Stylesheet
MOTION_EDIT_DIALOG_STYLESHEET = f"""
    QDialog {{
        background-color: {COLORS['PURE_BLACK']};
    }}
    
    QLineEdit, QTextEdit {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 5px;
        padding: 8px;
    }}
    QLineEdit:focus, QTextEdit:focus {{
        border: 2px solid {COLORS['RED_BRIGHT']};
    }}
"""

# Standard button style for edit dialog buttons
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['RED_DARK']};
        border: 2px solid {COLORS['RED_BRIGHT']};
    }}
    QPushButton:disabled {{
        background-color: {COLORS['GRAY']};
        color: {COLORS['GRAY_LIGHT']};
        border: 2px solid {COLORS['GRAY']};
    }}
"""

# Tag chip style
TAG_CHIP_STYLESHEET = f"""
    QFrame#tagChip {{
        background-color: {COLORS['RED_PRIMARY']};
        border: 1px solid {COLORS['RED_BRIGHT']};
        border-radius: 16px;
    }}
"""

# Tag chip remove button style
TAG_CHIP_REMOVE_BTN_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['RED_DARK']};
        color: {COLORS['WHITE']};
        border: none;
        border-radius: 10px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['RED_BRIGHT']};
    }}
"""

# Delete button style
DELETE_BTN_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['RED_DARK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_PRIMARY']};
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['RED_PRIMARY']};
        border: 2px solid {COLORS['RED_BRIGHT']};
    }}
"""

# Cancel button style
CANCEL_BTN_STYLE = f"""
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

# Save button style
SAVE_BTN_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['RED_PRIMARY']};
        color: {COLORS['WHITE']};
        border: 3px solid {COLORS['RED_BRIGHT']};
        border-radius: 5px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['RED_BRIGHT']};
    }}
"""

# Preview display style
PREVIEW_DISPLAY_STYLE = f"""
    background-color: {COLORS['GRAY_DARK']};
    border: 2px solid {COLORS['RED_DARK']};
    border-radius: 8px;
"""

# Value display style (for edit fields)
VALUE_DISPLAY_STYLE = f"""
    color: {COLORS['WHITE']};
    background-color: {COLORS['GRAY_DARK']};
    border: 2px solid {COLORS['RED_DARK']};
    border-radius: 5px;
    padding: 8px;
"""

VALUE_DISPLAY_MULTILINE_STYLE = f"""
    color: {COLORS['WHITE']};
    background-color: {COLORS['GRAY_DARK']};
    border: 2px solid {COLORS['RED_DARK']};
    border-radius: 5px;
    padding: 12px;
"""

# Tags container style
TAGS_CONTAINER_STYLE = f"""
    background-color: {COLORS['GRAY_DARK']};
    border: 2px solid {COLORS['RED_DARK']};
    border-radius: 5px;
"""
