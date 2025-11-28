"""
Profile List Widget
Left panel component for profile management with action buttons.
"""

import logging
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QInputDialog, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ..styles.common import COLORS

logger = logging.getLogger(__name__)


class ProfileListWidget(QWidget):
    """
    Profile list with action buttons.
    Emits signals for profile operations.
    """
    
    # Signals
    profile_selected = pyqtSignal(str)  # Profile filename (with .yaml)
    profile_renamed = pyqtSignal(str, str)  # old_name, new_name
    profile_deleted = pyqtSignal(str)  # Profile filename
    profile_created = pyqtSignal(str)  # Profile filename
    profile_duplicated = pyqtSignal(str, str)  # source, destination
    profile_imported = pyqtSignal(str)  # Profile filename
    profiles_changed = pyqtSignal()  # General refresh signal
    
    def __init__(self, profile_dir: Path, parent=None):
        super().__init__(parent)
        self.profile_dir = profile_dir
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        self._init_ui()
        self.load_profiles()
    
    def _init_ui(self):
        """Initialize the profile list UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # "PROFILES" title
        title = QLabel("PROFILES")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['RED_PRIMARY']}; background: transparent; padding: 5px; letter-spacing: 1px;")
        layout.addWidget(title)
        
        # Profile list
        self.profile_list = QListWidget()
        self.profile_list.setFont(QFont("Arial", 11))
        self.profile_list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self.profile_list, 1)
        
        # Action buttons
        buttons = [
            ("New", self._create_profile),
            ("Duplicate", self._duplicate_profile),
            ("Rename", self._rename_profile),
            ("Delete", self._delete_profile),
            ("Import...", self._import_profile),
            ("Export...", self._export_profile)
        ]
        
        for label, handler in buttons:
            btn = QPushButton(label)
            btn.setMinimumHeight(40)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
    
    def load_profiles(self):
        """Load all .yaml profiles from directory with clean display names."""
        current = self.get_current_profile()
        self.profile_list.clear()
        
        if not self.profile_dir.exists():
            return
        
        profile_files = sorted(self.profile_dir.glob("*.yaml"))
        for path in profile_files:
            # Create clean display name: "default.yaml" → "Default", "fighting_game.yaml" → "Fighting Game"
            display_name = self._format_display_name(path.stem)
            item = self.profile_list.addItem(display_name)
            # Store full filename (with .yaml) in UserRole for retrieval
            self.profile_list.item(self.profile_list.count() - 1).setData(Qt.ItemDataRole.UserRole, path.name)
        
        # Restore selection
        if current and self.profile_list.count() > 0:
            for i in range(self.profile_list.count()):
                item = self.profile_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == current:
                    self.profile_list.setCurrentItem(item)
                    break
        elif self.profile_list.count() > 0:
            self.profile_list.setCurrentRow(0)
    
    def get_current_profile(self) -> str:
        """Get currently selected profile filename (with .yaml extension)."""
        item = self.profile_list.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else ""
    
    def _format_display_name(self, stem: str) -> str:
        """Convert filename stem to clean display name.
        Examples: 'default' → 'Default', 'fighting_game' → 'Fighting Game'
        """
        # Replace underscores with spaces and title case each word
        return stem.replace('_', ' ').title()
    
    def _on_selection_changed(self, current, previous):
        """Handle profile selection change."""
        if current:
            # Emit the stored filename (with .yaml) from UserRole
            filename = current.data(Qt.ItemDataRole.UserRole)
            if filename:
                self.profile_selected.emit(filename)
    
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
        
        try:
            # Create minimal profile
            import yaml
            data = {'name': name.replace('.yaml', ''), 'mappings': {}}
            with open(profile_path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self.profile_created.emit(name)
            self.profiles_changed.emit()
            self.load_profiles()
            
            # Select the new profile by finding item with matching UserRole
            for i in range(self.profile_list.count()):
                item = self.profile_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == name:
                    self.profile_list.setCurrentItem(item)
                    break
            
            logger.info(f"Created profile: {name}")
        
        except Exception as e:
            logger.error(f"Failed to create profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to create profile:\n{e}")
    
    def _duplicate_profile(self):
        """Duplicate selected profile."""
        current = self.get_current_profile()
        if not current:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        base_name = current.replace('.yaml', '')
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
        
        src_path = self.profile_dir / current
        dst_path = self.profile_dir / new_name
        
        if dst_path.exists():
            QMessageBox.warning(self, "Error", f"Profile '{new_name}' already exists!")
            return
        
        try:
            import yaml
            shutil.copy2(src_path, dst_path)
            
            # Update name in the copied file
            with open(dst_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            data['name'] = new_name.replace('.yaml', '')
            with open(dst_path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self.profile_duplicated.emit(current, new_name)
            self.profiles_changed.emit()
            self.load_profiles()
            
            logger.info(f"Duplicated profile: {current} → {new_name}")
        
        except Exception as e:
            logger.error(f"Failed to duplicate profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to duplicate profile:\n{e}")
    
    def _rename_profile(self):
        """Rename selected profile."""
        current = self.get_current_profile()
        if not current:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        base_name = current.replace('.yaml', '')
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
        
        if new_name == current:
            return
        
        old_path = self.profile_dir / current
        new_path = self.profile_dir / new_name
        
        if new_path.exists():
            QMessageBox.warning(self, "Error", f"Profile '{new_name}' already exists!")
            return
        
        try:
            import yaml
            old_path.rename(new_path)
            
            # Update name in the file
            with open(new_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            data['name'] = new_name.replace('.yaml', '')
            with open(new_path, 'w') as f:
                yaml.safe_dump(data, f)
            
            self.profile_renamed.emit(current, new_name)
            self.profiles_changed.emit()
            self.load_profiles()
            
            # Select the renamed profile by finding item with matching UserRole
            for i in range(self.profile_list.count()):
                item = self.profile_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == new_name:
                    self.profile_list.setCurrentItem(item)
                    break
            
            logger.info(f"Renamed profile: {current} → {new_name}")
        
        except Exception as e:
            logger.error(f"Failed to rename profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to rename profile:\n{e}")
    
    def _delete_profile(self):
        """Delete selected profile."""
        current = self.get_current_profile()
        if not current:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        reply = QMessageBox.question(
            self, "Delete Profile",
            f"Are you sure you want to delete '{current}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                profile_path = self.profile_dir / current
                profile_path.unlink()
                
                self.profile_deleted.emit(current)
                self.profiles_changed.emit()
                self.load_profiles()
                
                logger.info(f"Deleted profile: {current}")
            
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
            
            self.profile_imported.emit(src_path.name)
            self.profiles_changed.emit()
            self.load_profiles()
            
            # Select the imported profile by finding item with matching UserRole
            for i in range(self.profile_list.count()):
                item = self.profile_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == src_path.name:
                    self.profile_list.setCurrentItem(item)
                    break
            
            logger.info(f"Imported profile: {src_path.name}")
            QMessageBox.information(self, "Success", f"Profile '{src_path.name}' imported successfully!")
        
        except Exception as e:
            logger.error(f"Failed to import profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to import profile:\n{e}")
    
    def _export_profile(self):
        """Export current profile to external location."""
        current = self.get_current_profile()
        if not current:
            QMessageBox.warning(self, "Warning", "No profile selected!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Profile",
            str(Path.home() / current),
            "YAML Files (*.yaml *.yml)"
        )
        
        if not file_path:
            return
        
        try:
            src_path = self.profile_dir / current
            dst_path = Path(file_path)
            shutil.copy2(src_path, dst_path)
            
            logger.info(f"Exported profile: {current} → {dst_path}")
            QMessageBox.information(self, "Success", f"Profile exported to:\n{dst_path}")
        
        except Exception as e:
            logger.error(f"Failed to export profile: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export profile:\n{e}")
