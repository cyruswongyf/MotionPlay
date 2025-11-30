"""
Recording Dialog for MotionPlay
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QProgressBar, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QImage
from ...utils.dark_dialogs import BlackDialog
from ...styles.colors import COLORS

logger = logging.getLogger(__name__)


class RecordingDialog(BlackDialog):
    """
    Modal dialog for recording motion gestures.
    Features countdown, live camera preview, progress tracking, and saving.
    """
    
    # Signals
    recording_started = pyqtSignal(str)  # Motion name
    frame_recorded = pyqtSignal()
    sequence_completed = pyqtSignal()
    recording_finished = pyqtSignal(str, list)  # Motion name, file paths
    
    def __init__(self, parent=None, camera=None, processor=None, recorder=None, config: dict = None):
        super().__init__(parent)
        
        self.config = config or {}
        self.camera = camera
        self.processor = processor
        self.recorder = recorder
        
        self.max_reps = 5
        self.recorded_count = 0
        self.recording = False
        self.countdown_active = False
        self.current_countdown = 3
        
        self.setWindowTitle("Record New Motion")
        self.setFixedSize(1000, 800)
        self.setModal(True)
        
        self._init_ui()
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {COLORS['BG_BLACK']}; color: white; }}
            QPushButton {{ 
                background-color: #333333; 
                color: white; 
                border: 2px solid {COLORS['RED_PRIMARY']}; 
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLORS['RED_PRIMARY']}; }}
            QLabel {{ color: white; background-color: transparent; }}
        """)
        
        if self.camera and self.processor:
            self.preview_timer = QTimer()
            self.preview_timer.timeout.connect(self._update_preview)
            self.preview_timer.start(33)  # ~30 FPS
        
        logger.info("Recording dialog opened")
    
    def _init_ui(self):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("🎬 Record Custom Gesture")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['RED_BRIGHT']};")
        layout.addWidget(title)
        
        # Camera preview
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setMaximumSize(640, 360)
        self.preview_label.setStyleSheet(f"QLabel {{ background-color: {COLORS['DARK_BG']}; border: 3px solid {COLORS['RED_PRIMARY']}; border-radius: 10px; }}")
        layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Countdown overlay (hidden initially)
        self.countdown_label = QLabel("3")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setFont(QFont("Arial", 120, QFont.Weight.Bold))
        self.countdown_label.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; background-color: rgba(0, 0, 0, 180); border-radius: 20px; padding: 20px;")
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
        self.start_btn.setStyleSheet(f"QPushButton {{ background-color: {COLORS['RED_PRIMARY']}; color: {COLORS['WHITE']}; border: 3px solid {COLORS['RED_BRIGHT']}; border-radius: 10px; font-weight: bold; letter-spacing: 2px; }} QPushButton:hover {{ background-color: {COLORS['RED_BRIGHT']}; }}")
        self.start_btn.clicked.connect(self._start_recording)
        button_layout.addWidget(self.start_btn)
        
        layout.addLayout(button_layout)
    
    def _update_preview(self):
        """Update camera preview."""
        if not self.camera:
            return
        
        ret, frame = self.camera.read_frame()
        if not ret or frame is None:
            return
        
        # Process with MediaPipe if available
        if self.processor and not self.countdown_active:
            import time
            timestamp_ms = int(time.time() * 1000)
            self.processor.process_frame(frame, timestamp_ms)
            
            # Record frame if currently recording
            if self.recording and self.recorder and self.recorder.is_recording():
                hand_landmarks = self.processor.get_hand_landmarks()
                if hand_landmarks:
                    self.recorder.record_frame(hand_landmarks)
                    self.frame_recorded.emit()
            
            # Draw landmarks
            frame = self.processor.draw_landmarks(frame)
        
        # Convert to QPixmap for display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (640, 360))
        
        h, w, ch = frame_resized.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_resized.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        self.preview_label.setPixmap(pixmap)
    
    def _start_recording(self):
        """Start recording process."""
        motion_name = self.name_input.text().strip()
        if not motion_name:
            self.name_input.setFocus()
            self.instruction.setText("⚠️ Please enter a gesture name!")
            self.instruction.setStyleSheet(f"color: {COLORS['RED_BRIGHT']};")
            return
        
        self.start_btn.setEnabled(False)
        self.name_input.setEnabled(False)
        
        # Initialize recorder
        if self.recorder:
            self.recorder.start_recording(motion_name)
        
        # Emit signal
        self.recording_started.emit(motion_name)
        
        # Show countdown
        self.countdown_active = True
        self.countdown_label.show()
        self._countdown(3)
        
        logger.info(f"Recording started: {motion_name}")
    
    def _countdown(self, value):
        """Countdown before recording."""
        if value > 0:
            self.countdown_label.setText(str(value))
            self.countdown_label.setStyleSheet(f"color: {COLORS['RED_BRIGHT']}; background-color: rgba(0, 0, 0, 180); border-radius: 20px; padding: 20px;")
            QTimer.singleShot(1000, lambda: self._countdown(value - 1))
        else:
            self.countdown_label.setText("🔴 RECORDING")
            self.countdown_label.setStyleSheet(f"color: {COLORS['WHITE']}; background-color: rgba(255, 26, 26, 200); border-radius: 20px; padding: 20px;")
            self.countdown_active = False
            self.recording = True
            self.instruction.setText("Perform the gesture NOW!")
            self.instruction.setStyleSheet(f"color: {COLORS['RED_BRIGHT']};")
            
            # Start actual recording sequence
            self._record_sequence()
    
    def _record_sequence(self):
        """Record a single sequence."""
        # Record for 3 seconds
        recording_duration_ms = 3000
        
        def complete_sequence():
            if self.recorder:
                self.recorder.complete_sequence()
            
            self.recorded_count += 1
            self.progress.setValue(self.recorded_count)
            self.sequence_completed.emit()
            
            # Check if we need more repetitions
            if self.recorded_count >= self.max_reps:
                self._complete_recording()
            else:
                self.recording = False
                self.countdown_label.hide()
                self.instruction.setText(f"✅ {self.recorded_count}/{self.max_reps} recorded. Get ready for next one!")
                self.instruction.setStyleSheet(f"color: {COLORS['WHITE']};")
                
                # Wait 2 seconds before next countdown
                QTimer.singleShot(2000, lambda: self._start_next_sequence())
        
        QTimer.singleShot(recording_duration_ms, complete_sequence)
    
    def _start_next_sequence(self):
        """Start countdown for next sequence."""
        self.countdown_active = True
        self.countdown_label.show()
        self._countdown(3)
    
    def _complete_recording(self):
        """Complete all recordings and save."""
        self.recording = False
        self.countdown_label.hide()
        
        self.instruction.setText("💾 Saving recordings...")
        self.instruction.setStyleSheet(f"color: {COLORS['WHITE']};")
        
        # Save recordings
        saved_files = []
        if self.recorder:
            motion_name = self.name_input.text().strip()
            
            # Create gesture-specific directory
            gesture_dir = Path('assets/recordings') / motion_name
            gesture_dir.mkdir(parents=True, exist_ok=True)
            
            # Save each sequence separately
            for i in range(len(self.recorder.recorded_sequences)):
                self.recorder.current_motion_name = f"{motion_name}_seq{i+1}"
                # Temporarily store the sequence
                temp_seq = self.recorder.recorded_sequences[i]
                self.recorder.recorded_sequences = [temp_seq]
                
                # Save to gesture directory
                original_dir = self.recorder.output_dir
                self.recorder.output_dir = gesture_dir
                filepath = self.recorder.save_recording(format='json')
                self.recorder.output_dir = original_dir
                
                if filepath:
                    saved_files.append(filepath)
            
            # Restore all sequences for the signal
            self.recorder.current_motion_name = motion_name
        
        self.countdown_label.show()
        self.countdown_label.setText("✅ COMPLETE!")
        self.countdown_label.setStyleSheet(f"color: {COLORS['WHITE']}; background-color: rgba(0, 200, 0, 200); border-radius: 20px; padding: 20px;")
        self.instruction.setText(f"🎉 {self.recorded_count} sequences saved successfully!")
        self.instruction.setStyleSheet(f"color: {COLORS['WHITE']};")
        
        # Emit completion signal
        self.recording_finished.emit(self.name_input.text().strip(), saved_files)
        
        QTimer.singleShot(2000, self.accept)
        
        logger.info(f"Recording completed: {self.name_input.text()} ({len(saved_files)} files)")
    
    def closeEvent(self, event):
        """Handle dialog close."""
        if hasattr(self, 'preview_timer'):
            self.preview_timer.stop()
        
        if self.recorder and self.recorder.is_recording():
            self.recorder.stop_recording()
        
        super().closeEvent(event)
