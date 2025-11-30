"""
Motion Library Dialog — MotionPlay v3.0 FINAL FORM
Professional motion library with sidebar filters, responsive grid, and floating actions.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QWidget, QScrollArea, QGridLayout,
    QFrame, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QEvent
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPen
from .styles.common import COLORS
from .motion_edit_dialog import MotionEditDialog
from .recording_dialog import RecordingDialog

logger = logging.getLogger(__name__)


class MotionCard(QFrame):
    """
    Individual motion card widget with thumbnail and info.
    Single-click: edit, Double-click: select.
    """
    
    single_clicked = pyqtSignal(str)  # Edit motion
    double_clicked = pyqtSignal(str)  # Select motion
    
    def __init__(self, motion_data: Dict, parent=None):
        super().__init__(parent)
        self.motion_data = motion_data
        self.motion_id = motion_data['motion_id']
        
        self.setObjectName("motionCard")
        self.setFixedSize(220, 280)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Click tracking
        self.click_timer = None
        
        self._init_ui()
        self._apply_styles()
    
    def _init_ui(self):
        """Initialize card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        # Preview thumbnail (placeholder if preview.gif missing)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(196, 150)
        self.preview_label.setStyleSheet(f"background-color: {COLORS['GRAY_DARK']}; border: 2px solid {COLORS['RED_DARK']}; border-radius: 5px;")
        
        # Load preview image or create placeholder
        preview_path = self._get_preview_path()
        if preview_path and preview_path.exists():
            pixmap = QPixmap(str(preview_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(196, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.preview_label.setPixmap(scaled)
            else:
                self._create_placeholder_preview()
        else:
            self._create_placeholder_preview()
        
        layout.addWidget(self.preview_label)
        
        # Display name
        display_name = self.motion_data.get('display_name', 'Unknown')
        name_label = QLabel(display_name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        name_label.setStyleSheet(f"color: {COLORS['WHITE']}; background: transparent;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Category tag
        category = self.motion_data.get('category', 'unknown')
        category_display = category.replace('_', ' ').title()
        category_label = QLabel(category_display)
        category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        category_label.setFont(QFont("Arial", 9))
        category_label.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; background: {COLORS['GRAY_DARK']}; border: 1px solid {COLORS['RED_DARK']}; border-radius: 3px; padding: 3px 8px;")
        layout.addWidget(category_label)
        
        # Difficulty indicator
        difficulty = self.motion_data.get('difficulty', 'medium')
        diff_colors = {
            'easy': '#00ff00',
            'medium': '#ffaa00',
            'hard': '#ff3333'
        }
        diff_label = QLabel(f"● {difficulty.upper()}")
        diff_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diff_label.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        diff_label.setStyleSheet(f"color: {diff_colors.get(difficulty, '#ffffff')}; background: transparent;")
        layout.addWidget(diff_label)
        
        layout.addStretch()
    
    def _get_preview_path(self) -> Optional[Path]:
        """Get path to preview.gif for this motion."""
        motion_id = self.motion_id
        base_path = Path("assets/motions")
        
        # Extract folder path from motion_id (e.g., "static/hadoken" -> "static/hadoken")
        motion_path = base_path / motion_id
        preview_path = motion_path / "preview.gif"
        
        return preview_path if preview_path.exists() else None
    
    def _create_placeholder_preview(self):
        """Create placeholder preview image."""
        pixmap = QPixmap(196, 150)
        pixmap.fill(QColor(COLORS['GRAY_DARK']))
        
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(COLORS['RED_DARK']), 2))
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "NO PREVIEW")
        painter.end()
        
        self.preview_label.setPixmap(pixmap)
    
    def _apply_styles(self):
        """Apply card styling."""
        self.setStyleSheet(f"""
            QFrame#motionCard {{
                background-color: {COLORS['BG_BLACK']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 8px;
            }}
            QFrame#motionCard:hover {{
                background-color: {COLORS['GRAY_DARK']};
                border: 3px solid {COLORS['RED_BRIGHT']};
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle single click (will be overridden by double-click)."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.single_clicked.emit(self.motion_id)
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to select motion."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit(self.motion_id)
        super().mouseDoubleClickEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter."""
        self.setStyleSheet(f"""
            QFrame#motionCard {{
                background-color: {COLORS['GRAY_DARK']};
                border: 3px solid {COLORS['RED_BRIGHT']};
            }}
        """)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave."""
        self._apply_styles()
        super().leaveEvent(event)


class MotionLibraryDialog(QDialog):
    """
    MotionPlay v3.0 FINAL FORM — Professional Motion Library.
    Sidebar filters, responsive grid, floating + button.
    Single-click: edit, Double-click: select.
    """
    
    motion_selected = pyqtSignal(str)  # Emits selected motion_id
    
    # All available tags for filtering
    ALL_TAGS = {'fighting', 'fps', 'moba', 'racing', 'basic', 'combo', 'punch', 'kick', 'defense', 'special'}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.motions_dir = Path("assets/motions")
        self.all_motions: List[Dict] = []
        self.filtered_motions: List[Dict] = []
        self.motion_cards: List[MotionCard] = []
        
        # Filter state
        self.active_tags: Set[str] = set()  # Empty = show all
        self.search_text: str = ""
        
        # Floating button
        self.add_button = None
        
        self.setWindowTitle("Motion Library — MotionPlay v3.0 FINAL FORM")
        self.setMinimumSize(1200, 800)
        self.setModal(True)
        
        self._init_ui()
        self._load_motions()
        self._apply_styles()
        
        logger.info("Motion Library v3.0 opened")
    
    def _init_ui(self):
        """Initialize v3.0 UI with sidebar and content area."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header bar
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet(f"background-color: {COLORS['PURE_BLACK']}; border-bottom: 3px solid {COLORS['RED_BRIGHT']};")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 0, 30, 0)
        
        title = QLabel("MOTION LIBRARY")
        title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; letter-spacing: 4px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search motions...")
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setFixedSize(350, 45)
        self.search_input.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_input)
        
        main_layout.addWidget(header_widget)
        
        # Content: Sidebar + Grid
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Left sidebar for filters
        sidebar = self._create_sidebar()
        content_layout.addWidget(sidebar)
        
        # Main content area with grid
        content_area = self._create_content_area()
        content_layout.addWidget(content_area, 1)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        # Floating + button (will be positioned in resizeEvent)
        self.add_button = QPushButton("+")
        self.add_button.setParent(self)
        self.add_button.setFixedSize(70, 70)
        self.add_button.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.add_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 4px solid {COLORS['RED_BRIGHT']};
                border-radius: 35px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
                border: 4px solid {COLORS['WHITE']};
            }}
        """)
        self.add_button.clicked.connect(self._on_create_motion)
        self.add_button.show()
    
    def _create_sidebar(self) -> QWidget:
        """Create left sidebar with tag filters."""
        sidebar = QFrame()
        sidebar.setFixedWidth(280)
        sidebar.setStyleSheet(f"background-color: {COLORS['BG_BLACK']}; border-right: 2px solid {COLORS['RED_DARK']};")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(15)
        
        # Filter title
        filter_title = QLabel("FILTER BY TAGS")
        filter_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        filter_title.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; letter-spacing: 2px;")
        sidebar_layout.addWidget(filter_title)
        
        # Tag checkboxes
        self.tag_checkboxes: Dict[str, QCheckBox] = {}
        
        for tag in sorted(self.ALL_TAGS):
            checkbox = QCheckBox(tag.upper())
            checkbox.setFont(QFont("Arial", 11))
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {COLORS['WHITE']};
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                    border: 2px solid {COLORS['RED_DARK']};
                    border-radius: 3px;
                    background-color: {COLORS['GRAY_DARK']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {COLORS['RED_PRIMARY']};
                    border: 2px solid {COLORS['RED_BRIGHT']};
                }}
            """)
            checkbox.stateChanged.connect(self._on_filter_changed)
            self.tag_checkboxes[tag] = checkbox
            sidebar_layout.addWidget(checkbox)
        
        sidebar_layout.addStretch()
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.setMinimumHeight(40)
        clear_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_DARK']};
            }}
        """)
        clear_btn.clicked.connect(self._clear_filters)
        sidebar_layout.addWidget(clear_btn)
        
        return sidebar
    
    def _create_content_area(self) -> QWidget:
        """Create main content area with responsive motion grid."""
        content = QWidget()
        content.setStyleSheet(f"background-color: {COLORS['PURE_BLACK']};")
        
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(0)
        
        # Scrollable grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.scroll_content.setStyleSheet(f"background-color: {COLORS['PURE_BLACK']};")
        
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(25)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self.scroll_content)
        content_layout.addWidget(self.scroll_area)
        
        return content
    
    def _load_motions(self):
        """Load all motions from assets/motions/."""
        if not self.motions_dir.exists():
            logger.warning(f"Motions directory not found: {self.motions_dir}")
            QMessageBox.warning(self, "Warning", f"Motions directory not found:\n{self.motions_dir}")
            return
        
        self.all_motions = []
        
        # Load static (built-in) motions
        static_dir = self.motions_dir / "static"
        if static_dir.exists():
            for motion_folder in static_dir.iterdir():
                if motion_folder.is_dir():
                    motion_data = self._load_motion_metadata(motion_folder, "static")
                    if motion_data:
                        self.all_motions.append(motion_data)
        
        # Load user (custom) motions
        user_dir = self.motions_dir / "user"
        if user_dir.exists():
            for motion_folder in user_dir.iterdir():
                if motion_folder.is_dir():
                    motion_data = self._load_motion_metadata(motion_folder, "user")
                    if motion_data:
                        self.all_motions.append(motion_data)
        
        logger.info(f"Loaded {len(self.all_motions)} motions")
        
        # Initial display
        self._update_motion_grid()
    
    def _load_motion_metadata(self, motion_folder: Path, category: str) -> Optional[Dict]:
        """Load metadata.json from motion folder."""
        metadata_file = motion_folder / "metadata.json"
        
        if not metadata_file.exists():
            logger.warning(f"No metadata.json in {motion_folder.name}")
            return None
        
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                data['_folder'] = motion_folder
                data['_type'] = category  # 'static' or 'user'
                return data
        except Exception as e:
            logger.error(f"Failed to load metadata from {metadata_file}: {e}")
            return None
    
    def _update_motion_grid(self):
        """Update motion grid based on filters."""
        # Apply filters
        filtered = []
        for motion in self.all_motions:
            # Tag filter (if any tags selected, motion must have at least one)
            if self.active_tags:
                motion_tags = set(motion.get('tags', []))
                if not motion_tags.intersection(self.active_tags):
                    continue
            
            # Search filter
            if self.search_text:
                display_name = motion.get('display_name', '').lower()
                description = motion.get('description', '').lower()
                tags = ' '.join(motion.get('tags', [])).lower()
                
                if (self.search_text not in display_name and 
                    self.search_text not in description and 
                    self.search_text not in tags):
                    continue
            
            filtered.append(motion)
        
        self.filtered_motions = filtered
        
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        self.motion_cards = []
        
        # Calculate responsive columns based on width
        available_width = self.scroll_area.width() - 50  # Account for margins
        card_width = 220 + 25  # Card width + spacing
        columns = max(1, available_width // card_width)
        
        # Add motion cards
        for i, motion_data in enumerate(filtered):
            card = MotionCard(motion_data)
            card.single_clicked.connect(self._on_motion_edit)
            card.double_clicked.connect(self._on_motion_select)
            self.motion_cards.append(card)
            
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(card, row, col)
        
        # Empty state
        if not filtered:
            empty_label = QLabel("No motions found")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setFont(QFont("Arial", 18))
            empty_label.setStyleSheet(f"color: {COLORS['GRAY']}; padding: 80px;")
            self.grid_layout.addWidget(empty_label, 0, 0, 1, columns)
        
        logger.info(f"Displaying {len(filtered)} motions")
    
    def _on_search_changed(self, text: str):
        """Handle search text change."""
        self.search_text = text.lower()
        self._update_motion_grid()
    
    def _on_filter_changed(self):
        """Handle tag filter change."""
        self.active_tags = {tag for tag, cb in self.tag_checkboxes.items() if cb.isChecked()}
        self._update_motion_grid()
    
    def _clear_filters(self):
        """Clear all tag filters."""
        for checkbox in self.tag_checkboxes.values():
            checkbox.setChecked(False)
        self.active_tags.clear()
        self._update_motion_grid()
    
    def _on_motion_edit(self, motion_id: str):
        """Handle single-click: open edit dialog."""
        motion_data = next((m for m in self.all_motions if m['motion_id'] == motion_id), None)
        if not motion_data:
            return
        
        # Extract just the motion folder name (e.g., "hadoken" from "static/hadoken")
        motion_folder = motion_id.split('/')[-1]
        
        dialog = MotionEditDialog(motion_folder, self)
        dialog.motion_saved.connect(lambda: self._reload_motion(motion_id))
        dialog.motion_deleted.connect(lambda: self._remove_motion(motion_id))
        dialog.exec()
    
    def _on_motion_select(self, motion_id: str):
        """Handle double-click: select and close."""
        logger.info(f"Motion selected: {motion_id}")
        self.motion_selected.emit(motion_id)
        self.accept()
    
    def _on_create_motion(self):
        """Handle + button: create new motion."""
        dialog = RecordingDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload motions to show new one
            self._load_motions()
            logger.info("New motion created")
    
    def _reload_motion(self, motion_id: str):
        """Reload a specific motion after edit."""
        # Find and reload the motion metadata
        for i, motion in enumerate(self.all_motions):
            if motion['motion_id'] == motion_id:
                motion_folder = motion['_folder']
                updated_motion = self._load_motion_metadata(motion_folder, motion['_type'])
                if updated_motion:
                    self.all_motions[i] = updated_motion
                break
        
        self._update_motion_grid()
        logger.info(f"Reloaded motion: {motion_id}")
    
    def _remove_motion(self, motion_id: str):
        """Remove motion from list after deletion."""
        self.all_motions = [m for m in self.all_motions if m['motion_id'] != motion_id]
        self._update_motion_grid()
        logger.info(f"Removed motion: {motion_id}")
    
    def resizeEvent(self, event):
        """Position floating button on resize."""
        super().resizeEvent(event)
        if self.add_button:
            # Position bottom-right with 30px margin
            x = self.width() - self.add_button.width() - 30
            y = self.height() - self.add_button.height() - 30
            self.add_button.move(x, y)
    
    def _apply_styles(self):
        """Apply v3.0 nuclear black theme."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['PURE_BLACK']};
            }}
            
            QLineEdit {{
                background-color: {COLORS['GRAY_DARK']};
                color: {COLORS['WHITE']};
                border: 2px solid {COLORS['RED_DARK']};
                border-radius: 8px;
                padding: 10px 15px;
            }}
            QLineEdit:focus {{
                border: 3px solid {COLORS['RED_BRIGHT']};
            }}
            
            QScrollArea {{
                background-color: {COLORS['PURE_BLACK']};
                border: none;
            }}
            
            QScrollBar:vertical {{
                background-color: {COLORS['GRAY_DARK']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {COLORS['RED_DARK']};
                border-radius: 6px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['RED_PRIMARY']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
