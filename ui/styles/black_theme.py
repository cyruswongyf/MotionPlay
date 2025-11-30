"""
MotionPlay v3.0 — Black Theme System
Centralized styles that GUARANTEE black backgrounds everywhere.
No more white button battles.
"""

from .common import COLORS

# ============================================================================
# COMMON WIDGET STYLES — Apply to ALL dialogs automatically
# ============================================================================

COMMON_BUTTON_STYLE = f"""
QPushButton {{
    background-color: #1a1a1a;
    color: white;
    border: 2px solid {COLORS['RED_DARK']};
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS['RED_PRIMARY']};
    color: black;
    border: 2px solid {COLORS['RED_BRIGHT']};
}}
QPushButton:pressed {{
    background-color: #cc0000;
    color: white;
}}
QPushButton:disabled {{
    background-color: {COLORS['GRAY_DARK']};
    color: {COLORS['GRAY_LIGHT']};
    border: 2px solid {COLORS['GRAY']};
}}
"""

COMMON_LINEEDIT_STYLE = f"""
QLineEdit {{
    background-color: #1a1a1a;
    color: white;
    border: 2px solid {COLORS['RED_DARK']};
    padding: 6px 10px;
    border-radius: 4px;
    selection-background-color: {COLORS['RED_PRIMARY']};
    selection-color: white;
}}
QLineEdit:focus {{
    border: 2px solid {COLORS['RED_BRIGHT']};
    background-color: #222222;
}}
QLineEdit:disabled {{
    background-color: {COLORS['GRAY_DARK']};
    color: {COLORS['GRAY_LIGHT']};
    border: 2px solid {COLORS['GRAY']};
}}
"""

COMMON_TEXTEDIT_STYLE = f"""
QTextEdit {{
    background-color: #1a1a1a;
    color: white;
    border: 2px solid {COLORS['RED_DARK']};
    padding: 8px;
    border-radius: 4px;
    selection-background-color: {COLORS['RED_PRIMARY']};
    selection-color: white;
}}
QTextEdit:focus {{
    border: 2px solid {COLORS['RED_BRIGHT']};
    background-color: #222222;
}}
"""

COMMON_LABEL_STYLE = f"""
QLabel {{
    color: white;
    background-color: transparent;
}}
"""

COMMON_COMBOBOX_STYLE = f"""
QComboBox {{
    background-color: #1a1a1a;
    color: white;
    border: 2px solid {COLORS['RED_DARK']};
    padding: 6px 10px;
    border-radius: 4px;
}}
QComboBox:hover {{
    border: 2px solid {COLORS['RED_BRIGHT']};
}}
QComboBox::drop-down {{
    border: none;
    background-color: {COLORS['RED_DARK']};
}}
QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid white;
    margin-right: 5px;
}}
QComboBox QAbstractItemView {{
    background-color: #1a1a1a;
    color: white;
    border: 2px solid {COLORS['RED_BRIGHT']};
    selection-background-color: {COLORS['RED_PRIMARY']};
    selection-color: white;
}}
"""

COMMON_CHECKBOX_STYLE = f"""
QCheckBox {{
    color: white;
    background-color: transparent;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {COLORS['RED_DARK']};
    border-radius: 3px;
    background-color: #1a1a1a;
}}
QCheckBox::indicator:hover {{
    border: 2px solid {COLORS['RED_BRIGHT']};
}}
QCheckBox::indicator:checked {{
    background-color: {COLORS['RED_PRIMARY']};
    border: 2px solid {COLORS['RED_BRIGHT']};
}}
"""

COMMON_SCROLLBAR_STYLE = f"""
QScrollBar:vertical {{
    background-color: {COLORS['GRAY_DARK']};
    width: 12px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical {{
    background-color: {COLORS['RED_DARK']};
    border-radius: 6px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['RED_PRIMARY']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background-color: {COLORS['GRAY_DARK']};
    height: 12px;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal {{
    background-color: {COLORS['RED_DARK']};
    border-radius: 6px;
    min-width: 20px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['RED_PRIMARY']};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""

# ============================================================================
# COMBINED UNIVERSAL STYLESHEET
# ============================================================================

UNIVERSAL_BLACK_STYLESHEET = f"""
{COMMON_BUTTON_STYLE}
{COMMON_LINEEDIT_STYLE}
{COMMON_TEXTEDIT_STYLE}
{COMMON_LABEL_STYLE}
{COMMON_COMBOBOX_STYLE}
{COMMON_CHECKBOX_STYLE}
{COMMON_SCROLLBAR_STYLE}
"""

# ============================================================================
# SPECIALIZED BUTTON STYLES (for specific use cases)
# ============================================================================

PRIMARY_ACTION_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['RED_PRIMARY']};
    color: white;
    border: 3px solid {COLORS['RED_BRIGHT']};
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS['RED_BRIGHT']};
    color: black;
}}
QPushButton:pressed {{
    background-color: #cc0000;
}}
"""

DANGER_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['RED_DARK']};
    color: white;
    border: 3px solid {COLORS['RED_PRIMARY']};
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS['RED_PRIMARY']};
    border: 3px solid {COLORS['RED_BRIGHT']};
}}
"""

SECONDARY_BUTTON_STYLE = f"""
QPushButton {{
    background-color: {COLORS['GRAY']};
    color: white;
    border: 2px solid {COLORS['GRAY_LIGHT']};
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {COLORS['GRAY_LIGHT']};
}}
"""

# ============================================================================
# INPUT DIALOG STYLE
# ============================================================================

INPUT_DIALOG_STYLESHEET = f"""
QDialog {{
    background-color: #0d0d0d;
    color: white;
}}
QLabel {{
    color: white;
    background-color: transparent;
    font-size: 13px;
}}
{COMMON_LINEEDIT_STYLE}
{COMMON_TEXTEDIT_STYLE}
{COMMON_BUTTON_STYLE}
"""
