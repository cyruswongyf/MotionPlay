"""
Profile Manager Styles
All styles for Profile Manager dialog and its components.
"""

from .common import COLORS

# Profile Manager Dialog Complete Stylesheet
PROFILE_MANAGER_STYLESHEET = f"""
    /* Dialog Base */
    QDialog {{
        background-color: {COLORS['BG_BLACK']};
    }}
    
    QWidget {{
        background-color: transparent;
    }}
    
    /* Labels */
    QLabel {{
        color: {COLORS['WHITE']};
        background-color: transparent;
    }}
    
    /* Push Buttons - Base style */
    QPushButton {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 4px;
        font-weight: bold;
        font-size: 10pt;
        padding: 8px 15px;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['RED_DARK']};
        border: 2px solid {COLORS['RED_BRIGHT']};
    }}
    
    QPushButton:pressed {{
        background-color: {COLORS['PURE_BLACK']};
    }}
    
    QPushButton:disabled {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['GRAY']};
        border: 2px solid {COLORS['GRAY_DARK']};
    }}
    
    /* Profile Indicator (top-right red status tag) */
    QPushButton#profileIndicator {{
        background-color: {COLORS['PURE_BLACK']};
        color: #ff1a1a;
        border: 2px solid #ff1a1a;
        border-radius: 4px;
        font-weight: bold;
        font-size: 10pt;
        padding: 8px 15px;
        letter-spacing: 1px;
    }}
    
    /* List Widgets */
    QListWidget {{
        background-color: {COLORS['PURE_BLACK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 6px;
        padding: 8px;
        outline: none;
    }}
    
    QListWidget::item {{
        padding: 12px 8px;
        border-radius: 4px;
        margin: 2px 0px;
    }}
    
    QListWidget::item:hover {{
        background-color: {COLORS['GRAY_DARK']};
    }}
    
    QListWidget::item:selected {{
        background-color: {COLORS['RED_DARK']};
        color: {COLORS['WHITE']};
        border: 1px solid {COLORS['RED_PRIMARY']};
    }}
    
    /* Table Widgets */
    QTableWidget {{
        background-color: {COLORS['PURE_BLACK']};
        color: {COLORS['WHITE']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 6px;
        gridline-color: #1a1a1a;
        outline: none;
    }}
    
    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid #1a1a1a;
    }}
    
    QTableWidget::item:alternate {{
        background-color: #1a1a1a;  /* Subtle alternating row color */
    }}
    
    /* FIXED: Force full row selection on ALL rows with red primary */
    QTableWidget::item:selected {{
        background-color: {COLORS['RED_PRIMARY']};
        color: {COLORS['WHITE']};
    }}
    
    QTableWidget::item {{
        selection-background-color: {COLORS['RED_PRIMARY']};
    }}
    
    /* FIXED: Clean header with NO red dividers, only subtle dark separator */
    QHeaderView::section {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['RED_BRIGHT']};
        padding: 12px 8px;
        border: none;
        border-right: 1px solid #333;
        border-bottom: 2px solid {COLORS['RED_DARK']};
        font-weight: bold;
        font-size: 11pt;
    }}
    
    /* FIXED: Splitter with transparent handle - NO red connecting line */
    QSplitter::handle {{
        background: transparent;
        width: 12px;
    }}
    
    QSplitter::handle:horizontal {{
        background: transparent;
        width: 12px;
    }}
    
    QSplitter::handle:vertical {{
        background: transparent;
        height: 12px;
    }}
"""
