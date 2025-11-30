"""
Motion Edit Dialog — MotionPlay v3.0
Professional motion metadata editor with preview upload and re-record functionality.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QFileDialog, QMessageBox, QWidget,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from .styles.common import COLORS

logger = logging.getLogger(__name__)


class TagChip(QFrame):
    """Tag chip widget with remove button."""
    
    removed = pyqtSignal(str)  # Emits tag name
    
    def __init__(self, tag: str, parent=None):
        super().__init__(parent)
        self.tag = tag
        
        self.setObjectName("tagChip")
        self.setFixedHeight(32)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # Tag label
        label = QLabel(tag)
        label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {COLORS['WHITE']}; background: transparent;")
        layout.addWidget(label)
        
        # Remove button
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(20, 20)
        remove_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_DARK']};
                color: {COLORS['WHITE']};
                border: none;
                border-radius: 10px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
            }}
        """)
        remove_btn.clicked.connect(lambda: self.removed.emit(self.tag))
        layout.addWidget(remove_btn)
        
        self.setStyleSheet(f"""
            QFrame#tagChip {{
                background-color: {COLORS['RED_PRIMARY']};
                border: 1px solid {COLORS['RED_BRIGHT']};
                border-radius: 16px;
            }}
        """)


class MotionEditDialog(QDialog):
    """
    Professional motion metadata editor.
    Edit name, description, tags, preview image, and re-record motion.
    """
    
    motion_saved = pyqtSignal(str)  # Emits motion name
    motion_deleted = pyqtSignal(str)  # Emits motion name
    
    def __init__(self, motion_name: Optional[str] = None, parent=None):
        super().__init__(parent)
        
        self.motion_name = motion_name
        self.motion_dir = Path("assets/motions/user")
        self.tags = []
        self.preview_path = None
        
        self.setWindowTitle("Edit Motion" if motion_name else "Create New Motion")
        self.setMinimumSize(700, 650)
        self.setModal(True)
        
        self._init_ui()
        self._apply_styles()
        
        if motion_name:
            self._load_motion_data()
        
        logger.info(f"Motion Edit Dialog opened: {motion_name or 'New'}")
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("EDIT MOTION" if self.motion_name else "CREATE NEW MOTION")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; letter-spacing: 2px;")
        layout.addWidget(title)
        
        # Preview image
        preview_label = QLabel("PREVIEW")
        preview_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        preview_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        layout.addWidget(preview_label)
        
        preview_container = QHBoxLayout()
        
        self.preview_display = QLabel()
        self.preview_display.setFixedSize(250, 200)
        self.preview_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_display.setStyleSheet(f"""
            background-color: {COLORS['GRAY_DARK']};
            border: 2px solid {COLORS['RED_DARK']};
            border-radius: 8px;
        """)
        self._set_placeholder_preview()
        preview_container.addWidget(self.preview_display)
        
        preview_buttons = QVBoxLayout()
        preview_buttons.setSpacing(10)
        
        upload_btn = QPushButton("Upload Preview")
        upload_btn.setMinimumHeight(45)
        upload_btn.setFont(QFont("Arial", 11))
        upload_btn.setStyleSheet(self._button_style())
        upload_btn.clicked.connect(self._upload_preview)
        preview_buttons.addWidget(upload_btn)
        
        self.rerecord_btn = QPushButton("Re-record Motion")
        self.rerecord_btn.setMinimumHeight(45)
        self.rerecord_btn.setFont(QFont("Arial", 11))
        self.rerecord_btn.setStyleSheet(self._button_style())
        self.rerecord_btn.clicked.connect(self._rerecord_motion)
        self.rerecord_btn.setEnabled(bool(self.motion_name))
        preview_buttons.addWidget(self.rerecord_btn)
        
        preview_buttons.addStretch()
        preview_container.addLayout(preview_buttons)
        preview_container.addStretch()
        
        layout.addLayout(preview_container)
        
        # Name field
        name_label = QLabel("MOTION NAME")
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Forward Punch, Hadoken, Uppercut")
        self.name_input.setMinimumHeight(45)
        self.name_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.name_input)
        
        # Description field
        desc_label = QLabel("DESCRIPTION")
        desc_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        desc_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Brief description of the motion...")
        self.desc_input.setMinimumHeight(80)
        self.desc_input.setMaximumHeight(120)
        self.desc_input.setFont(QFont("Arial", 11))
        layout.addWidget(self.desc_input)
        
        # Tags section
        tags_label = QLabel("TAGS")
        tags_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        tags_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        layout.addWidget(tags_label)
        
        # Tags display area
        self.tags_container = QWidget()
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setContentsMargins(0, 0, 0, 0)
        self.tags_layout.setSpacing(8)
        self.tags_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.tags_container)
        
        # Add tag input
        add_tag_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Add tag (e.g., fighting, punch, combo)")
        self.tag_input.setMinimumHeight(40)
        self.tag_input.setFont(QFont("Arial", 11))
        self.tag_input.returnPressed.connect(self._add_tag)
        add_tag_layout.addWidget(self.tag_input, 1)
        
        add_tag_btn = QPushButton("+ Add Tag")
        add_tag_btn.setMinimumHeight(40)
        add_tag_btn.setMinimumWidth(120)
        add_tag_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        add_tag_btn.setStyleSheet(self._button_style())
        add_tag_btn.clicked.connect(self._add_tag)
        add_tag_layout.addWidget(add_tag_btn)
        
        layout.addLayout(add_tag_layout)
        
        layout.addStretch()
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        if self.motion_name:
            delete_btn = QPushButton("Delete Motion")
            delete_btn.setMinimumSize(140, 50)
            delete_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            delete_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['RED_DARK']};
                    color: {COLORS['WHITE']};
                    border: 2px solid {COLORS['RED_PRIMARY']};
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['RED_PRIMARY']};
                    border: 2px solid {COLORS['RED_BRIGHT']};
                }}
            """)
            delete_btn.clicked.connect(self._delete_motion)
            button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumSize(120, 50)
        cancel_btn.setFont(QFont("Arial", 11))
        cancel_btn.setStyleSheet(f"""
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
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Motion")
        save_btn.setMinimumSize(150, 50)
        save_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 3px solid {COLORS['RED_BRIGHT']};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
            }}
        """)
        save_btn.clicked.connect(self._save_motion)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _button_style(self) -> str:
        """Standard button style."""
        return f"""
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
            QPushButton:disabled {{
                background-color: {COLORS['GRAY']};
                color: {COLORS['GRAY_LIGHT']};
                border: 2px solid {COLORS['GRAY']};
            }}
        """
    
    def _set_placeholder_preview(self):
        """Set placeholder preview image."""
        pixmap = QPixmap(250, 200)
        pixmap.fill(QColor(COLORS['RED_DARK']))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(COLORS['WHITE']))
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "NO PREVIEW")
        painter.end()
        
        self.preview_display.setPixmap(pixmap)
    
    def _load_motion_data(self):
        """Load existing motion metadata."""
        if not self.motion_name:
            return
        
        motion_path = self.motion_dir / self.motion_name
        metadata_file = motion_path / "metadata.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                
                self.name_input.setText(data.get('display_name', self.motion_name))
                self.desc_input.setPlainText(data.get('description', ''))
                self.tags = data.get('tags', [])
                self._refresh_tags()
                
                # Load preview
                preview_file = motion_path / "preview.gif"
                if not preview_file.exists():
                    preview_file = motion_path / "preview.png"
                
                if preview_file.exists():
                    pixmap = QPixmap(str(preview_file))
                    if not pixmap.isNull():
                        scaled = pixmap.scaled(250, 200, Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
                        self.preview_display.setPixmap(scaled)
                        self.preview_path = preview_file
                
            except Exception as e:
                logger.error(f"Failed to load motion metadata: {e}")
    
    def _add_tag(self):
        """Add a tag."""
        tag = self.tag_input.text().strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self._refresh_tags()
            self.tag_input.clear()
    
    def _remove_tag(self, tag: str):
        """Remove a tag."""
        if tag in self.tags:
            self.tags.remove(tag)
            self._refresh_tags()
    
    def _refresh_tags(self):
        """Refresh tags display."""
        # Clear existing
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # Add tag chips
        for tag in self.tags:
            chip = TagChip(tag)
            chip.removed.connect(self._remove_tag)
            self.tags_layout.addWidget(chip)
        
        self.tags_layout.addStretch()
    
    def _upload_preview(self):
        """Upload preview image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Preview Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif);;All Files (*)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(250, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
                self.preview_display.setPixmap(scaled)
                self.preview_path = Path(file_path)
                logger.info(f"Preview image uploaded: {file_path}")
    
    def _rerecord_motion(self):
        """Re-record motion (opens recording dialog)."""
        # TODO: Integrate with recording system
        QMessageBox.information(self, "Re-record", "Recording system integration coming soon!")
    
    def _save_motion(self):
        """Save motion metadata."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a motion name.")
            return
        
        # Create motion folder
        folder_name = name.lower().replace(' ', '_')
        motion_path = self.motion_dir / folder_name
        motion_path.mkdir(parents=True, exist_ok=True)
        
        # Save metadata
        metadata = {
            "motion_id": f"user/{folder_name}",
            "display_name": name,
            "description": self.desc_input.toPlainText().strip(),
            "category": "custom",
            "difficulty": "medium",
            "tags": self.tags,
            "preview_gif": "preview.gif",
            "author": "User",
            "created_date": "2026-01-01",
            "version": "1.0"
        }
        
        try:
            with open(motion_path / "metadata.json", 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Copy preview if uploaded
            if self.preview_path and self.preview_path.exists():
                import shutil
                dest = motion_path / f"preview{self.preview_path.suffix}"
                shutil.copy(str(self.preview_path), str(dest))
            
            logger.info(f"Motion saved: {name}")
            self.motion_saved.emit(folder_name)
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to save motion: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save motion:\n{e}")
    
    def _delete_motion(self):
        """Delete motion."""
        if not self.motion_name:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Motion",
            f"Permanently delete motion '{self.motion_name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            motion_path = self.motion_dir / self.motion_name
            
            try:
                import shutil
                shutil.rmtree(motion_path)
                
                logger.info(f"Motion deleted: {self.motion_name}")
                self.motion_deleted.emit(self.motion_name)
                self.accept()
                
            except Exception as e:
                logger.error(f"Failed to delete motion: {e}")
                QMessageBox.critical(self, "Delete Error", f"Failed to delete motion:\n{e}")
    
    def _apply_styles(self):
        """Apply black-red theme."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['PURE_BLACK']};
            }}
            
            QLineEdit, QTextEdit {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 5px;
                padding: 8px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {COLORS['RED_BRIGHT']};
            }}
        """)
