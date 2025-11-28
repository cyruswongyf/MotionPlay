"""
MotionPlay - Pro Gaming Gesture Recognition
Main entry point with clean architecture and proper lifecycle management.
"""

import sys
import yaml
import time
import signal
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from core import Camera, MediaPipeProcessor, MotionRecognizer, ActionMapper
from core.motion_recorder import MotionRecorder
from ui import MotionPlayMainWindow

# Global flag for graceful shutdown
running = True


def setup_logging(config: dict) -> None:
    """
    Setup logging with file and console handlers.
    
    Args:
        config: Logging configuration dict
    """
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    fmt = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    log_file = log_config.get('file')
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=log_config.get('max_bytes', 10485760),
            backupCount=log_config.get('backup_count', 3)
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(file_handler)


def load_config(config_path: str = 'config.yaml') -> dict:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dict
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default configuration")
        return {
            'camera': {'device_id': 0, 'width': 1280, 'height': 720, 'fps': 30, 'mirror': True},
            'mediapipe': {'num_hands': 2, 'enable_pose': False, 'enable_gestures': True},
            'recognition': {'confidence_threshold': 0.7, 'cooldown_ms': 500},
            'profiles': {'default_profile': 'default', 'profile_dir': 'profiles'},
            'ui': {'window_width': 1400, 'window_height': 820, 'camera_width': 980, 'camera_height': 820},
            'logging': {'level': 'INFO'}
        }


class MotionPlayApp:
    """
    Main application coordinator.
    Manages camera, processing, recognition, and UI lifecycle.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the application.
        
        Args:
            config: Configuration dict
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Components
        self.camera: Camera = None
        self.processor: MediaPipeProcessor = None
        self.recognizer: MotionRecognizer = None
        self.action_mapper: ActionMapper = None
        self.window: MotionPlayMainWindow = None
        
        # State
        self.timestamp_ms = 0
        self.running = False
        
        self._init_components()
        
        self.logger.info("MotionPlay initialized")
    
    def _init_components(self):
        """Initialize core components."""
        # Camera
        cam_config = self.config['camera']
        self.camera = Camera(
            camera_id=cam_config['device_id'],
            width=cam_config['width'],
            height=cam_config['height'],
            fps=cam_config['fps'],
            mirror=cam_config['mirror'],
            buffer_size=cam_config.get('buffer_size', 1)
        )
        
        # MediaPipe
        mp_config = self.config['mediapipe']
        self.processor = MediaPipeProcessor(
            hand_model_path=mp_config.get('hand_model', 'models/hand_landmarker.task'),
            pose_model_path=mp_config.get('pose_model', 'models/pose_landmarker.task'),
            gesture_model_path=mp_config.get('gesture_model', 'models/gesture_recognizer.task'),
            num_hands=mp_config['num_hands'],
            enable_pose=mp_config['enable_pose'],
            enable_gestures=mp_config['enable_gestures']
        )
        
        # Recognizer
        rec_config = self.config['recognition']
        self.recognizer = MotionRecognizer(
            confidence_threshold=rec_config['confidence_threshold'],
            cooldown_ms=rec_config['cooldown_ms']
        )
        
        # Action Mapper
        prof_config = self.config['profiles']
        self.action_mapper = ActionMapper(
            profile_dir=prof_config['profile_dir'],
            initial_profile=prof_config['default_profile']
        )
    
    def run(self, app: QApplication):
        """
        Run the main application loop.
        
        Args:
            app: QApplication instance
        """
        # Create main window
        self.window = MotionPlayMainWindow(self.config)
        self.window.profile_changed.connect(self._on_profile_changed)
        
        # Set available profiles
        profiles = self.action_mapper.list_available_profiles()
        self.window.set_profiles(profiles)
        
        # Setup processing timer
        self.process_timer = QTimer()
        self.process_timer.timeout.connect(self._process_frame)
        self.process_timer.start(33)  # ~30 FPS
        
        self.window.show()
        self.running = True
        
        self.logger.info("Application started")
        
        # Run event loop
        return app.exec()
    
    def _process_frame(self):
        """Process a single frame (called by timer)."""
        if not self.running:
            return
        
        # Read frame
        ret, frame = self.camera.read_frame()
        if not ret or frame is None:
            return
        
        # Process with MediaPipe
        self.timestamp_ms += 33
        self.processor.process_frame(frame, self.timestamp_ms)
        
        # Draw landmarks if enabled
        if self.config['ui']['overlay'].get('show_landmarks', True):
            frame = self.processor.draw_landmarks(frame)
        
        # Update UI
        self.window.update_frame(frame)
        self.window.update_fps(int(self.camera.get_fps()))
        
        # Recognize motion
        gestures = self.processor.get_gestures()
        detection = self.recognizer.recognize_from_gestures(gestures, self.timestamp_ms)
        
        if detection:
            motion = detection['motion']
            confidence = detection['confidence']
            
            # Get mapped action
            action = self.action_mapper.get_action(motion)
            
            if action:
                # Execute action
                self.action_mapper.execute_action(motion)
                
                # Update UI
                self.window.update_motion(motion, action)
                self.window.show_trigger_feedback(motion, action)
                
                self.logger.info(f"Motion detected: {motion} → {action} ({confidence:.2f})")
    
    def _on_profile_changed(self, profile_name: str):
        """Handle profile change."""
        if self.action_mapper.load_profile(profile_name):
            self.logger.info(f"Profile changed: {profile_name}")
    
    def shutdown(self):
        """Graceful shutdown."""
        self.logger.info("Shutting down...")
        
        self.running = False
        
        if hasattr(self, 'process_timer'):
            self.process_timer.stop()
        
        if self.camera:
            self.camera.release()
        
        if self.processor:
            self.processor.release()
        
        self.logger.info("Shutdown complete")


def signal_handler(sig, frame):
    """Handle interrupt signals for graceful shutdown."""
    global running
    running = False
    print("\nShutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Load config
    config = load_config()
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("MotionPlay - Pro Gaming Gesture Recognition")
    logger.info("=" * 60)
    
    try:
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("MotionPlay")
        
        # Create and run app
        motion_app = MotionPlayApp(config)
        exit_code = motion_app.run(app)
        
        # Shutdown
        motion_app.shutdown()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
