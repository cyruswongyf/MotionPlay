"""
Key Selector Dialog
Modal dialog for selecting keyboard keys or mouse actions.
"""

import logging
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ..base import BlackDialog
from ..styles.common import COLORS
from ..styles.profile_manager import PROFILE_MANAGER_STYLESHEET

logger = logging.getLogger(__name__)


class KeySelectorDialog(BlackDialog):
    """
    Popup dialog for selecting keyboard keys or mouse actions.
    Returns action in format: "keyboard:w", "mouse:left_click", etc.
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
        
        mouse_buttons = [
            ("Left Click", "left_click"),
            ("Right Click", "right_click"),
            ("Middle", "middle_click")
        ]
        
        for label, action in mouse_buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, a=action: self._set_action(a))
            mouse_layout.addWidget(btn)
        
        layout.addLayout(mouse_layout)
        
        # Scroll actions
        scroll_layout = QHBoxLayout()
        scroll_layout.setSpacing(8)
        
        scroll_buttons = [
            ("Scroll ↑", "scroll_up"),
            ("Scroll ↓", "scroll_down"),
            ("None", "")
        ]
        
        for label, action in scroll_buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, a=action: self._set_action(a))
            scroll_layout.addWidget(btn)
        
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
        ok_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['RED_PRIMARY']}; color: {COLORS['WHITE']}; border: 2px solid {COLORS['RED_BRIGHT']}; border-radius: 5px; font-weight: bold; }} QPushButton:hover {{ background-color: {COLORS['RED_BRIGHT']}; }}")
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
        """Apply red theme styling."""
        self.setStyleSheet(PROFILE_MANAGER_STYLESHEET)
    
    def get_action(self) -> str:
        """Get the selected action."""
        return self.selected_action
