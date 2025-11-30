"""
Action Mapper for MotionPlay
Maps detected motions to keyboard/mouse actions using profiles.
Supports hot-reloading, debouncing, and runtime profile switching.
Pure logic - no UI dependencies.
"""

import yaml
import logging
import time
from typing import Dict, Optional, Any
from pathlib import Path
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class ProfileWatcher(FileSystemEventHandler):
    """File system watcher for profile hot-reloading."""
    
    def __init__(self, action_mapper):
        self.action_mapper = action_mapper
        super().__init__()
    
    def on_modified(self, event):
        """Handle file modification."""
        if event.is_directory:
            return
        
        # Check if it's the current profile file
        if event.src_path.endswith(f"{self.action_mapper.current_profile}.yaml"):
            logger.info(f"Profile file modified, hot-reloading: {self.action_mapper.current_profile}")
            self.action_mapper.reload_profile()


class ActionMapper:
    """
    Maps motion names to keyboard/mouse actions based on loaded profiles.
    Features:
    - Hot-reloading when profile YAML files change
    - Debouncing (0.8s cooldown per gesture)
    - Runtime profile switching
    - pynput for reliable cross-platform input
    
    Attributes:
        profile_dir: Directory containing profile YAML files
        current_profile: Name of the currently loaded profile
        debounce_time: Cooldown period between same gesture (seconds)
    """
    
    # Special key mappings
    SPECIAL_KEYS = {
        'space': Key.space,
        'enter': Key.enter,
        'return': Key.enter,
        'tab': Key.tab,
        'backspace': Key.backspace,
        'delete': Key.delete,
        'esc': Key.esc,
        'escape': Key.esc,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'control': Key.ctrl,
        'alt': Key.alt,
        'cmd': Key.cmd,
        'command': Key.cmd,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right,
        'home': Key.home,
        'end': Key.end,
        'page_up': Key.page_up,
        'pageup': Key.page_up,
        'page_down': Key.page_down,
        'pagedown': Key.page_down,
    }
    
    # Mouse button mappings
    MOUSE_BUTTONS = {
        'left_click': Button.left,
        'right_click': Button.right,
        'middle_click': Button.middle,
    }
    
    def __init__(
        self,
        profile_dir: str = 'profiles',
        initial_profile: str = 'default',
        debounce_time: float = 0.8,
        enable_hot_reload: bool = True
    ):
        """
        Initialize action mapper.
        
        Args:
            profile_dir: Directory containing profile YAML files
            initial_profile: Name of profile to load initially
            debounce_time: Cooldown time between same gesture (seconds)
            enable_hot_reload: Enable file watching for hot-reload
        """
        self.profile_dir = Path(profile_dir)
        self.current_profile: Optional[str] = None
        self.mappings: Dict[str, str] = {}
        self.debounce_time = debounce_time
        
        # Debounce tracking: motion_name -> last_trigger_time
        self.last_trigger_times: Dict[str, float] = {}
        
        # Controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
        # Hot-reload watcher
        self.observer: Optional[Observer] = None
        self.enable_hot_reload = enable_hot_reload
        
        # Load initial profile
        self.load_profile(initial_profile)
        
        # Start file watcher if enabled
        if self.enable_hot_reload:
            self._start_file_watcher()
        
        logger.info(f"ActionMapper initialized (profile: {initial_profile}, debounce: {debounce_time}s)")
    
    def load_profile(self, profile_name: str) -> bool:
        """
        Load a profile from YAML file (v3: simplified format with backward compatibility).
        
        Args:
            profile_name: Name of profile (without .yaml extension)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        profile_path = self.profile_dir / f"{profile_name}.yaml"
        
        if not profile_path.exists():
            logger.error(f"Profile not found: {profile_path}")
            return False
        
        try:
            with open(profile_path, 'r') as f:
                profile_data = yaml.safe_load(f)
            
            mappings_data = profile_data.get('mappings', [])
            
            # v3: Convert to motion -> control mapping with backward compatibility
            self.mappings = {}
            
            if isinstance(mappings_data, list):
                # Check if v3 format (has 'motion' field) or v2 format (has 'motion_id' field)
                for mapping in mappings_data:
                    if 'motion' in mapping:
                        # v3 format: {name, control, motion}
                        motion = mapping.get('motion', '')
                        control = mapping.get('control', '')
                        
                        if motion and control:
                            self.mappings[motion] = control
                    elif 'motion_id' in mapping:
                        # v2 format: {display_name, control, motion_id}
                        motion_id = mapping.get('motion_id', '')
                        control = mapping.get('control', '')
                        
                        if motion_id and control:
                            # Extract motion name from motion_id (e.g., "static/hadoken" -> "hadoken")
                            motion = motion_id.split('/')[-1]
                            self.mappings[motion] = control
                            # Also keep full motion_id for backward compatibility
                            self.mappings[motion_id] = control
            elif isinstance(mappings_data, dict):
                # Old dict format: motion_name -> control
                for motion, control in mappings_data.items():
                    self.mappings[motion] = control
            
            self.current_profile = profile_name
            
            logger.info(f"✓ Profile loaded: {profile_name} ({len(self.mappings)} mappings)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load profile {profile_name}: {e}")
            return False
    
    def switch_profile(self, profile_name: str) -> bool:
        """FINAL CHANGE: Instantly switch to a different profile (for real-time profile manager).
        
        Args:
            profile_name: Name of profile (without .yaml extension)
            
        Returns:
            True if switched successfully, False otherwise
        """
        if self.load_profile(profile_name):
            # Clear debounce on profile switch for immediate response
            self.clear_debounce()
            logger.info(f"⚡ Profile switched instantly: {profile_name}")
            return True
        return False
    
    def reload_profile(self) -> bool:
        """
        Reload the current profile (hot-reload).
        
        Returns:
            True if reloaded successfully, False otherwise
        """
        if self.current_profile:
            return self.load_profile(self.current_profile)
        return False
    
    def get_action(self, motion_name: str) -> Optional[str]:
        """
        Get the mapped action for a motion.
        
        Args:
            motion_name: Name of the detected motion
            
        Returns:
            Action string (key/mouse action) or None if not mapped
        """
        # Case-insensitive lookup
        motion_key = motion_name.lower()
        
        for key, value in self.mappings.items():
            if key.lower() == motion_key:
                return value
        
        return None
    
    def trigger_action(self, motion_name: str) -> bool:
        """
        Trigger action for a motion with debouncing.
        Main entry point for gesture detection -> action execution.
        
        Args:
            motion_name: Name of the detected motion
            
        Returns:
            True if action executed, False if debounced or failed
        """
        # Check debounce
        if not self._check_debounce(motion_name):
            logger.debug(f"Motion debounced: {motion_name}")
            return False
        
        # Execute the action
        success = self.execute_action(motion_name)
        
        if success:
            # Update last trigger time
            self.last_trigger_times[motion_name] = time.time()
        
        return success
    
    def execute_action(self, motion_name: str) -> bool:
        """
        Execute the action mapped to a motion (without debounce check).
        
        Args:
            motion_name: Name of the detected motion
            
        Returns:
            True if action executed successfully, False otherwise
        """
        action = self.get_action(motion_name)
        
        if not action:
            logger.debug(f"No action mapped for motion: {motion_name}")
            return False
        
        try:
            # Parse action type
            action_lower = action.lower()
            
            # Mouse actions
            if action_lower in self.MOUSE_BUTTONS:
                self._execute_mouse_click(self.MOUSE_BUTTONS[action_lower])
                logger.info(f"⚡ Executed: {motion_name} → {action}")
                return True
            
            # Special keys
            if action_lower in self.SPECIAL_KEYS:
                self._execute_key_press(self.SPECIAL_KEYS[action_lower])
                logger.info(f"⚡ Executed: {motion_name} → {action}")
                return True
            
            # Regular character/string
            if len(action) == 1:
                # Single character
                self._execute_key_press(action)
                logger.info(f"⚡ Executed: {motion_name} → {action}")
                return True
            else:
                # Type string
                self.keyboard.type(action)
                logger.info(f"⚡ Executed: {motion_name} → {action}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to execute action '{action}' for motion '{motion_name}': {e}")
            return False
    
    def _check_debounce(self, motion_name: str) -> bool:
        """
        Check if motion should be debounced.
        
        Args:
            motion_name: Name of the motion
            
        Returns:
            True if motion can be triggered, False if still in cooldown
        """
        current_time = time.time()
        last_time = self.last_trigger_times.get(motion_name, 0)
        
        return (current_time - last_time) >= self.debounce_time
    
    def _execute_key_press(self, key) -> None:
        """
        Execute a key press.
        
        Args:
            key: pynput Key object or character string
        """
        self.keyboard.press(key)
        self.keyboard.release(key)
    
    def _execute_mouse_click(self, button: Button) -> None:
        """
        Execute a mouse click.
        
        Args:
            button: pynput mouse Button
        """
        self.mouse.click(button)
    
    def get_all_mappings(self) -> Dict[str, str]:
        """
        Get all current mappings.
        
        Returns:
            Dict of motion -> action mappings
        """
        return self.mappings.copy()
    
    def get_profile_name(self) -> Optional[str]:
        """Get the current profile name."""
        return self.current_profile
    
    def list_available_profiles(self) -> list:
        """
        List all available profile files.
        
        Returns:
            List of profile names (without .yaml extension)
        """
        if not self.profile_dir.exists():
            return []
        
        profiles = []
        for path in self.profile_dir.glob("*.yaml"):
            profiles.append(path.stem)
        
        return sorted(profiles)
    
    def _start_file_watcher(self) -> None:
        """Start file system watcher for hot-reload."""
        if not self.profile_dir.exists():
            logger.warning(f"Profile directory not found: {self.profile_dir}")
            return
        
        try:
            self.observer = Observer()
            event_handler = ProfileWatcher(self)
            self.observer.schedule(event_handler, str(self.profile_dir), recursive=False)
            self.observer.start()
            logger.info("Profile hot-reload watcher started")
        except Exception as e:
            logger.error(f"Failed to start file watcher: {e}")
    
    def stop_watcher(self) -> None:
        """Stop file system watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Profile watcher stopped")
    
    def set_debounce_time(self, debounce_time: float) -> None:
        """
        Set debounce time.
        
        Args:
            debounce_time: New debounce time in seconds
        """
        self.debounce_time = debounce_time
        logger.info(f"Debounce time set to {debounce_time}s")
    
    def clear_debounce(self, motion_name: Optional[str] = None) -> None:
        """
        Clear debounce timer for a motion or all motions.
        
        Args:
            motion_name: Motion to clear, or None to clear all
        """
        if motion_name:
            self.last_trigger_times.pop(motion_name, None)
        else:
            self.last_trigger_times.clear()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.stop_watcher()
