"""
Motion Recorder for MotionPlay
Records motion sequences and saves them for training.
Includes normalization and resampling for MediaPipe Model Maker compatibility.
Pure logic - no UI dependencies.
"""

import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from scipy import interpolate

logger = logging.getLogger(__name__)


class MotionRecorder:
    """
    Records motion sequences from hand/pose landmarks.
    Saves recordings as JSON with normalization and resampling for training.
    
    Features:
    - Landmark normalization (relative to wrist)
    - Temporal resampling to fixed length
    - MediaPipe Model Maker compatible format
    
    Attributes:
        output_dir: Directory to save recordings
        target_frames: Target number of frames after resampling
        recording: Whether currently recording
    """
    
    # MediaPipe hand landmark indices
    WRIST_INDEX = 0
    NUM_HAND_LANDMARKS = 21
    
    def __init__(
        self,
        output_dir: str = 'assets/recordings',
        target_frames: int = 60,
        min_frames: int = 15,
        normalize: bool = True
    ):
        """
        Initialize motion recorder.
        
        Args:
            output_dir: Directory to save recordings
            target_frames: Target number of frames after resampling
            min_frames: Minimum frames for valid recording
            normalize: Whether to normalize landmarks relative to wrist
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.target_frames = target_frames
        self.min_frames = min_frames
        self.normalize = normalize
        
        # Recording state
        self.recording = False
        self.current_motion_name: Optional[str] = None
        self.recorded_frames: List[Dict[str, Any]] = []
        self.recorded_sequences: List[List[Dict[str, Any]]] = []
        
        logger.info(f"MotionRecorder initialized (output: {output_dir}, target_frames: {target_frames})")
    
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
            True if frame recorded, False otherwise
        """
        if not self.recording:
            return False
        
        if not hand_landmarks:
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
    
    def _normalize_landmarks(self, landmarks: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """
        Normalize landmarks relative to wrist position.
        
        Args:
            landmarks: List of (x, y, z) tuples
            
        Returns:
            Normalized landmarks
        """
        if not landmarks or len(landmarks) < self.NUM_HAND_LANDMARKS:
            return landmarks
        
        # Get wrist position (landmark 0)
        wrist_x, wrist_y, wrist_z = landmarks[self.WRIST_INDEX]
        
        # Normalize all landmarks relative to wrist
        normalized = []
        for x, y, z in landmarks:
            normalized.append((
                x - wrist_x,
                y - wrist_y,
                z - wrist_z
            ))
        
        return normalized
    
    def _resample_sequence(self, sequence: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resample sequence to target number of frames using interpolation.
        
        Args:
            sequence: Original sequence of frames
            
        Returns:
            Resampled sequence
        """
        if len(sequence) == self.target_frames:
            return sequence
        
        if len(sequence) < 2:
            # Can't interpolate, just duplicate frames
            return sequence * self.target_frames
        
        # Extract landmarks for interpolation
        original_indices = np.linspace(0, len(sequence) - 1, len(sequence))
        target_indices = np.linspace(0, len(sequence) - 1, self.target_frames)
        
        resampled_sequence = []
        
        # Get number of hands (assume consistent across sequence)
        num_hands = len(sequence[0]['hands'])
        
        for target_idx in target_indices:
            # Find interpolation weights
            frame_data = {
                'timestamp': datetime.now().isoformat(),
                'hands': []
            }
            
            for hand_idx in range(num_hands):
                # Extract all landmarks for this hand across time
                landmarks_over_time = []
                handedness = sequence[0]['hands'][hand_idx]['handedness']
                
                for frame in sequence:
                    if hand_idx < len(frame['hands']):
                        landmarks_over_time.append(frame['hands'][hand_idx]['landmarks'])
                
                # Interpolate each landmark coordinate
                if landmarks_over_time:
                    num_landmarks = len(landmarks_over_time[0])
                    interpolated_landmarks = []
                    
                    for lm_idx in range(num_landmarks):
                        # Get x, y, z for this landmark across all frames
                        x_values = [lms[lm_idx][0] for lms in landmarks_over_time]
                        y_values = [lms[lm_idx][1] for lms in landmarks_over_time]
                        z_values = [lms[lm_idx][2] for lms in landmarks_over_time]
                        
                        # Interpolate
                        x_interp = np.interp(target_idx, original_indices, x_values)
                        y_interp = np.interp(target_idx, original_indices, y_values)
                        z_interp = np.interp(target_idx, original_indices, z_values)
                        
                        interpolated_landmarks.append((float(x_interp), float(y_interp), float(z_interp)))
                    
                    frame_data['hands'].append({
                        'handedness': handedness,
                        'landmarks': interpolated_landmarks,
                        'score': 1.0
                    })
            
            resampled_sequence.append(frame_data)
        
        return resampled_sequence
    
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
        """Save recording as JSON in MediaPipe Model Maker compatible format."""
        processed_sequences = []
        
        for sequence in self.recorded_sequences:
            # Resample to target frames
            resampled = self._resample_sequence(sequence)
            
            # Normalize landmarks if enabled
            if self.normalize:
                for frame in resampled:
                    for hand in frame['hands']:
                        hand['landmarks'] = self._normalize_landmarks(hand['landmarks'])
            
            processed_sequences.append(resampled)
        
        # MediaPipe Model Maker format
        data = {
            'gesture_name': self.current_motion_name,
            'num_sequences': len(processed_sequences),
            'target_frames': self.target_frames,
            'normalized': self.normalize,
            'sequences': processed_sequences,
            'metadata': {
                'recorded_at': datetime.now().isoformat(),
                'num_landmarks_per_hand': self.NUM_HAND_LANDMARKS,
                'format_version': '1.0'
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
