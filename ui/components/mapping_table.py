"""
Mapping Table Widget
Right panel component for editing motion-to-key mappings.
"""

import logging
import yaml
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QInputDialog, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from ..styles.common import COLORS
from .key_selector_dialog import KeySelectorDialog

logger = logging.getLogger(__name__)


class MappingTable(QWidget):
    """
    Motion mappings table with Add/Remove buttons.
    Auto-saves on changes.
    """
    
    # Signals
    mappings_changed = pyqtSignal()  # Emitted when mappings are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile_path = None
        self.profile_data = {}
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the mapping table UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Header row: "MOTION MAPPINGS" + Profile indicator
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        title = QLabel("MOTION MAPPINGS")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['RED_PRIMARY']}; background: transparent; letter-spacing: 1px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Profile indicator button (top right) - RED STATUS TAG
        self.profile_indicator = QPushButton("Profile: None")
        self.profile_indicator.setObjectName("profileIndicator")
        self.profile_indicator.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.profile_indicator.setMinimumHeight(30)
        self.profile_indicator.setEnabled(False)
        header_layout.addWidget(self.profile_indicator)
        
        layout.addLayout(header_layout)
        
        # FIXED: Motion mappings table - 3 columns with centered red arrow →
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Motion Name", "", "Key/Action"])
        self.table.setFont(QFont("Arial", 11))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.cellDoubleClicked.connect(self._edit_mapping)
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        
        # FIXED: Column sizing - Name (stretch) | Arrow (60px fixed) | Key/Action (stretch)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnWidth(1, 60)  # Fixed 60px for arrow column
        
        # Row height
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table, 1)
        
        # Add/Remove buttons below table
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        add_btn = QPushButton("＋ Add Motion Mapping")
        add_btn.setMinimumHeight(45)
        add_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        add_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['GRAY_DARK']}; color: {COLORS['WHITE']}; border: 2px solid {COLORS['RED_PRIMARY']}; border-radius: 5px; }} QPushButton:hover {{ background-color: {COLORS['RED_DARK']}; border: 2px solid {COLORS['RED_BRIGHT']}; }}")
        add_btn.clicked.connect(self._add_mapping)
        btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("－ Remove Selected")
        remove_btn.setMinimumHeight(45)
        remove_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        remove_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['GRAY_DARK']}; color: {COLORS['WHITE']}; border: 2px solid {COLORS['RED_DARK']}; border-radius: 5px; }} QPushButton:hover {{ background-color: {COLORS['RED_DARK']}; border: 2px solid {COLORS['RED_BRIGHT']}; }}")
        remove_btn.clicked.connect(self._remove_mapping)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
    
    def load_profile(self, profile_path: Path):
        """Load profile data and populate table."""
        self.profile_path = profile_path
        
        try:
            with open(profile_path, 'r') as f:
                self.profile_data = yaml.safe_load(f) or {}
            
            # FINAL CHANGE: Update profile indicator - now shows 'Active:' for instant feedback
            display_name = self._format_clean_name(profile_path.stem)
            self.profile_indicator.setText(f"Active: {display_name}")
            
            self._populate_table()
            
            logger.info(f"Loaded profile: {profile_path.name}")
        
        except Exception as e:
            logger.error(f"Failed to load profile {profile_path.name}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load profile:\n{e}")
    
    def clear_profile(self):
        """Clear the current profile."""
        self.profile_path = None
        self.profile_data = {}
        self.profile_indicator.setText("Active: None")
        self.table.setRowCount(0)
    
    def _format_clean_name(self, stem: str) -> str:
        """Convert filename stem to clean display name.
        Examples: 'default' → 'Default', 'fighting_game' → 'Fighting Game'
        """
        return stem.replace('_', ' ').title()
    
    def _populate_table(self):
        """FIXED: Populate the table with 3 columns including centered red arrow →."""
        self.table.setRowCount(0)
        
        mappings = self.profile_data.get('mappings', {})
        
        for row, (motion, action) in enumerate(mappings.items()):
            self.table.insertRow(row)
            
            # Column 0: Motion Name (white, left-aligned, read-only)
            motion_item = QTableWidgetItem(motion)
            motion_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            motion_item.setFont(QFont("Arial", 11))
            motion_item.setForeground(QColor(COLORS['WHITE']))
            motion_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row, 0, motion_item)
            
            # FIXED: Column 1: Centered red arrow → (NOT editable, NOT selectable)
            arrow_item = QTableWidgetItem("→")
            arrow_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            arrow_item.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            arrow_item.setForeground(QColor("#ff1a1a"))  # Red arrow
            arrow_item.setFlags(Qt.ItemFlag.ItemIsEnabled)  # Not selectable
            self.table.setItem(row, 1, arrow_item)
            
            # Column 2: Key/Action (clean display, center-aligned, editable)
            action_display = str(action).upper() if action else "None"
            action_item = QTableWidgetItem(action_display)
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            action_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            action_item.setForeground(QColor(COLORS['RED_BRIGHT']))
            action_item.setData(Qt.ItemDataRole.UserRole, action)  # Store raw action for editing
            self.table.setItem(row, 2, action_item)
    
    def _edit_mapping(self, row: int, column: int):
        """FIXED: Edit mapping cell (double-click handler) - works on column 2 (Key/Action)."""
        if column != 2:  # Only column 2 (Key/Action) is editable
            return
        
        # Get current action
        current_item = self.table.item(row, 2)
        current_action = current_item.data(Qt.ItemDataRole.UserRole) or ""
        
        # Open key selector dialog
        dialog = KeySelectorDialog(self, current_action)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_action = dialog.get_action()
            
            # Update display and data
            action_display = str(new_action).upper() if new_action else "None"
            current_item.setText(action_display)
            current_item.setData(Qt.ItemDataRole.UserRole, new_action)
            
            # Auto-save
            self._save_profile()
    
    def highlight_row(self, motion_name: str):
        """FIXED: Flash entire row bright red (#ff3333) for 800ms when gesture triggers.
        Public method for main app integration.
        """
        from PyQt6.QtCore import QTimer
        
        # Find row by motion name
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == motion_name:
                # Store original backgrounds
                original_bg_0 = item.background()
                original_bg_1 = self.table.item(row, 1).background()
                original_bg_2 = self.table.item(row, 2).background()
                
                # Flash bright red (#ff3333) - all columns
                flash_color = QColor("#ff3333")
                item.setBackground(flash_color)
                self.table.item(row, 1).setBackground(flash_color)
                self.table.item(row, 2).setBackground(flash_color)
                
                # Restore after 800ms
                QTimer.singleShot(800, lambda: self._restore_row_colors(row, original_bg_0, original_bg_1, original_bg_2))
                break
    
    def _restore_row_colors(self, row: int, bg_0, bg_1, bg_2):
        """Restore original row colors after flash."""
        if row < self.table.rowCount():
            self.table.item(row, 0).setBackground(bg_0)
            self.table.item(row, 1).setBackground(bg_1)
            self.table.item(row, 2).setBackground(bg_2)
    
    def _add_mapping(self):
        """Add a new mapping row."""
        if not self.profile_path:
            QMessageBox.warning(self, "Warning", "No profile loaded!")
            return
        
        motion_name, ok = QInputDialog.getText(
            self, "New Mapping",
            "Enter motion name:"
        )
        
        if not ok or not motion_name:
            return
        
        motion_name = motion_name.strip()
        if not motion_name:
            return
        
        # Open key selector
        dialog = KeySelectorDialog(self, "")
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        action = dialog.get_action()
        
        # FIXED: Add to table (3 columns with red arrow)
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Column 0: Motion Name
        motion_item = QTableWidgetItem(motion_name)
        motion_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        motion_item.setFont(QFont("Arial", 11))
        motion_item.setForeground(QColor(COLORS['WHITE']))
        motion_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, 0, motion_item)
        
        # Column 1: Centered red arrow →
        arrow_item = QTableWidgetItem("→")
        arrow_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_item.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        arrow_item.setForeground(QColor("#ff1a1a"))
        arrow_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.table.setItem(row, 1, arrow_item)
        
        # Column 2: Key/Action
        action_display = str(action).upper() if action else "None"
        action_item = QTableWidgetItem(action_display)
        action_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        action_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        action_item.setForeground(QColor(COLORS['RED_BRIGHT']))
        action_item.setData(Qt.ItemDataRole.UserRole, action)
        self.table.setItem(row, 2, action_item)
        
        # Auto-save
        self._save_profile()
        
        logger.info(f"Added mapping: {motion_name} → {action}")
    
    def _remove_mapping(self):
        """Remove selected mapping row."""
        if not self.profile_path:
            QMessageBox.warning(self, "Warning", "No profile loaded!")
            return
        
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "No mapping selected!")
            return
        
        motion_name = self.table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Remove Mapping",
            f"Remove mapping for '{motion_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(current_row)
            
            # Auto-save
            self._save_profile()
            
            logger.info(f"Removed mapping: {motion_name}")
    
    def _save_profile(self):
        """FIXED: Auto-save current profile to .yaml file (3-column table)."""
        if not self.profile_path:
            return
        
        # Collect mappings from table (3 columns - action is in column 2)
        mappings = {}
        for row in range(self.table.rowCount()):
            motion = self.table.item(row, 0).text()
            action_item = self.table.item(row, 2)  # Column 2 has the action
            action = action_item.data(Qt.ItemDataRole.UserRole) or ""
            
            if action:
                mappings[motion] = action
        
        # Update profile data
        self.profile_data['mappings'] = mappings
        
        # Save to file
        try:
            with open(self.profile_path, 'w') as f:
                yaml.safe_dump(self.profile_data, f, default_flow_style=False, sort_keys=False)
            
            self.mappings_changed.emit()
            logger.info(f"Auto-saved profile: {self.profile_path.name}")
        
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save profile:\n{e}")
