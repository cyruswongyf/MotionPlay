"""
Main Window for MotionPlay
Clean, modern main window with camera feed and control panel.
"""

import cv2
import logging
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QFont
from .styles import get_stylesheet, COLORS
from .recording_dialog import RecordingDialog
from .profile_manager import ProfileManagerDialog

logger = logging.getLogger(__name__)


class TriggerOverlay(QWidget):
    """Aggressive overlay for motion trigger feedback - pro gaming style."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 150);
            border: 4px solid {COLORS['RED_BRIGHT']};
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # Motion name label - BIG and aggressive
        self.motion_label = QLabel()
        self.motion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motion_label.setFont(QFont("Arial", 100, QFont.Weight.Bold))
        self.motion_label.setStyleSheet(f"""
            color: {COLORS['RED_BRIGHT']};
            text-shadow: 0 0 20px {COLORS['RED_GLOW']};
            letter-spacing: 8px;
        """)
        layout.addWidget(self.motion_label)
        
        # Arrow
        arrow_label = QLabel("→")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        arrow_label.setFont(QFont("Arial", 60, QFont.Weight.Bold))
        arrow_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        layout.addWidget(arrow_label)
        
        # Key label - clear and prominent
        self.key_label = QLabel()
        self.key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_label.setFont(QFont("Arial", 80, QFont.Weight.Bold))
        self.key_label.setStyleSheet(f"""
            color: {COLORS['WHITE']};
            background-color: {COLORS['RED_PRIMARY']};
            padding: 20px 40px;
            border-radius: 15px;
            border: 3px solid {COLORS['RED_BRIGHT']};
        """)
        layout.addWidget(self.key_label)
        
        self.hide()
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
        
        # Fade out animation effect (optional enhancement)
        self.opacity = 1.0
    
    def show_feedback(self, motion: str, key: str):
        """Show trigger feedback with aggressive styling."""
        self.motion_label.setText(motion.upper().replace('_', ' '))
        self.key_label.setText(key.upper())
        self.setStyleSheet(f"""
            background-color: rgba(0, 0, 0, 150);
            border: 4px solid {COLORS['RED_BRIGHT']};
        """)
        self.show()
        self.raise_()
        self.hide_timer.start(800)  # Show for 800ms as specified


class MotionPlayMainWindow(QMainWindow):
    """
    Main application window.
    Pure black + aggressive red theme.
    """
    
    motion_detected = pyqtSignal(str, str)  # motion_name, key_action
    profile_changed = pyqtSignal(str)  # profile_name
    
    def __init__(self, config: dict):
        super().__init__()
        
        self.config = config
        self.current_profile = config['profiles']['default_profile']
        
        # Setup window
        ui_config = config['ui']
        self.setWindowTitle("MotionPlay")
        self.setFixedSize(ui_config['window_width'], ui_config['window_height'])
        
        # State
        self.current_fps = 0
        
        self._init_ui()
        self.setStyleSheet(get_stylesheet())
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        central.setObjectName("central")
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left: Camera feed
        camera_container = QWidget()
        camera_container.setObjectName("cameraContainer")
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setContentsMargins(0, 0, 0, 0)
        
        ui_config = self.config['ui']
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(
            ui_config['camera_width'],
            ui_config['camera_height']
        )
        self.camera_label.setObjectName("cameraLabel")
        camera_layout.addWidget(self.camera_label)
        
        # Trigger overlay
        self.trigger_overlay = TriggerOverlay(camera_container)
        self.trigger_overlay.setGeometry(
            0, 0,
            ui_config['camera_width'],
            ui_config['camera_height']
        )
        
        # Right: Control panel
        control_panel = self._create_control_panel()
        
        main_layout.addWidget(camera_container, 70)
        main_layout.addWidget(control_panel, 30)
    
    def _create_control_panel(self):
        """Create control panel."""
        panel = QWidget()
        panel.setObjectName("controlPanel")
        panel.setFixedWidth(420)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("MotionPlay")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Detected motion section
        motion_label = QLabel("Detected Motion:")
        motion_label.setObjectName("sectionLabel")
        motion_label.setFont(QFont("Arial", 12))
        layout.addWidget(motion_label)
        
        self.motion_name = QLabel("READY")
        self.motion_name.setObjectName("motion_name")
        self.motion_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.motion_name.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.motion_name.setMinimumHeight(100)
        self.motion_name.setStyleSheet(f"""
            color: {COLORS['RED_BRIGHT']};
            background-color: rgba(255, 26, 26, 20);
            border: 2px solid {COLORS['RED_PRIMARY']};
            border-radius: 10px;
            padding: 10px;
            letter-spacing: 4px;
        """)
        layout.addWidget(self.motion_name)
        
        # Triggers - aggressive display
        trigger_container = QWidget()
        trigger_layout = QVBoxLayout(trigger_container)
        trigger_layout.setContentsMargins(0, 10, 0, 10)
        trigger_layout.setSpacing(5)
        
        trigger_label = QLabel("⚡ TRIGGERS")
        trigger_label.setObjectName("triggerLabel")
        trigger_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        trigger_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trigger_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        trigger_layout.addWidget(trigger_label)
        
        self.key_action = QLabel("--")
        self.key_action.setObjectName("key_action")
        self.key_action.setFont(QFont("Arial", 44, QFont.Weight.Bold))
        self.key_action.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.key_action.setMinimumHeight(70)
        self.key_action.setStyleSheet(f"""
            color: {COLORS['WHITE']};
            background-color: {COLORS['RED_PRIMARY']};
            border: 3px solid {COLORS['RED_BRIGHT']};
            border-radius: 12px;
            padding: 10px;
        """)
        trigger_layout.addWidget(self.key_action)
        
        layout.addWidget(trigger_container)
        layout.addSpacing(15)
        
        # Profile selector
        profile_label = QLabel("Combat Profile:")
        profile_label.setObjectName("sectionLabel")
        profile_label.setFont(QFont("Arial", 12))
        layout.addWidget(profile_label)
        
        self.profile_combo = QComboBox()
        self.profile_combo.setObjectName("profileCombo")
        self.profile_combo.setFont(QFont("Arial", 14))
        self.profile_combo.setMinimumHeight(45)
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        layout.addWidget(self.profile_combo)
        
        layout.addSpacing(20)
        
        # Action buttons
        self.record_btn = QPushButton("RECORD NEW MOTION")
        self.record_btn.setObjectName("recordButton")
        self.record_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.record_btn.setMinimumHeight(55)
        self.record_btn.clicked.connect(self._open_record_dialog)
        layout.addWidget(self.record_btn)
        
        self.edit_btn = QPushButton("Edit Profile")
        self.edit_btn.setObjectName("actionButton")
        self.edit_btn.setFont(QFont("Arial", 12))
        self.edit_btn.setMinimumHeight(45)
        self.edit_btn.clicked.connect(self._open_profile_manager)
        layout.addWidget(self.edit_btn)
        
        layout.addStretch()
        
        # Exit button
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.setObjectName("exitButton")
        self.exit_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.exit_btn.setMinimumHeight(45)
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn)
        
        # Status bar
        self.status_bar = QLabel(f"Profile: {self.current_profile} │ FPS: 0")
        self.status_bar.setObjectName("statusBar")
        self.status_bar.setFont(QFont("Arial", 10))
        self.status_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_bar.setMinimumHeight(35)
        layout.addWidget(self.status_bar)
        
        return panel
    
    def update_frame(self, frame):
        """Update camera feed."""
        if frame is None:
            return
        
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_image)
        scaled = pixmap.scaled(
            self.camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled)
    
    def update_motion(self, motion: str, key: str):
        """Update detected motion display with aggressive styling."""
        self.motion_name.setText(motion.upper().replace('_', ' '))
        self.key_action.setText(key.upper())
        
        # Flash effect - brief highlight on trigger
        self.motion_name.setStyleSheet(f"""
            color: {COLORS['WHITE']};
            background-color: {COLORS['RED_BRIGHT']};
            border: 3px solid {COLORS['RED_GLOW']};
            border-radius: 10px;
            padding: 10px;
            letter-spacing: 4px;
        """)
        
        # Reset after brief flash
        QTimer.singleShot(300, lambda: self.motion_name.setStyleSheet(f"""
            color: {COLORS['RED_BRIGHT']};
            background-color: rgba(255, 26, 26, 20);
            border: 2px solid {COLORS['RED_PRIMARY']};
            border-radius: 10px;
            padding: 10px;
            letter-spacing: 4px;
        """))
    
    def show_trigger_feedback(self, motion: str, key: str):
        """Show trigger feedback overlay."""
        if self.config['ui']['overlay']['trigger_feedback']:
            self.trigger_overlay.show_feedback(motion, key)
    
    def update_fps(self, fps: int):
        """Update FPS display."""
        self.current_fps = fps
        self.status_bar.setText(f"🎮 {self.current_profile.upper()} │ FPS: {fps} │ READY")
    
    def set_profiles(self, profiles: list):
        """Set available profiles."""
        current = self.profile_combo.currentText()
        self.profile_combo.clear()
        self.profile_combo.addItems(profiles)
        
        idx = self.profile_combo.findText(current)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)
    
    def _on_profile_changed(self, profile_name: str):
        """Handle profile change."""
        self.current_profile = profile_name
        self.profile_changed.emit(profile_name)
        self.update_fps(self.current_fps)
    
    def _open_record_dialog(self):
        """Open recording dialog."""
        dialog = RecordingDialog(self, self.config)
        dialog.exec()
    
    def _open_profile_manager(self):
        """Open profile manager."""
        dialog = ProfileManagerDialog(self, self.config)
        dialog.profile_changed.connect(self._on_profile_changed)
        dialog.exec()
