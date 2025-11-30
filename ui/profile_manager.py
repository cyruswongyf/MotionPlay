"""
MotionPlay Motion Mapping Group System
Clean, modular profile manager using reusable components.
Professional gaming peripheral software aesthetic.
"""

import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton,
    QSplitter, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from .base import BlackDialog
from .components import ProfileListWidget, MappingTable
from .styles.common import COLORS
from .styles.profile_manager import PROFILE_MANAGER_STYLESHEET

logger = logging.getLogger(__name__)


class ProfileManagerDialog(BlackDialog):
    """
    Clean profile manager dialog.
    Orchestrates ProfileListWidget and MappingTable components.
    """
    
    profile_changed = pyqtSignal(str)  # Emits profile name (without .yaml)
    
    def __init__(self, parent=None, config: dict = None):
        super().__init__(parent)
        
        self.config = config or {}
        self.profile_dir = Path(config.get('profiles', {}).get('profile_dir', 'profiles'))
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        self.setWindowTitle("Motion Mapping Group System")
        self.setMinimumSize(1400, 750)
        self.setModal(True)
        
        # Apply profile manager styles BEFORE building UI
        self._apply_styles()
        self._init_ui()
        
        # Auto-refresh timer for external file changes
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self._check_external_changes)
        self.refresh_timer.start(2000)
        
        logger.info("Motion Mapping Group System opened")
    
    def _init_ui(self):
        """Initialize UI with component-based architecture."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # NUCLEAR FIX: Force entire dialog and splitter to pure black
        self.setObjectName("ProfileManagerDialog")
        
        # FIXED: Horizontal splitter with BLACK background - no white gaps
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(12)  # 12px clean gap between panels
        splitter.setStyleSheet(f"""
            QSplitter {{ 
                background-color: #0d0d0d; 
            }}
            QSplitter::handle {{ 
                background: #1a1a1a; 
            }}
        """)
        
        # Left panel: Profile list widget
        left_panel = self._create_panel()
        self.profile_list_widget = ProfileListWidget(self.profile_dir)
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.addWidget(self.profile_list_widget)
        splitter.addWidget(left_panel)
        
        # Right panel: Mapping table widget
        right_panel = self._create_panel()
        self.mapping_table = MappingTable()
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.addWidget(self.mapping_table)
        splitter.addWidget(right_panel)
        
        # Set splitter proportions (30% left, 70% right)
        splitter.setStretchFactor(0, 30)
        splitter.setStretchFactor(1, 70)
        
        main_layout.addWidget(splitter, 1)
        
        # FINAL CHANGE: Bottom bar with only Close button - profile selection is now INSTANT
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)
        
        bottom_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setObjectName("closeButton")
        close_btn.setMinimumHeight(50)
        close_btn.setMinimumWidth(140)
        close_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        close_btn.setStyleSheet(f"QPushButton#closeButton {{ background-color: {COLORS['GRAY']}; color: {COLORS['WHITE']}; border: 2px solid {COLORS['GRAY_LIGHT']}; border-radius: 5px; }} QPushButton#closeButton:hover {{ background-color: {COLORS['GRAY_LIGHT']}; }}")
        close_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(close_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # Connect signals
        self.profile_list_widget.profile_selected.connect(self._on_profile_selected)
        self.profile_list_widget.profiles_changed.connect(self._on_profiles_changed)
    
    def _create_panel(self) -> QWidget:
        """Create a styled panel widget."""
        panel = QWidget()
        panel.setObjectName("panel")
        panel.setStyleSheet(f"QWidget#panel {{ background-color: #0a0a0a; border: 2px solid {COLORS['RED_DARK']}; border-radius: 8px; }}")
        return panel
    
    def _apply_styles(self):
        """Apply red theme styling with NUCLEAR BLACK background fix."""
        # NUCLEAR FIX: Force ALL backgrounds to pure black
        nuclear_black_fix = f"""
            #ProfileManagerDialog, QDialog, QWidget {{ 
                background-color: #0d0d0d; 
            }}
            QSplitter {{ 
                background-color: #0d0d0d; 
            }}
            QSplitter::handle {{ 
                background: #1a1a1a; 
            }}
        """
        self.setStyleSheet(nuclear_black_fix + "\n" + PROFILE_MANAGER_STYLESHEET)
    
    def _on_profile_selected(self, profile_name: str):
        """FINAL CHANGE: Profile selection INSTANTLY activates profile - no button needed."""
        if not profile_name:
            self.mapping_table.clear_profile()
            return
        
        profile_path = self.profile_dir / profile_name
        self.mapping_table.load_profile(profile_path)
        
        # INSTANT ACTIVATION: Emit signal immediately when profile is selected
        profile_name_clean = profile_name.replace('.yaml', '')
        self.profile_changed.emit(profile_name_clean)
        
        logger.info(f"Profile instantly activated: {profile_name_clean}")
    
    def _on_profiles_changed(self):
        """Handle changes to profile list."""
        # Refresh handled by ProfileListWidget
        pass
    
    def showEvent(self, event):
        """FINAL CHANGE: Auto-load currently active profile when dialog opens."""
        super().showEvent(event)
        # Use QTimer to ensure UI is fully initialized before triggering selection
        QTimer.singleShot(0, self._auto_load_initial_profile)
    
    def set_active_profile(self, profile_name: str):
        """Set which profile is currently active (for auto-selection on open)."""
        self.current_active_profile = profile_name
    
    def _auto_load_initial_profile(self):
        """FINAL CHANGE: Auto-load currently active profile from main app."""
        if self.profile_list_widget.profile_list.count() == 0:
            return
        
        # Try to find and select currently active profile
        active_profile = getattr(self, 'current_active_profile', None)
        if active_profile:
            target_filename = f"{active_profile}.yaml"
            for i in range(self.profile_list_widget.profile_list.count()):
                item = self.profile_list_widget.profile_list.item(i)
                filename = item.data(Qt.ItemDataRole.UserRole)
                if filename == target_filename:
                    self.profile_list_widget.profile_list.setCurrentItem(item)
                    logger.info(f"Auto-loaded active profile: {active_profile}")
                    return
        
        # Fallback: Try to find default.yaml
        for i in range(self.profile_list_widget.profile_list.count()):
            item = self.profile_list_widget.profile_list.item(i)
            filename = item.data(Qt.ItemDataRole.UserRole)
            if filename == "default.yaml":
                self.profile_list_widget.profile_list.setCurrentItem(item)
                logger.info("Auto-loaded default.yaml as fallback")
                return
        
        # Final fallback: select first profile
        if self.profile_list_widget.profile_list.count() > 0:
            self.profile_list_widget.profile_list.setCurrentRow(0)
            logger.info("Auto-loaded first available profile")
    
    def _check_external_changes(self):
        """Check if profiles were added/removed externally and auto-refresh."""
        if not self.profile_dir.exists():
            return
        
        current_files = set(p.name for p in self.profile_dir.glob("*.yaml"))
        list_files = set()
        
        # Get files from profile list widget (check UserRole for actual filenames)
        for i in range(self.profile_list_widget.profile_list.count()):
            item = self.profile_list_widget.profile_list.item(i)
            if item:
                filename = item.data(Qt.ItemDataRole.UserRole)
                if filename:
                    list_files.add(filename)
        
        if current_files != list_files:
            # Profiles changed externally - refresh list
            self.profile_list_widget.load_profiles()
