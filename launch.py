#!/usr/bin/env python3
"""
MotionPlay Quick Launcher
Checks dependencies and starts the application.
"""

import sys
import subprocess
import argparse
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


def check_models(skip_check: bool = False):
    """Check if MediaPipe models exist"""
    if skip_check:
        print("⏭️  Skipping model check (offline mode)")
        return True, []
    
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
            print(f"⚠️  {model} - Will auto-download")
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
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='MotionPlay - Pro Gaming Gesture Recognition System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch.py                  # Normal launch with auto-download
  python launch.py --download-models  # Force re-download models
  python launch.py --offline        # Skip download checks (air-gapped)
        """
    )
    parser.add_argument(
        '--download-models',
        action='store_true',
        help='Force re-download MediaPipe models even if they exist'
    )
    parser.add_argument(
        '--offline',
        action='store_true',
        help='Skip model download checks (for air-gapped systems)'
    )
    parser.add_argument(
        '--skip-checks',
        action='store_true',
        help='Skip dependency and model checks (advanced users)'
    )
    
    args = parser.parse_args()
    
    # Handle force model download
    if args.download_models:
        print("=" * 60)
        print("MotionPlay Model Downloader")
        print("=" * 60)
        print()
        
        try:
            # Import and use model_manager
            from core import model_manager
            model_manager.ensure_models_exist(force_download=True)
            print("\n✅ Model download complete!")
            return 0
        except Exception as e:
            print(f"\n❌ Model download failed: {e}")
            return 1
    
    print("=" * 60)
    print("MotionPlay Quick Launcher")
    print("=" * 60)
    print()
    
    if args.offline:
        print("🔒 Offline mode enabled - skipping auto-download")
        print()
    
    if not args.skip_checks:
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
        models_ok, missing_models = check_models(skip_check=args.offline)
        print()
        
        if not models_ok and not args.offline:
            print("📦 Models will be auto-downloaded on first run")
            print()
        
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
    
    # Launch main.py with offline flag if specified
    launch_args = [sys.executable, 'main.py']
    if args.offline:
        launch_args.append('--offline')
    
    try:
        subprocess.run(launch_args)
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
