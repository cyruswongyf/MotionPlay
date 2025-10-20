#!/usr/bin/env python
"""
MotionPlay - UI Mode Entry Point
Launch the gesture recognition application with graphical interface
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from main_ui import main

if __name__ == "__main__":
    main()
