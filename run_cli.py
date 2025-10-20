#!/usr/bin/env python
"""
MotionPlay - CLI Mode Entry Point
Launch the command-line version of the gesture recognition application
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from main import main

if __name__ == "__main__":
    main()
