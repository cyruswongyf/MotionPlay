"""
Profile Manager Dialog for MotionPlay
Manage motion profiles and mappings.
"""

import yaml
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QWidget, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from .styles import get_dialog_stylesheet, COLORS

logger = logging.getLogger(__name__)


class ProfileManagerDialog(QDialog):
    """
    Modal dialog for managing motion profiles.
    """
    
    profile_changed = pyqtSignal(str)
    
    def __init__(self, parent=None, config: dict = None):
        super().__init__(parent)
        
        self.config = config or {}
        self.profile_dir = Path(config.get('profiles', {}).get('profile_dir', 'profiles'))
        self.current_profile = None
        
        self.setWindowTitle("Profile Manager")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        self._init_ui()
        self.setStyleSheet(get_dialog_stylesheet())
        self._load_profiles()
        
        logger.info("Profile manager opened")
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("COMBAT PROFILES")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['RED_PRIMARY']};")
        layout.addWidget(title)
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setFont(QFont("Arial", 14))
        self.profile_list.currentItemChanged.connect(self._on_profile_selected)
        layout.addWidget(self.profile_list, 1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        new_btn = QPushButton("New")
        new_btn.setFont(QFont("Arial", 12))
        new_btn.setMinimumHeight(45)
        new_btn.clicked.connect(self._create_profile)
        button_layout.addWidget(new_btn)
        
        duplicate_btn = QPushButton("Duplicate")
        duplicate_btn.setFont(QFont("Arial", 12))
        duplicate_btn.setMinimumHeight(45)
        duplicate_btn.clicked.connect(self._duplicate_profile)
        button_layout.addWidget(duplicate_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setFont(QFont("Arial", 12))
        delete_btn.setMinimumHeight(45)
        delete_btn.clicked.connect(self._delete_profile)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        # Bottom buttons
        bottom_layout = QHBoxLayout()
        
        close_btn = QPushButton("Close")
        close_btn.setFont(QFont("Arial", 12))
        close_btn.setMinimumHeight(50)
        close_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(close_btn)
        
        bottom_layout.addStretch()
        
        self.activate_btn = QPushButton("SET AS ACTIVE")
        self.activate_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.activate_btn.setMinimumHeight(55)
        self.activate_btn.setMinimumWidth(200)
        self.activate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 3px solid {COLORS['RED_BRIGHT']};
                border-radius: 10px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
            }}
        """)
        self.activate_btn.setEnabled(False)
        self.activate_btn.clicked.connect(self._activate_profile)
        bottom_layout.addWidget(self.activate_btn)
        
        layout.addLayout(bottom_layout)
    
    def _load_profiles(self):
        """Load available profiles."""
        self.profile_list.clear()
        
        if not self.profile_dir.exists():
            return
        
        for path in sorted(self.profile_dir.glob("*.yaml")):
            self.profile_list.addItem(path.stem)
        
        if self.profile_list.count() > 0:
            self.profile_list.setCurrentRow(0)
    
    def _on_profile_selected(self, current, previous):
        """Handle profile selection."""
        if current:
            self.current_profile = current.text()
            self.activate_btn.setEnabled(True)
        else:
            self.current_profile = None
            self.activate_btn.setEnabled(False)
    
    def _create_profile(self):
        """Create new profile."""
        name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
        if ok and name:
            name = name.strip()
            path = self.profile_dir / f"{name}.yaml"
            
            if path.exists():
                QMessageBox.warning(self, "Error", f"Profile '{name}' already exists!")
                return
            
            # Create minimal profile
            data = {
                'name': name,
                'mappings': {}
            }
            
            with open(path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self._load_profiles()
            logger.info(f"Profile created: {name}")
    
    def _duplicate_profile(self):
        """Duplicate selected profile."""
        if not self.current_profile:
            QMessageBox.warning(self, "Error", "No profile selected!")
            return
        
        name, ok = QInputDialog.getText(
            self, "Duplicate Profile",
            f"Enter name for copy of '{self.current_profile}':",
            text=f"{self.current_profile}_copy"
        )
        
        if ok and name:
            name = name.strip()
            src = self.profile_dir / f"{self.current_profile}.yaml"
            dst = self.profile_dir / f"{name}.yaml"
            
            if dst.exists():
                QMessageBox.warning(self, "Error", f"Profile '{name}' already exists!")
                return
            
            # Copy profile
            with open(src, 'r') as f:
                data = yaml.safe_load(f)
            
            data['name'] = name
            
            with open(dst, 'w') as f:
                yaml.safe_dump(data, f)
            
            self._load_profiles()
            logger.info(f"Profile duplicated: {self.current_profile} → {name}")
    
    def _delete_profile(self):
        """Delete selected profile."""
        if not self.current_profile:
            QMessageBox.warning(self, "Error", "No profile selected!")
            return
        
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete '{self.current_profile}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            path = self.profile_dir / f"{self.current_profile}.yaml"
            path.unlink()
            self._load_profiles()
            logger.info(f"Profile deleted: {self.current_profile}")
    
    def _activate_profile(self):
        """Activate selected profile."""
        if self.current_profile:
            self.profile_changed.emit(self.current_profile)
            QMessageBox.information(
                self, "Success",
                f"Profile '{self.current_profile}' is now active!"
            )
            logger.info(f"Profile activated: {self.current_profile}")
