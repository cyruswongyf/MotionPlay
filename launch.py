#!/usr/bin/env python3
"""
MotionPlay Quick Launcher
Checks dependencies and starts the application.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'cv2',
        'mediapipe',
        'yaml',
        'PyQt6',
        'pynput',
        'numpy'
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing.append(package)
    
    return len(missing) == 0, missing


def check_models():
    """Check if MediaPipe models exist"""
    models_dir = Path('models')
    required_models = [
        'hand_landmarker.task',
        'pose_landmarker.task',
        'gesture_recognizer.task'
    ]
    
    missing = []
    for model in required_models:
        path = models_dir / model
        if path.exists():
            print(f"✅ {model}")
        else:
            print(f"❌ {model} - MISSING")
            missing.append(model)
    
    return len(missing) == 0, missing


def check_config():
    """Check if config.yaml exists"""
    if Path('config.yaml').exists():
        print("✅ config.yaml")
        return True
    else:
        print("❌ config.yaml - MISSING")
        return False


def main():
    """Main launcher"""
    print("=" * 60)
    print("MotionPlay Quick Launcher")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    if not check_python_version():
        return 1
    print()
    
    print("Checking dependencies...")
    deps_ok, missing_deps = check_dependencies()
    print()
    
    if not deps_ok:
        print("⚠️  Missing dependencies detected!")
        print("   Install with: pip install -r requirements.txt")
        return 1
    
    print("Checking MediaPipe models...")
    models_ok, missing_models = check_models()
    print()
    
    if not models_ok:
        print("⚠️  Missing MediaPipe models!")
        print("   Download with: python download_models.py")
        return 1
    
    print("Checking configuration...")
    config_ok = check_config()
    print()
    
    if not config_ok:
        print("⚠️  config.yaml not found!")
        return 1
    
    print("=" * 60)
    print("✅ All checks passed!")
    print("=" * 60)
    print()
    print("Starting MotionPlay...")
    print()
    
    # Launch main.py
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
