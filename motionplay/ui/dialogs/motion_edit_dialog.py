"""
Motion Edit Dialog — MotionPlay v3.0 FINAL RECKONING
Simple, beautiful, no bugs. Complete redesign.
"""

import json
import logging
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFileDialog, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QColor
from ...utils.dark_dialogs import (
    BlackDialog, BlackInputDialog, BlackMultiLineInputDialog,
    show_warning, show_question, show_error
)
from ...styles.colors import COLORS

logger = logging.getLogger(__name__)


class MotionEditDialog(BlackDialog):
    """
    Simple, beautiful motion editor.
    Shows current values with Edit buttons - popup inline editing.
    """
    
    motion_saved = pyqtSignal(str)  # Emits motion name
    motion_deleted = pyqtSignal(str)  # Emits motion name
    
    def __init__(self, motion_name: str, parent=None):
        """
        Initialize motion edit dialog.
        
        Args:
            motion_name: Name of motion to edit (required - folder name in user/)
            parent: Parent widget
        """
        super().__init__(parent)
        
        if not motion_name:
            raise ValueError("motion_name is required for editing")
        
        self.motion_name = motion_name
        self.motion_dir = Path("assets/motions/user")
        self.motion_path = self.motion_dir / motion_name
        
        # Current data
        self.display_name = ""
        self.description = ""
        self.tags = []
        self.preview_path = None
        
        self.setWindowTitle(f"Edit Motion: {motion_name}")
        self.setMinimumSize(700, 800)
        self.setModal(True)
        
        # Load data first
        self._load_motion_data()
        
        # Then build UI
        self._init_ui()
        
        logger.info(f"Motion Edit Dialog opened: {motion_name}")
    
    def _init_ui(self):
        """Initialize beautiful simple UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Title
        title = QLabel(f"EDIT MOTION: {self.motion_name.upper()}")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; letter-spacing: 3px;")
        layout.addWidget(title)
        
        layout.addSpacing(10)
        
        # Large preview in center
        preview_container = QWidget()
        preview_layout = QVBoxLayout(preview_container)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(10)
        
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(400, 300)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(f"""
            background-color: {COLORS['GRAY_DARK']};
            border: 3px solid {COLORS['RED_DARK']};
            border-radius: 10px;
        """)
        self._update_preview()
        preview_layout.addWidget(self.preview_label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Change image button below preview
        change_img_btn = QPushButton("Change Image/GIF")
        change_img_btn.setMinimumHeight(50)
        change_img_btn.setFixedWidth(400)
        change_img_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        change_img_btn.setStyleSheet(self._action_button_style())
        change_img_btn.clicked.connect(self._change_preview)
        preview_layout.addWidget(change_img_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(preview_container)
        
        layout.addSpacing(10)
        
        # 5 clean sections with Edit buttons
        self._add_field_row(layout, "NAME", self.display_name, self._edit_name)
        self._add_field_row(layout, "DESCRIPTION", self.description or "No description", self._edit_description)
        self._add_field_row(layout, "TAGS", ", ".join(self.tags) if self.tags else "No tags", self._edit_tags)
        
        layout.addSpacing(10)
        
        # Re-record button
        rerecord_btn = QPushButton("Re-record Motion")
        rerecord_btn.setMinimumHeight(55)
        rerecord_btn.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        rerecord_btn.setStyleSheet(self._action_button_style())
        rerecord_btn.clicked.connect(self._rerecord_motion)
        layout.addWidget(rerecord_btn)
        
        layout.addStretch()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        delete_btn = QPushButton("Delete Motion")
        delete_btn.setMinimumSize(160, 60)
        delete_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_DARK']};
                color: {COLORS['WHITE']};
                border: 3px solid {COLORS['RED_PRIMARY']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_PRIMARY']};
                border: 3px solid {COLORS['RED_BRIGHT']};
            }}
        """)
        delete_btn.clicked.connect(self._delete_motion)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(140, 60)
        cancel_btn.setFont(QFont("Arial", 12))
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['GRAY']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['GRAY_LIGHT']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['GRAY_LIGHT']};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setMinimumSize(180, 60)
        save_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 4px solid {COLORS['RED_BRIGHT']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
                border: 4px solid {COLORS['WHITE']};
            }}
        """)
        save_btn.clicked.connect(self._save_motion)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _add_field_row(self, parent_layout: QVBoxLayout, label: str, value: str, edit_callback):
        """Add a field row with label, value, and Edit button."""
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(15)
        
        # Label
        field_label = QLabel(f"{label}:")
        field_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        field_label.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; background: transparent;")
        field_label.setFixedWidth(120)
        container_layout.addWidget(field_label)
        
        # Value display
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 12))
        value_label.setStyleSheet(f"""
            color: {COLORS['WHITE']};
            background-color: {COLORS['GRAY_DARK']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 5px;
            padding: 12px 15px;
        """)
        value_label.setWordWrap(True)
        value_label.setMinimumHeight(50)
        
        # Store reference for updating
        setattr(self, f"{label.lower()}_value_label", value_label)
        container_layout.addWidget(value_label, 1)
        
        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.setMinimumSize(100, 50)
        edit_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        edit_btn.setStyleSheet(f"""
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
        edit_btn.clicked.connect(edit_callback)
        container_layout.addWidget(edit_btn)
        
        parent_layout.addWidget(container)
    
    def _action_button_style(self) -> str:
        """Style for action buttons."""
        return f"""
            QPushButton {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_PRIMARY']};
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_DARK']};
                border: 3px solid {COLORS['RED_BRIGHT']};
            }}
        """
    
    def _load_motion_data(self):
        """Load existing motion metadata."""
        metadata_file = self.motion_path / "metadata.json"
        
        if not metadata_file.exists():
            logger.warning(f"No metadata found for {self.motion_name}")
            self.display_name = self.motion_name.replace('_', ' ').title()
            return
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
            
            self.display_name = data.get('display_name', self.motion_name)
            self.description = data.get('description', '')
            self.tags = data.get('tags', [])
            
            logger.info(f"Loaded motion data: {self.display_name}")
            
        except Exception as e:
            logger.error(f"Failed to load motion metadata: {e}")
            self.display_name = self.motion_name.replace('_', ' ').title()
    
    def _update_preview(self):
        """Update preview image/GIF."""
        # Try to find preview file
        preview_file = self.motion_path / "preview.gif"
        if not preview_file.exists():
            preview_file = self.motion_path / "preview.png"
        
        if preview_file.exists():
            pixmap = QPixmap(str(preview_file))
            if not pixmap.isNull():
                scaled = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
                self.preview_path = preview_file
                return
        
        # Placeholder
        self.preview_label.setText("NO PREVIEW")
        self.preview_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.preview_label.setStyleSheet(f"""
            color: {COLORS['GRAY_LIGHT']};
            background-color: {COLORS['GRAY_DARK']};
            border: 3px solid {COLORS['RED_DARK']};
            border-radius: 10px;
        """)
    
    def _edit_name(self):
        """Edit motion name inline."""
        text, ok = BlackInputDialog.get_text_input(
            self,
            "Edit Name",
            "Motion Name:",
            self.display_name
        )
        
        if ok and text.strip():
            self.display_name = text.strip()
            self.name_value_label.setText(self.display_name)
            logger.info(f"Name updated: {self.display_name}")
    
    def _edit_description(self):
        """Edit description inline."""
        text, ok = BlackMultiLineInputDialog.get_multi_line_text_input(
            self,
            "Edit Description",
            "Motion Description:",
            self.description
        )
        
        if ok:
            self.description = text.strip()
            self.description_value_label.setText(self.description or "No description")
            logger.info("Description updated")
    
    def _edit_tags(self):
        """Edit tags inline."""
        current_tags_str = ", ".join(self.tags)
        text, ok = BlackInputDialog.get_text_input(
            self,
            "Edit Tags",
            "Tags (comma-separated):",
            current_tags_str
        )
        
        if ok:
            # Parse tags
            if text.strip():
                self.tags = [t.strip().lower() for t in text.split(',') if t.strip()]
            else:
                self.tags = []
            
            self.tags_value_label.setText(", ".join(self.tags) if self.tags else "No tags")
            logger.info(f"Tags updated: {self.tags}")
    
    def _change_preview(self):
        """Change preview image/GIF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Preview Image/GIF",
            "",
            "Images (*.png *.jpg *.jpeg *.gif);;All Files (*)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
                self.preview_path = Path(file_path)
                logger.info(f"Preview changed: {file_path}")
    
    def _rerecord_motion(self):
        """Re-record motion (opens recording dialog)."""
        from .recording_dialog import RecordingDialog
        dialog = RecordingDialog(self)
        if dialog.exec():
            logger.info("Motion re-recorded")
            # Reload data
            self._load_motion_data()
            self._update_preview()
    
    def _save_motion(self):
        """Save motion metadata - NEVER creates new motion."""
        if not self.display_name.strip():
            show_warning(self, "Missing Name", "Please enter a motion name.")
            return
        
        # Save to EXISTING motion folder (never create new)
        metadata = {
            "motion_id": f"user/{self.motion_name}",
            "display_name": self.display_name,
            "description": self.description,
            "category": "custom",
            "difficulty": "medium",
            "tags": self.tags,
            "preview_gif": "preview.gif",
            "author": "User",
            "version": "1.0"
        }
        
        try:
            # Save metadata to existing folder
            with open(self.motion_path / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Copy preview if changed
            if self.preview_path and self.preview_path.exists():
                import shutil
                dest = self.motion_path / f"preview{self.preview_path.suffix}"
                if dest != self.preview_path:  # Don't copy to itself
                    shutil.copy(str(self.preview_path), str(dest))
            
            logger.info(f"Motion saved: {self.display_name}")
            self.motion_saved.emit(self.motion_name)
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to save motion: {e}")
            show_error(self, "Save Error", f"Failed to save motion:\n{e}")
    
    def _delete_motion(self):
        """Delete this motion permanently."""
        reply = show_question(
            self,
            "Delete Motion",
            f"Permanently delete motion '{self.display_name}'?\nThis cannot be undone."
        )
        
        if reply == 16384:  # QMessageBox.StandardButton.Yes
            try:
                import shutil
                shutil.rmtree(self.motion_path)
                
                logger.info(f"Motion deleted: {self.motion_name}")
                self.motion_deleted.emit(self.motion_name)
                self.accept()
                
            except Exception as e:
                logger.error(f"Failed to delete motion: {e}")
                show_error(self, "Delete Error", f"Failed to delete motion:\n{e}")
