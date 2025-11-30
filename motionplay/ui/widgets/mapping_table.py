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
    QInputDialog, QMessageBox, QDialog, QStyledItemDelegate, QLineEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from ...styles.colors import COLORS
from .key_selector_dialog import KeySelectorDialog

logger = logging.getLogger(__name__)


class NoOverlapDelegate(QStyledItemDelegate):
    """
    Custom delegate to prevent text overlap when editing Name column.
    Auto-saves to YAML on Enter key press.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.table_widget = None  # Will be set by MappingTable
    
    def createEditor(self, parent, option, index):
        """Create editor with proper styling - no overlap."""
        editor = QLineEdit(parent)
        editor.setStyleSheet(f"""
            QLineEdit {{
                background-color: #333333;
                color: white;
                border: 2px solid {COLORS['RED_BRIGHT']};
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11pt;
            }}
        """)
        # Connect Enter key to commit and save
        editor.returnPressed.connect(lambda: self._commit_and_save(editor))
        return editor
    
    def setEditorData(self, editor, index):
        """Set editor data from model."""
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setText(str(value) if value else "")
    
    def setModelData(self, editor, model, index):
        """Save editor data to model."""
        model.setData(index, editor.text(), Qt.ItemDataRole.DisplayRole)
    
    def _commit_and_save(self, editor):
        """Commit editor and trigger auto-save on Enter."""
        self.commitData.emit(editor)
        self.closeEditor.emit(editor)
        # Trigger parent table's save
        if self.table_widget and hasattr(self.table_widget, '_save_profile'):
            self.table_widget._save_profile()
            logger.info("Auto-saved on Enter key")

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
        
        # v3: Motion mappings table - 3 columns (Name | Control | Motion)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Control", "Motion"])
        self.table.setFont(QFont("Arial", 11))
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)  # Enable editing
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.cellDoubleClicked.connect(self._edit_mapping)
        self.table.itemChanged.connect(self._on_item_changed)  # Track name changes
        self.table.setShowGrid(True)
        self.table.setAlternatingRowColors(True)
        
        # Apply styling
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                gridline-color: {COLORS['RED_DARK']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 5px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['RED_DARK']};
                color: {COLORS['WHITE']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['GRAY']};
                color: {COLORS['RED_BRIGHT']};
                padding: 10px;
                border: 1px solid {COLORS['RED_DARK']};
                font-weight: bold;
            }}
        """)
        
        # Set NoOverlapDelegate for Name column (column 0) - FINAL FIX with Enter auto-save
        delegate = NoOverlapDelegate(self.table)
        delegate.table_widget = self  # Set reference for auto-save
        self.table.setItemDelegateForColumn(0, delegate)
        
        # v3: Column sizing - Name | Control | Motion (all stretch)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
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
        """v3: Populate table with Name | Control | Motion format."""
        self.table.setRowCount(0)
        
        mappings = self.profile_data.get('mappings', [])
        
        # Backward compatibility: convert old dict format to v3 list
        if isinstance(mappings, dict):
            mappings = [
                {'name': name, 'control': ctrl, 'motion': name.lower()}
                for name, ctrl in mappings.items()
            ]
        
        for row, mapping in enumerate(mappings):
            self.table.insertRow(row)
            
            # Column 0: Name (editable display name)
            name = mapping.get('name', 'Unnamed')
            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setFont(QFont("Arial", 11))
            name_item.setForeground(QColor(COLORS['WHITE']))
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            
            # Column 1: Control (double-click to edit)
            control = mapping.get('control', '')
            control_display = str(control).upper() if control else "None"
            control_item = QTableWidgetItem(control_display)
            control_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            control_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            control_item.setForeground(QColor(COLORS['RED_BRIGHT']))
            control_item.setData(Qt.ItemDataRole.UserRole, control)
            control_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row, 1, control_item)
            
            # Column 2: Motion (double-click to select from library)
            motion = mapping.get('motion', '')
            motion_item = QTableWidgetItem(motion)
            motion_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            motion_item.setFont(QFont("Arial", 11))
            motion_item.setForeground(QColor(COLORS['RED_DARK']))
            motion_item.setData(Qt.ItemDataRole.UserRole, motion)
            motion_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.table.setItem(row, 2, motion_item)
    
    def _on_item_changed(self, item: QTableWidgetItem):
        """Handle item changes (for Name column inline editing)."""
        if item and item.column() == 0:  # Name column changed
            # Only save if row is complete (all 3 columns exist)
            row = item.row()
            if (self.table.item(row, 0) and 
                self.table.item(row, 1) and 
                self.table.item(row, 2)):
                self._save_profile()
                logger.info(f"Updated mapping name: {item.text()}")
    
    def _edit_mapping(self, row: int, column: int):
        """v3: Edit mapping - Column 0 (Name) is editable, Column 1 (Control) opens KeySelector, Column 2 (Motion) opens MotionLibrary."""
        if column == 0:
            # Name is directly editable via double-click (handled by EditTrigger)
            return
        elif column == 1:
            # Control: Open KeySelectorDialog
            current_item = self.table.item(row, 1)
            current_control = current_item.data(Qt.ItemDataRole.UserRole) or ""
            
            dialog = KeySelectorDialog(self, current_control)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_control = dialog.get_action()
                control_display = str(new_control).upper() if new_control else "None"
                current_item.setText(control_display)
                current_item.setData(Qt.ItemDataRole.UserRole, new_control)
                self._save_profile()
        elif column == 2:
            # Motion: Open MotionLibraryDialog
            from ..motion_library_dialog import MotionLibraryDialog
            
            dialog = MotionLibraryDialog(self)
            dialog.motion_selected.connect(lambda motion_id: self._update_motion(row, motion_id))
            dialog.exec()
    
    def highlight_row(self, motion_name: str):
        """v3: Flash entire row bright red (#ff3333) for 800ms when gesture triggers.
        Matches against motion field (column 2).
        """
        from PyQt6.QtCore import QTimer
        
        # Find row by motion name (column 2)
        for row in range(self.table.rowCount()):
            motion_item = self.table.item(row, 2)
            if motion_item and motion_item.data(Qt.ItemDataRole.UserRole) == motion_name:
                # Store original backgrounds
                original_bg_0 = self.table.item(row, 0).background()
                original_bg_1 = self.table.item(row, 1).background()
                original_bg_2 = motion_item.background()
                
                # Flash bright red (#ff3333) - all columns
                flash_color = QColor("#ff3333")
                self.table.item(row, 0).setBackground(flash_color)
                self.table.item(row, 1).setBackground(flash_color)
                motion_item.setBackground(flash_color)
                
                # Restore after 800ms
                QTimer.singleShot(800, lambda: self._restore_row_colors(row, original_bg_0, original_bg_1, original_bg_2))
                break
    
    def _restore_row_colors(self, row: int, bg_0, bg_1, bg_2):
        """Restore original row colors after flash."""
        if row < self.table.rowCount():
            self.table.item(row, 0).setBackground(bg_0)
            self.table.item(row, 1).setBackground(bg_1)
            self.table.item(row, 2).setBackground(bg_2)
    
    def _update_motion(self, row: int, motion_id: str):
        """Update motion field after selecting from library."""
        # Extract motion name from motion_id (e.g., "static/hadoken" -> "hadoken")
        motion_name = motion_id.split('/')[-1]
        
        motion_item = self.table.item(row, 2)
        motion_item.setText(motion_name)
        motion_item.setData(Qt.ItemDataRole.UserRole, motion_name)
        self._save_profile()
        
        logger.info(f"Updated motion in row {row}: {motion_name}")
    
    def _add_mapping(self):
        """v3: Add new mapping with Name, Control, and Motion."""
        if not self.profile_path:
            QMessageBox.warning(self, "Warning", "No profile loaded!")
            return
        
        # Get display name
        name, ok = QInputDialog.getText(
            self, "New Mapping",
            "Enter display name (e.g., 'Hadoken Attack'):"
        )
        
        if not ok or not name:
            return
        
        name = name.strip()
        if not name:
            return
        
        # Open key selector for control
        control_dialog = KeySelectorDialog(self, "")
        if control_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        control = control_dialog.get_action()
        
        # Open motion library for motion
        from ..motion_library_dialog import MotionLibraryDialog
        motion_dialog = MotionLibraryDialog(self)
        if motion_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        motion_id = motion_dialog.get_selected_motion_id()
        if not motion_id:
            return
        
        # Extract motion name from motion_id
        motion = motion_id.split('/')[-1] if motion_id else ''
        
        # Add to table (v3 format: Name | Control | Motion)
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Column 0: Name (editable)
        name_item = QTableWidgetItem(name)
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        name_item.setFont(QFont("Arial", 11))
        name_item.setForeground(QColor(COLORS['WHITE']))
        name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, name_item)
        
        # Column 1: Control
        control_display = str(control).upper() if control else "None"
        control_item = QTableWidgetItem(control_display)
        control_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        control_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        control_item.setForeground(QColor(COLORS['RED_BRIGHT']))
        control_item.setData(Qt.ItemDataRole.UserRole, control)
        control_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, 1, control_item)
        
        # Column 2: Motion
        motion_item = QTableWidgetItem(motion)
        motion_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        motion_item.setFont(QFont("Arial", 11))
        motion_item.setForeground(QColor(COLORS['RED_DARK']))
        motion_item.setData(Qt.ItemDataRole.UserRole, motion)
        motion_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.table.setItem(row, 2, motion_item)
        
        # Auto-save
        self._save_profile()
        
        logger.info(f"Added mapping: {name} → {control} ({motion})")
    
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
        """v3: Auto-save current profile to .yaml file in v3 format (list of {name, control, motion})."""
        if not self.profile_path:
            return
        
        # Collect mappings from table in v3 format
        mappings = []
        for row in range(self.table.rowCount()):
            # Safety check: ensure all items exist
            item_0 = self.table.item(row, 0)
            item_1 = self.table.item(row, 1)
            item_2 = self.table.item(row, 2)
            
            if not (item_0 and item_1 and item_2):
                continue  # Skip incomplete rows
            
            name = item_0.text()
            control = item_1.data(Qt.ItemDataRole.UserRole) or ""
            motion = item_2.data(Qt.ItemDataRole.UserRole) or ""
            
            if name and control and motion:
                mappings.append({
                    'name': name,
                    'control': control,
                    'motion': motion
                })
        
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
