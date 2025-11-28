"""
Action Mapper for MotionPlay
Maps detected motions to keyboard/mouse actions using profiles.
Supports hot-reloading of profiles.
Pure logic - no UI dependencies.
"""

import yaml
import logging
from typing import Dict, Optional, Any
from pathlib import Path
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button

logger = logging.getLogger(__name__)


class ActionMapper:
    """
    Maps motion names to keyboard/mouse actions based on loaded profiles.
    Supports hot-reloading when profile changes.
    
    Attributes:
        profile_dir: Directory containing profile YAML files
        current_profile: Name of the currently loaded profile
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
        initial_profile: str = 'default'
    ):
        """
        Initialize action mapper.
        
        Args:
            profile_dir: Directory containing profile YAML files
            initial_profile: Name of profile to load initially
        """
        self.profile_dir = Path(profile_dir)
        self.current_profile: Optional[str] = None
        self.mappings: Dict[str, str] = {}
        
        # Controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()
        
        # Load initial profile
        self.load_profile(initial_profile)
        
        logger.info(f"ActionMapper initialized with profile: {initial_profile}")
    
    def load_profile(self, profile_name: str) -> bool:
        """
        Load a profile from YAML file.
        
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
            
            self.mappings = profile_data.get('mappings', {})
            self.current_profile = profile_name
            
            logger.info(f"Profile loaded: {profile_name} ({len(self.mappings)} mappings)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load profile {profile_name}: {e}")
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
    
    def execute_action(self, motion_name: str) -> bool:
        """
        Execute the action mapped to a motion.
        
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
                logger.info(f"Executed: {motion_name} → {action}")
                return True
            
            # Special keys
            if action_lower in self.SPECIAL_KEYS:
                self._execute_key_press(self.SPECIAL_KEYS[action_lower])
                logger.info(f"Executed: {motion_name} → {action}")
                return True
            
            # Regular character/string
            if len(action) == 1:
                # Single character
                self._execute_key_press(action)
                logger.info(f"Executed: {motion_name} → {action}")
                return True
            else:
                # Type string
                self.keyboard.type(action)
                logger.info(f"Executed: {motion_name} → {action}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to execute action '{action}' for motion '{motion_name}': {e}")
            return False
    
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
