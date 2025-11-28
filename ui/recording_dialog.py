"""
Recording Dialog for MotionPlay
Clean modal dialog for recording new motion gestures.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from .styles import get_dialog_stylesheet, COLORS

logger = logging.getLogger(__name__)


class RecordingDialog(QDialog):
    """
    Modal dialog for recording motion gestures.
    Features countdown, live preview, and progress tracking.
    """
    
    def __init__(self, parent=None, config: dict = None):
        super().__init__(parent)
        
        self.config = config or {}
        self.max_reps = 5
        self.recorded_count = 0
        self.recording = False
        
        self.setWindowTitle("Record New Motion")
        self.setFixedSize(900, 700)
        self.setModal(True)
        
        self._init_ui()
        self.setStyleSheet(get_dialog_stylesheet())
        
        logger.info("Recording dialog opened")
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Countdown label (hidden initially)
        self.countdown_label = QLabel("3")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 120, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet(f"color: {COLORS['RED_PRIMARY']};")
        self.countdown_label.setMinimumHeight(180)
        self.countdown_label.hide()
        layout.addWidget(self.countdown_label)
        
        # Instruction
        self.instruction = QLabel("Perform the motion clearly 5 times")
        self.instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction.setFont(QFont("Arial", 16))
        self.instruction.setStyleSheet(f"color: {COLORS['WHITE']};")
        layout.addWidget(self.instruction)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(self.max_reps)
        self.progress.setValue(0)
        self.progress.setFormat("Repetitions: %v / %m")
        self.progress.setMinimumHeight(35)
        layout.addWidget(self.progress)
        
        # Motion name input
        name_container = QWidget()
        name_layout = QHBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        
        name_label = QLabel("Motion Name:")
        name_label.setFont(QFont("Arial", 14))
        name_label.setStyleSheet(f"color: {COLORS['WHITE']};")
        name_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter motion name (e.g., Hadouken)")
        self.name_input.setFont(QFont("Arial", 14))
        self.name_input.setMinimumHeight(45)
        name_layout.addWidget(self.name_input)
        
        layout.addWidget(name_container)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Arial", 13))
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setMinimumWidth(150)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        self.start_btn = QPushButton("START RECORDING")
        self.start_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.start_btn.setMinimumHeight(60)
        self.start_btn.setMinimumWidth(250)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['RED_PRIMARY']};
                color: {COLORS['WHITE']};
                border: 3px solid {COLORS['RED_BRIGHT']};
                border-radius: 10px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['RED_BRIGHT']};
            }}
        """)
        self.start_btn.clicked.connect(self._start_recording)
        button_layout.addWidget(self.start_btn)
        
        layout.addLayout(button_layout)
    
    def _start_recording(self):
        """Start recording process."""
        motion_name = self.name_input.text().strip()
        if not motion_name:
            self.name_input.setFocus()
            return
        
        self.start_btn.setEnabled(False)
        self.name_input.setEnabled(False)
        
        # Show countdown
        self.countdown_label.show()
        self._countdown(3)
        
        logger.info(f"Recording started: {motion_name}")
    
    def _countdown(self, value):
        """Countdown before recording."""
        if value > 0:
            self.countdown_label.setText(str(value))
            QTimer.singleShot(1000, lambda: self._countdown(value - 1))
        else:
            self.countdown_label.setText("RECORDING!!!")
            self.recording = True
            self.instruction.setText("Perform the motion NOW!")
            self._simulate_recording()
    
    def _simulate_recording(self):
        """Simulate recording progress."""
        # This would be connected to actual motion recorder
        self.recorded_count = 0
        
        def add_rep():
            self.recorded_count += 1
            self.progress.setValue(self.recorded_count)
            if self.recorded_count >= self.max_reps:
                self._complete_recording()
        
        self.rep_timer = QTimer()
        self.rep_timer.timeout.connect(add_rep)
        self.rep_timer.start(1000)
    
    def _complete_recording(self):
        """Complete recording."""
        self.rep_timer.stop()
        self.recording = False
        
        self.countdown_label.setText("MOTION LEARNED")
        self.instruction.setText("Motion captured successfully!")
        
        QTimer.singleShot(1000, self.accept)
        
        logger.info(f"Recording completed: {self.name_input.text()}")
