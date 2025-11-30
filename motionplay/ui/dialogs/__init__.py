"""
MotionPlay UI Dialogs Package
All dialog windows for the application.
"""

from .recording_dialog import RecordingDialog
from .motion_edit_dialog import MotionEditDialog
from .motion_library_dialog import MotionLibraryDialog
from .profile_manager import ProfileManagerDialog

__all__ = [
    'RecordingDialog',
    'MotionEditDialog',
    'MotionLibraryDialog',
    'ProfileManagerDialog'
]
