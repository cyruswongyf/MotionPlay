"""
MotionPlay Motion Mapping Group System
Full-featured profile manager with motion → key mapping editor.
Matches TARGET design: professional gaming peripheral software aesthetic.
"""

import yaml
import logging
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QTableWidget, QTableWidgetItem, QWidget,
    QInputDialog, QMessageBox, QFileDialog, QHeaderView,
    QAbstractItemView, QSplitter, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from .styles import COLORS

logger = logging.getLogger(__name__)


class KeySelectorDialog(QDialog):
    """
    Popup dialog for selecting keyboard keys or mouse actions.
    Minimal design matching TARGET screenshot aesthetic.
    """
    
    def __init__(self, parent=None, current_value: str = ""):
        super().__init__(parent)
        self.selected_action = current_value
        self.setWindowTitle("Select Key/Action")
        self.setFixedSize(450, 350)
        self.setModal(True)
        
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        """Initialize key selector UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("SELECT KEY OR ACTION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Current selection display
        self.current_label = QLabel(f"Selected: {self._format_action(self.selected_action)}")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_label.setFont(QFont("Arial", 13))
        layout.addWidget(self.current_label)
        
        # Instructions
        instruction = QLabel("Press any key or click an option below")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setFont(QFont("Arial", 10))
        instruction.setStyleSheet(f"color: {COLORS['GRAY_LIGHT']};")
        layout.addWidget(instruction)
        
        # Mouse actions
        mouse_group = QLabel("MOUSE ACTIONS")
        mouse_group.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        mouse_group.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; margin-top: 10px;")
        layout.addWidget(mouse_group)
        
        mouse_layout = QHBoxLayout()
        mouse_layout.setSpacing(8)
        
        mouse_left = QPushButton("Left Click")
        mouse_left.setMinimumHeight(45)
        mouse_left.clicked.connect(lambda: self._set_action("left_click"))
        mouse_layout.addWidget(mouse_left)
        
        mouse_right = QPushButton("Right Click")
        mouse_right.setMinimumHeight(45)
        mouse_right.clicked.connect(lambda: self._set_action("right_click"))
        mouse_layout.addWidget(mouse_right)
        
        mouse_middle = QPushButton("Middle")
        mouse_middle.setMinimumHeight(45)
        mouse_middle.clicked.connect(lambda: self._set_action("middle_click"))
        mouse_layout.addWidget(mouse_middle)
        
        layout.addLayout(mouse_layout)
        
        # Scroll actions
        scroll_layout = QHBoxLayout()
        scroll_layout.setSpacing(8)
        
        scroll_up = QPushButton("Scroll ↑")
        scroll_up.setMinimumHeight(45)
        scroll_up.clicked.connect(lambda: self._set_action("scroll_up"))
        scroll_layout.addWidget(scroll_up)
        
        scroll_down = QPushButton("Scroll ↓")
        scroll_down.setMinimumHeight(45)
        scroll_down.clicked.connect(lambda: self._set_action("scroll_down"))
        scroll_layout.addWidget(scroll_down)
        
        none_btn = QPushButton("None")
        none_btn.setMinimumHeight(45)
        none_btn.clicked.connect(lambda: self._set_action(""))
        scroll_layout.addWidget(none_btn)
        
        layout.addLayout(scroll_layout)
        
        layout.addStretch()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumHeight(40)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_BRIGHT']};
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
            }}
        """)
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def _set_action(self, action: str):
        """Set the selected action."""
        self.selected_action = action
        self.current_label.setText(f"Selected: {self._format_action(action)}")
    
    def _format_action(self, action: str) -> str:
        """Format action for display."""
        if not action:
            return "None"
        return action.upper()
    
    def keyPressEvent(self, event):
        """Capture keyboard key presses."""
        key = event.key()
        
        # Ignore Escape (used for cancel)
        if key == Qt.Key.Key_Escape:
            self.reject()
            return
        
        # Map Qt keys to readable format
        key_map = {
            Qt.Key.Key_Space: "space",
            Qt.Key.Key_Return: "enter",
            Qt.Key.Key_Enter: "enter",
            Qt.Key.Key_Backspace: "backspace",
            Qt.Key.Key_Tab: "tab",
            Qt.Key.Key_Shift: "shift",
            Qt.Key.Key_Control: "ctrl",
            Qt.Key.Key_Alt: "alt",
            Qt.Key.Key_CapsLock: "capslock",
            Qt.Key.Key_Up: "up",
            Qt.Key.Key_Down: "down",
            Qt.Key.Key_Left: "left",
            Qt.Key.Key_Right: "right",
        }
        
        if key in key_map:
            key_name = key_map[key]
        else:
            key_text = event.text()
            if key_text and key_text.isprintable():
                key_name = key_text.lower()
            else:
                return
        
        self._set_action(key_name)
    
    def _apply_styles(self):
        """Apply TARGET screenshot styling."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['BG_BLACK']};
            }}
            
            QLabel {{
                color: {COLORS['WHITE']};
                background-color: transparent;
            }}
            
            QPushButton {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['RED_DARK']};
                border: 2px solid {COLORS['RED_BRIGHT']};
            }}
            
            QPushButton:pressed {{
                background-color: {COLORS['PURE_BLACK']};
            }}
        """)
    
    def get_action(self) -> str:
        """Get the selected action."""
        return self.selected_action


class ProfileManagerDialog(QDialog):
    """
    Motion Mapping Group System - TARGET screenshot design.
    Left: Profile list with action buttons
    Right: MOTION MAPPINGS table editor
    Bottom: Close / SET AS ACTIVE buttons
    """
    
    profile_changed = pyqtSignal(str)  # Emits profile name (without .yaml)
    
    def __init__(self, parent=None, config: dict = None):
        super().__init__(parent)
        
        self.config = config or {}
        self.profile_dir = Path(config.get('profiles', {}).get('profile_dir', 'profiles'))
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_profile_name = None  # Filename with .yaml
        self.current_profile_data = {}
        
        self.setWindowTitle("Motion Mapping Group System")
        self.setMinimumSize(1400, 750)
        self.setModal(True)
        
        self._init_ui()
        self._apply_styles()
        self._load_profiles()
        
        # Auto-refresh timer for external file changes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._check_external_changes)
        self.refresh_timer.start(2000)
        
        logger.info("Motion Mapping Group System opened")
    
    def _init_ui(self):
        """Initialize UI matching TARGET screenshot."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Horizontal splitter for left/right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(3)
        
        # ==================== LEFT PANEL ====================
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(8)
        
        # "PROFILES" title
        profiles_title = QLabel("PROFILES")
        profiles_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        profiles_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profiles_title.setStyleSheet(f"""
            color: {COLORS['RED_PRIMARY']};
            background: transparent;
            padding: 5px;
            letter-spacing: 1px;
        """)
        left_layout.addWidget(profiles_title)
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setFont(QFont("Arial", 11))
        self.profile_list.currentItemChanged.connect(self._on_profile_selected)
        left_layout.addWidget(self.profile_list, 1)
        
        # Action buttons (vertical stack)
        btn_style = """
            QPushButton {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #ff1a1a;
                border-radius: 4px;
                font-weight: bold;
                font-size: 10pt;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #ff1a1a;
                border: 2px solid #ff3333;
            }
            QPushButton:pressed {
                background-color: #cc0000;
            }
        """
        
        new_btn = QPushButton("New")
        new_btn.setMinimumHeight(40)
        new_btn.setStyleSheet(btn_style)
        new_btn.clicked.connect(self._create_profile)
        left_layout.addWidget(new_btn)
        
        duplicate_btn = QPushButton("Duplicate")
        duplicate_btn.setMinimumHeight(40)
        duplicate_btn.setStyleSheet(btn_style)
        duplicate_btn.clicked.connect(self._duplicate_profile)
        left_layout.addWidget(duplicate_btn)
        
        rename_btn = QPushButton("Rename")
        rename_btn.setMinimumHeight(40)
        rename_btn.setStyleSheet(btn_style)
        rename_btn.clicked.connect(self._rename_profile)
        left_layout.addWidget(rename_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setMinimumHeight(40)
        delete_btn.setStyleSheet(btn_style)
        delete_btn.clicked.connect(self._delete_profile)
        left_layout.addWidget(delete_btn)
        
        import_btn = QPushButton("Import...")
        import_btn.setMinimumHeight(40)
        import_btn.setStyleSheet(btn_style)
        import_btn.clicked.connect(self._import_profile)
        left_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export...")
        export_btn.setMinimumHeight(40)
        export_btn.setStyleSheet(btn_style)
        export_btn.clicked.connect(self._export_profile)
        left_layout.addWidget(export_btn)
        
        splitter.addWidget(left_panel)
        
        # ==================== RIGHT PANEL ====================
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(8)
        
        # Header row: "MOTION MAPPINGS" + Profile name button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        mappings_title = QLabel("MOTION MAPPINGS")
        mappings_title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        mappings_title.setStyleSheet(f"""
            color: {COLORS['RED_PRIMARY']};
            background: transparent;
            letter-spacing: 1px;
        """)
        header_layout.addWidget(mappings_title)
        
        header_layout.addStretch()
        
        # Profile indicator button (top right)
        self.profile_indicator = QPushButton("Profile: None")
        self.profile_indicator.setFont(QFont("Arial", 10))
        self.profile_indicator.setMinimumHeight(30)
        self.profile_indicator.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }}
        """)
        self.profile_indicator.setEnabled(False)
        header_layout.addWidget(self.profile_indicator)
        
        right_layout.addLayout(header_layout)
        
        # Motion mappings table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(3)
        self.mapping_table.setHorizontalHeaderLabels(["Motion Name", "→", "Key/Action → Preview"])
        self.mapping_table.setFont(QFont("Arial", 11))
        self.mapping_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mapping_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.mapping_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.mapping_table.cellDoubleClicked.connect(self._edit_mapping)
        self.mapping_table.setShowGrid(True)
        self.mapping_table.setAlternatingRowColors(True)
        
        # Column sizing
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.mapping_table.setColumnWidth(0, 300)
        self.mapping_table.setColumnWidth(1, 50)
        
        # Row height
        self.mapping_table.verticalHeader().setDefaultSectionSize(40)
        self.mapping_table.verticalHeader().setVisible(False)
        
        right_layout.addWidget(self.mapping_table, 1)
        
        # Add/Remove buttons below table
        table_btn_layout = QHBoxLayout()
        table_btn_layout.setSpacing(10)
        
        add_btn = QPushButton("＋ Add Motion Mapping")
        add_btn.setMinimumHeight(45)
        add_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_PRIMARY']};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_DARK']};
                border: 2px solid {COLORS['RED_BRIGHT']};
            }}
        """)
        add_btn.clicked.connect(self._add_mapping_row)
        table_btn_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("－ Remove Selected")
        remove_btn.setMinimumHeight(45)
        remove_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        remove_btn.setStyleSheet(f"""
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
        """)
        remove_btn.clicked.connect(self._remove_mapping_row)
        table_btn_layout.addWidget(remove_btn)
        
        right_layout.addLayout(table_btn_layout)
        
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setStretchFactor(0, 30)
        splitter.setStretchFactor(1, 70)
        
        main_layout.addWidget(splitter, 1)
        
        # ==================== BOTTOM BAR ====================
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)
        
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(50)
        close_btn.setMinimumWidth(120)
        close_btn.setFont(QFont("Arial", 11))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['GRAY']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['GRAY_LIGHT']};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['GRAY_LIGHT']};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(close_btn)
        
        bottom_layout.addStretch()
        
        # Big red "SET AS ACTIVE" button
        self.activate_btn = QPushButton("SET AS ACTIVE")
        self.activate_btn.setMinimumHeight(50)
        self.activate_btn.setMinimumWidth(200)
        self.activate_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.activate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 3px solid {COLORS['RED_BRIGHT']};
                border-radius: 6px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
                border: 3px solid #ff6666;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['RED_DARK']};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['GRAY']};
                border: 3px solid {COLORS['GRAY_DARK']};
            }}
        """)
        self.activate_btn.setEnabled(False)
        self.activate_btn.clicked.connect(self._set_as_active)
        bottom_layout.addWidget(self.activate_btn)
        
        main_layout.addLayout(bottom_layout)
    
    def _apply_styles(self):
        """Apply TARGET screenshot styling."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['BG_BLACK']};
            }}
            
            QWidget {{
                background-color: transparent;
            }}
            
            QWidget#leftPanel, QWidget#rightPanel {{
                background-color: #0a0a0a;
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 8px;
            }}
            
            QLabel {{
                color: {COLORS['WHITE']};
                background-color: transparent;
            }}
            
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
            
            QTableWidget::item:selected {{
                background-color: {COLORS['RED_DARK']};
                color: {COLORS['WHITE']};
            }}
            
            QTableWidget::item:alternate {{
                background-color: #0a0a0a;
            }}
            
            QHeaderView::section {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['RED_BRIGHT']};
                padding: 12px 8px;
                border: none;
                border-right: 1px solid {COLORS['RED_DARK']};
                border-bottom: 2px solid {COLORS['RED_DARK']};
                font-weight: bold;
                font-size: 11pt;
            }}
            
            QSplitter::handle {{
                background-color: {COLORS['RED_DARK']};
            }}
        """)
    
    def _load_profiles(self):
        """Load all .yaml profiles from profiles/ directory."""
        self.profile_list.clear()
        
        if not self.profile_dir.exists():
            self.profile_dir.mkdir(parents=True, exist_ok=True)
            return
        
        profile_files = sorted(self.profile_dir.glob("*.yaml"))
        for path in profile_files:
            self.profile_list.addItem(path.name)
        
        if self.profile_list.count() > 0:
            self.profile_list.setCurrentRow(0)
    
    def _on_profile_selected(self, current, previous):
        """Handle profile selection change - instantly load mappings."""
        if not current:
            self.current_profile_name = None
            self.current_profile_data = {}
            self.profile_indicator.setText("Profile: None")
            self.mapping_table.setRowCount(0)
            self.activate_btn.setEnabled(False)
            return
        
        # Load new profile (auto-save behavior)
        self.current_profile_name = current.text()
        self._load_profile_data()
        self.activate_btn.setEnabled(True)
    
    def _load_profile_data(self):
        """Load profile data and populate mapping table."""
        if not self.current_profile_name:
            return
        
        profile_path = self.profile_dir / self.current_profile_name
        
        try:
            with open(profile_path, 'r') as f:
                self.current_profile_data = yaml.safe_load(f) or {}
            
            # Update profile indicator
            display_name = self.current_profile_name.replace('.yaml', '')
            self.profile_indicator.setText(f"Profile: {display_name}")
            
            self._populate_mapping_table()
            
            logger.info(f"Loaded profile: {self.current_profile_name}")
        
        except Exception as e:
            logger.error(f"Failed to load profile {self.current_profile_name}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load profile:\n{e}")
    
    def _populate_mapping_table(self):
        """Populate the mapping table with current profile data."""
        self.mapping_table.setRowCount(0)
        
        mappings = self.current_profile_data.get('mappings', {})
        
        for row, (motion, action) in enumerate(mappings.items()):
            self.mapping_table.insertRow(row)
            
            # Column 0: Motion Name (white, read-only)
            motion_item = QTableWidgetItem(motion)
            motion_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            motion_item.setFont(QFont("Arial", 11))
            motion_item.setForeground(QColor(COLORS['WHITE']))
            motion_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.mapping_table.setItem(row, 0, motion_item)
            
            # Column 1: Arrow (red, centered)
            arrow_item = QTableWidgetItem("→")
            arrow_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            arrow_item.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            arrow_item.setForeground(QColor(COLORS['RED_PRIMARY']))
            arrow_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.mapping_table.setItem(row, 1, arrow_item)
            
            # Column 2: Key/Action + Preview
            preview = self._format_action_preview(action)
            action_item = QTableWidgetItem(preview)
            action_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            action_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            action_item.setForeground(QColor(COLORS['RED_BRIGHT']))
            action_item.setData(Qt.ItemDataRole.UserRole, action)  # Store raw action
            self.mapping_table.setItem(row, 2, action_item)
    
    def _format_action_preview(self, action) -> str:
        """Format action with preview arrow (e.g., '→ W' or '→ left_click')."""
        if not action:
            return "→ None"
        
        action_str = str(action).upper()
        return f"→ {action_str}"
    
    def _edit_mapping(self, row: int, column: int):
        """Edit mapping cell (double-click handler)."""
        if column != 2:  # Only column 2 (Key/Action) is editable
            return
        
        # Get current action (stored in UserRole)
        current_item = self.mapping_table.item(row, 2)
        current_action = current_item.data(Qt.ItemDataRole.UserRole) or ""
        
        # Open key selector dialog
        dialog = KeySelectorDialog(self, current_action)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_action = dialog.get_action()
            
            # Update display and data
            preview = self._format_action_preview(new_action)
            current_item.setText(preview)
            current_item.setData(Qt.ItemDataRole.UserRole, new_action)
            
            # Auto-save
            self._save_profile()
    
    def _add_mapping_row(self):
        """Add a new mapping row."""
        if not self.current_profile_name:
            QMessageBox.warning(self, "Warning", "No profile selected!")
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
        
        # Add to table
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        
        # Column 0: Motion Name
        motion_item = QTableWidgetItem(motion_name)
        motion_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        motion_item.setFont(QFont("Arial", 11))
        motion_item.setForeground(QColor(COLORS['WHITE']))
        motion_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.mapping_table.setItem(row, 0, motion_item)
        
        # Column 1: Arrow
        arrow_item = QTableWidgetItem("→")
        arrow_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_item.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        arrow_item.setForeground(QColor(COLORS['RED_PRIMARY']))
        arrow_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.mapping_table.setItem(row, 1, arrow_item)
        
        # Column 2: Key/Action
        preview = self._format_action_preview(action)
        action_item = QTableWidgetItem(preview)
        action_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        action_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        action_item.setForeground(QColor(COLORS['RED_BRIGHT']))
        action_item.setData(Qt.ItemDataRole.UserRole, action)
        self.mapping_table.setItem(row, 2, action_item)
        
        # Auto-save
        self._save_profile()
        
        logger.info(f"Added mapping: {motion_name} → {action}")
    
    def _remove_mapping_row(self):
        """Remove selected mapping row."""
        if not self.current_profile_name:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        current_row = self.mapping_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "No mapping selected!")
            return
        
        motion_name = self.mapping_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "Remove Mapping",
            f"Remove mapping for '{motion_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.mapping_table.removeRow(current_row)
            
            # Auto-save
            self._save_profile()
            
            logger.info(f"Removed mapping: {motion_name}")
    
    def _save_profile(self):
        """Auto-save current profile to .yaml file."""
        if not self.current_profile_name:
            return
        
        # Collect mappings from table
        mappings = {}
        for row in range(self.mapping_table.rowCount()):
            motion = self.mapping_table.item(row, 0).text()
            action_item = self.mapping_table.item(row, 2)
            action = action_item.data(Qt.ItemDataRole.UserRole) or ""
            
            if action:
                mappings[motion] = action
        
        # Update profile data
        self.current_profile_data['mappings'] = mappings
        
        # Save to file
        profile_path = self.profile_dir / self.current_profile_name
        
        try:
            with open(profile_path, 'w') as f:
                yaml.safe_dump(self.current_profile_data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Auto-saved profile: {self.current_profile_name}")
            
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save profile:\n{e}")
    
    def _create_profile(self):
        """Create a new profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if not ok or not name:
            return
        
        name = name.strip()
        if not name.endswith('.yaml'):
            name += '.yaml'
        
        profile_path = self.profile_dir / name
        
        if profile_path.exists():
            QMessageBox.warning(self, "Error", f"Profile '{name}' already exists!")
            return
        
        # Create minimal profile
        data = {
            'name': name.replace('.yaml', ''),
            'mappings': {}
        }
        
        try:
            with open(profile_path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self._load_profiles()
            
            # Select the new profile
            items = self.profile_list.findItems(name, Qt.MatchFlag.MatchExactly)
            if items:
                self.profile_list.setCurrentItem(items[0])
            
            logger.info(f"Created profile: {name}")
        
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create profile:\n{e}")
    
    def _duplicate_profile(self):
        """Duplicate selected profile."""
        if not self.current_profile_name:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        base_name = self.current_profile_name.replace('.yaml', '')
        new_name, ok = QInputDialog.getText(
            self, "Duplicate Profile",
            f"Enter name for copy of '{base_name}':",
            text=f"{base_name}_copy"
        )
        
        if not ok or not new_name:
            return
        
        new_name = new_name.strip()
        if not new_name.endswith('.yaml'):
            new_name += '.yaml'
        
        src_path = self.profile_dir / self.current_profile_name
        dst_path = self.profile_dir / new_name
        
        if dst_path.exists():
            QMessageBox.warning(self, "Error", f"Profile '{new_name}' already exists!")
            return
        
        try:
            shutil.copy2(src_path, dst_path)
            
            # Update name in the copied file
            with open(dst_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            data['name'] = new_name.replace('.yaml', '')
            
            with open(dst_path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self._load_profiles()
            logger.info(f"Duplicated profile: {self.current_profile_name} → {new_name}")
        
        except Exception as e:
            logger.error(f"Failed to duplicate profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to duplicate profile:\n{e}")
    
    def _rename_profile(self):
        """Rename selected profile."""
        if not self.current_profile_name:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        base_name = self.current_profile_name.replace('.yaml', '')
        new_name, ok = QInputDialog.getText(
            self, "Rename Profile",
            "Enter new profile name:",
            text=base_name
        )
        
        if not ok or not new_name:
            return
        
        new_name = new_name.strip()
        if not new_name.endswith('.yaml'):
            new_name += '.yaml'
        
        if new_name == self.current_profile_name:
            return
        
        old_path = self.profile_dir / self.current_profile_name
        new_path = self.profile_dir / new_name
        
        if new_path.exists():
            QMessageBox.warning(self, "Error", f"Profile '{new_name}' already exists!")
            return
        
        try:
            old_path.rename(new_path)
            
            # Update name in the file
            with open(new_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            data['name'] = new_name.replace('.yaml', '')
            
            with open(new_path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self._load_profiles()
            
            # Select the renamed profile
            items = self.profile_list.findItems(new_name, Qt.MatchFlag.MatchExactly)
            if items:
                self.profile_list.setCurrentItem(items[0])
            
            logger.info(f"Renamed profile: {self.current_profile_name} → {new_name}")
        
        except Exception as e:
            logger.error(f"Failed to rename profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to rename profile:\n{e}")
    
    def _delete_profile(self):
        """Delete selected profile."""
        if not self.current_profile_name:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete '{self.current_profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            profile_path = self.profile_dir / self.current_profile_name
            
            try:
                profile_path.unlink()
                logger.info(f"Deleted profile: {self.current_profile_name}")
                
                self.current_profile_name = None
                self.current_profile_data = {}
                self.unsaved_changes = False
                
                self._load_profiles()
            
            except Exception as e:
                logger.error(f"Failed to delete profile: {e}")
                QMessageBox.critical(self, "Error", f"Failed to delete profile:\n{e}")
    
    def _import_profile(self):
        """Import profile from external .yaml file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Profile",
            str(Path.home()),
            "YAML Files (*.yaml *.yml)"
        )
        
        if not file_path:
            return
        
        src_path = Path(file_path)
        dst_path = self.profile_dir / src_path.name
        
        if dst_path.exists():
            reply = QMessageBox.question(
                self, "Profile Exists",
                f"Profile '{src_path.name}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                return
        
        try:
            shutil.copy2(src_path, dst_path)
            self._load_profiles()
            
            # Select the imported profile
            items = self.profile_list.findItems(src_path.name, Qt.MatchFlag.MatchExactly)
            if items:
                self.profile_list.setCurrentItem(items[0])
            
            logger.info(f"Imported profile: {src_path.name}")
            QMessageBox.information(self, "Success", f"Profile '{src_path.name}' imported successfully!")
        
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to import profile:\n{e}")
    
    def _export_profile(self):
        """Export current profile to external location."""
        if not self.current_profile_name:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Profile",
            str(Path.home() / self.current_profile_name),
            "YAML Files (*.yaml *.yml)"
        )
        
        if not file_path:
            return
        
        src_path = self.profile_dir / self.current_profile_name
        dst_path = Path(file_path)
        
        try:
            shutil.copy2(src_path, dst_path)
            logger.info(f"Exported profile: {self.current_profile_name} → {dst_path}")
            QMessageBox.information(self, "Success", f"Profile exported to:\n{dst_path}")
        
        except Exception as e:
            logger.error(f"Failed to export profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export profile:\n{e}")
    
    def _set_as_active(self):
        """Set current profile as active in main application."""
        if not self.current_profile_name:
            return
        
        # Emit signal to activate profile (without .yaml extension)
        profile_name = self.current_profile_name.replace('.yaml', '')
        self.profile_changed.emit(profile_name)
        
        QMessageBox.information(
            self, "Profile Activated",
            f"'{profile_name}' is now the active profile!"
        )
        
        logger.info(f"Activated profile: {profile_name}")
    
    def _check_external_changes(self):
        """Check if profiles were added/removed externally and auto-refresh."""
        if not self.profile_dir.exists():
            return
        
        current_files = set(p.name for p in self.profile_dir.glob("*.yaml"))
        list_files = set(self.profile_list.item(i).text() for i in range(self.profile_list.count()))
        
        if current_files != list_files:
            # Profiles changed externally - refresh list
            current_selection = self.current_profile_name
            self._load_profiles()
            
            # Try to restore selection
            if current_selection:
                items = self.profile_list.findItems(current_selection, Qt.MatchFlag.MatchExactly)
                if items:
                    self.profile_list.setCurrentItem(items[0])
