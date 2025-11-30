"""
Mapping Table Styles
All styles for the mapping table component.
"""

from .common import COLORS

# Mapping Table Complete Stylesheet
MAPPING_TABLE_STYLESHEET = f"""
    QTableWidget {{
        background-color: {COLORS['BG_BLACK']};
        color: {COLORS['WHITE']};
        gridline-color: {COLORS['RED_DARK']};
        border: 2px solid {COLORS['RED_DARK']};
        border-radius: 5px;
        selection-background-color: {COLORS['RED_DARK']};
        selection-color: {COLORS['WHITE']};
    }}
    
    QTableWidget::item {{
        padding: 8px;
    }}
    
    QTableWidget::item:alternate {{
        background-color: {COLORS['GRAY_DARK']};
    }}
    
    QHeaderView::section {{
        background-color: {COLORS['GRAY_DARK']};
        color: {COLORS['RED_BRIGHT']};
        padding: 10px;
        border: 1px solid {COLORS['RED_DARK']};
        font-weight: bold;
    }}
"""
