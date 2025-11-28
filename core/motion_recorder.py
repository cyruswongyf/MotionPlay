"""
Motion Recorder for MotionPlay
Records motion sequences and saves them for training.
Pure logic - no UI dependencies.
"""

import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class MotionRecorder:
    """
    Records motion sequences from hand/pose landmarks.
    Saves recordings as JSON or NumPy files for training.
    
    Attributes:
        output_dir: Directory to save recordings
        max_frames: Maximum frames to record per sequence
        recording: Whether currently recording
    """
    
    def __init__(
        self,
        output_dir: str = 'assets/recordings',
        max_frames: int = 150,
        min_frames: int = 15
    ):
        """
        Initialize motion recorder.
        
        Args:
            output_dir: Directory to save recordings
            max_frames: Maximum frames per sequence
            min_frames: Minimum frames for valid recording
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_frames = max_frames
        self.min_frames = min_frames
        
        # Recording state
        self.recording = False
        self.current_motion_name: Optional[str] = None
        self.recorded_frames: List[Dict[str, Any]] = []
        self.recorded_sequences: List[List[Dict[str, Any]]] = []
        
        logger.info(f"MotionRecorder initialized (output: {output_dir})")
    
    def start_recording(self, motion_name: str) -> None:
        """
        Start recording a new motion sequence.
        
        Args:
            motion_name: Name of the motion being recorded
        """
        self.recording = True
        self.current_motion_name = motion_name
        self.recorded_frames = []
        self.recorded_sequences = []
        
        logger.info(f"Recording started: {motion_name}")
    
    def record_frame(
        self,
        hand_landmarks: List[Any],
        pose_landmarks: Optional[Any] = None
    ) -> bool:
        """
        Record a single frame of motion data.
        
        Args:
            hand_landmarks: List of HandLandmarks from MediaPipeProcessor
            pose_landmarks: Optional PoseLandmarks from MediaPipeProcessor
            
        Returns:
            True if frame recorded, False if max frames reached
        """
        if not self.recording:
            return False
        
        if len(self.recorded_frames) >= self.max_frames:
            logger.warning(f"Max frames ({self.max_frames}) reached")
            return False
        
        # Extract landmark data
        frame_data = {
            'timestamp': datetime.now().isoformat(),
            'hands': []
        }
        
        # Add hand landmarks
        for hand in hand_landmarks:
            frame_data['hands'].append({
                'handedness': hand.handedness,
                'landmarks': hand.landmarks,
                'score': hand.score
            })
        
        # Add pose landmarks if available
        if pose_landmarks:
            frame_data['pose'] = {
                'landmarks': pose_landmarks.landmarks,
                'score': pose_landmarks.score
            }
        
        self.recorded_frames.append(frame_data)
        return True
    
    def complete_sequence(self) -> bool:
        """
        Complete the current recording sequence.
        
        Returns:
            True if sequence is valid and saved, False otherwise
        """
        if not self.recording:
            return False
        
        if len(self.recorded_frames) < self.min_frames:
            logger.warning(f"Sequence too short ({len(self.recorded_frames)} < {self.min_frames})")
            return False
        
        # Save the sequence
        self.recorded_sequences.append(self.recorded_frames.copy())
        self.recorded_frames = []
        
        logger.info(f"Sequence {len(self.recorded_sequences)} completed ({len(self.recorded_frames)} frames)")
        return True
    
    def stop_recording(self) -> None:
        """Stop recording and clear current sequence."""
        self.recording = False
        self.recorded_frames = []
        logger.info("Recording stopped")
    
    def save_recording(
        self,
        motion_name: Optional[str] = None,
        format: str = 'json'
    ) -> Optional[str]:
        """
        Save all recorded sequences to file.
        
        Args:
            motion_name: Name of the motion (uses current_motion_name if None)
            format: Output format ('json' or 'npy')
            
        Returns:
            Path to saved file, or None if failed
        """
        if not self.recorded_sequences:
            logger.warning("No sequences to save")
            return None
        
        motion_name = motion_name or self.current_motion_name
        if not motion_name:
            logger.error("No motion name provided")
            return None
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{motion_name}_{timestamp}.{format}"
        filepath = self.output_dir / filename
        
        try:
            if format == 'json':
                self._save_json(filepath)
            elif format == 'npy':
                self._save_npy(filepath)
            else:
                logger.error(f"Unsupported format: {format}")
                return None
            
            logger.info(f"Recording saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            return None
    
    def _save_json(self, filepath: Path) -> None:
        """Save recording as JSON."""
        data = {
            'motion_name': self.current_motion_name,
            'num_sequences': len(self.recorded_sequences),
            'sequences': self.recorded_sequences,
            'metadata': {
                'max_frames': self.max_frames,
                'min_frames': self.min_frames,
                'recorded_at': datetime.now().isoformat()
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_npy(self, filepath: Path) -> None:
        """Save recording as NumPy array."""
        # Convert sequences to numpy array
        # This assumes all sequences have the same structure
        # You may need to pad sequences to the same length
        
        arrays = []
        for sequence in self.recorded_sequences:
            # Extract landmark coordinates only
            seq_array = []
            for frame in sequence:
                frame_coords = []
                for hand in frame['hands']:
                    for landmark in hand['landmarks']:
                        frame_coords.extend(landmark[:2])  # x, y only
                seq_array.append(frame_coords)
            arrays.append(seq_array)
        
        # Save as numpy array
        np.save(filepath, np.array(arrays, dtype=object))
    
    def get_recorded_count(self) -> int:
        """Get the number of recorded sequences."""
        return len(self.recorded_sequences)
    
    def get_current_frame_count(self) -> int:
        """Get the number of frames in current sequence."""
        return len(self.recorded_frames)
    
    def clear_recordings(self) -> None:
        """Clear all recorded sequences."""
        self.recorded_sequences = []
        self.recorded_frames = []
        logger.info("Recordings cleared")
    
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self.recording
