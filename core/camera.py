"""
Camera module for MotionPlay
Handles camera capture, frame preprocessing, and FPS calculation.
Pure logic - no UI dependencies.
"""

import cv2
import time
import logging
from typing import Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class Camera:
    """
    Camera capture and frame preprocessing.
    
    Attributes:
        camera_id: OpenCV camera device ID
        width: Frame width in pixels
        height: Frame height in pixels
        fps: Target frames per second
        mirror: Whether to mirror flip the frame horizontally
    """
    
    def __init__(
        self,
        camera_id: int = 0,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
        mirror: bool = True,
        buffer_size: int = 1
    ):
        """
        Initialize camera capture.
        
        Args:
            camera_id: OpenCV camera device ID (default 0)
            width: Frame width in pixels
            height: Frame height in pixels
            fps: Target frames per second
            mirror: Whether to mirror flip frames horizontally
            buffer_size: OpenCV buffer size (1 = minimal latency)
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.target_fps = fps
        self.mirror = mirror
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_opened = False
        
        # FPS tracking
        self._fps_start_time = time.time()
        self._fps_counter = 0
        self._current_fps = 0.0
        
        self._open_camera(buffer_size)
    
    def _open_camera(self, buffer_size: int) -> None:
        """Open the camera device."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open camera {self.camera_id}")
            
            # Configure camera
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
            
            self.is_opened = True
            logger.info(f"Camera {self.camera_id} opened: {self.width}x{self.height} @ {self.target_fps}fps")
            
        except Exception as e:
            logger.error(f"Failed to open camera: {e}")
            raise
    
    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from the camera.
        
        Returns:
            Tuple of (success, frame)
            - success: Whether frame was read successfully
            - frame: BGR frame as numpy array, or None if failed
        """
        if not self.is_opened or self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        
        if not ret or frame is None:
            logger.warning("Failed to read frame from camera")
            return False, None
        
        # Apply mirror flip if enabled
        if self.mirror:
            frame = cv2.flip(frame, 1)
        
        # Update FPS
        self._update_fps()
        
        return True, frame
    
    def _update_fps(self) -> None:
        """Update FPS calculation."""
        self._fps_counter += 1
        elapsed = time.time() - self._fps_start_time
        
        if elapsed >= 1.0:
            self._current_fps = self._fps_counter / elapsed
            self._fps_counter = 0
            self._fps_start_time = time.time()
    
    def get_fps(self) -> float:
        """Get current FPS."""
        return self._current_fps
    
    def release(self) -> None:
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
            self.is_opened = False
            logger.info("Camera released")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure camera is released."""
        self.release()
    
    def __del__(self):
        """Destructor - ensure camera is released."""
        self.release()
