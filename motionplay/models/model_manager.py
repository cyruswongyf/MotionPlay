"""
Model Manager for MotionPlay
Handles automatic downloading and validation of MediaPipe models.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

MODEL_URLS: Dict[str, str] = {
    'hand_landmarker.task': 
        'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',
    'pose_landmarker.task': 
        'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/1/pose_landmarker_heavy.task',
    'gesture_recognizer.task': 
        'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task',
}

MODELS_DIR = Path('models')


class ProgressBar:
    """Simple progress bar for downloads without external dependencies."""
    
    def __init__(self, total: int, prefix: str = ''):
        self.total = total
        self.prefix = prefix
        self.current = 0
        
    def update(self, chunk_size: int):
        self.current += chunk_size
        percent = min(100, int(100 * self.current / self.total))
        bar_length = 40
        filled = int(bar_length * percent / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        current_mb = self.current / (1024 * 1024)
        total_mb = self.total / (1024 * 1024)
        
        print(f'\r{self.prefix} [{bar}] {percent}% ({current_mb:.1f}/{total_mb:.1f} MB)', end='', flush=True)
        
        if self.current >= self.total:
            print()


def download_model(url: str, destination: Path, force: bool = False) -> bool:
    """Download a MediaPipe model from official Google Storage."""
    if destination.exists() and not force:
        logger.info(f"Model already exists: {destination.name}")
        return True
    
    try:
        logger.info(f"Downloading {destination.name}...")
        print(f"📥 Downloading {destination.name}...", flush=True)
        
        with urllib.request.urlopen(url) as response:
            file_size = int(response.headers.get('Content-Length', 0))
            
            # Create progress bar
            progress = ProgressBar(file_size, prefix=f"   {destination.name}")
            
            # Download with progress tracking
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            with open(destination, 'wb') as f:
                chunk_size = 8192
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    progress.update(len(chunk))
        
        print(f"✅ Downloaded {destination.name}", flush=True)
        logger.info(f"Successfully downloaded: {destination.name}")
        return True
        
    except urllib.error.URLError as e:
        logger.error(f"Network error downloading {destination.name}: {e}")
        print(f"❌ Network error: {e}", flush=True)
        return False
        
    except Exception as e:
        logger.error(f"Failed to download {destination.name}: {e}")
        print(f"❌ Download failed: {e}", flush=True)
        return False


def check_models_exist(models_dir: Path = MODELS_DIR) -> tuple[bool, List[str]]:
    """
    Check if all required MediaPipe models exist.
    
    Args:
        models_dir: Directory where models should be located
        
    Returns:
        Tuple of (all_exist: bool, missing_models: List[str])
    """
    missing = []
    
    for model_name in MODEL_URLS.keys():
        model_path = models_dir / model_name
        if not model_path.exists():
            missing.append(model_name)
    
    return len(missing) == 0, missing


def ensure_models_exist(
    models_dir: Path = MODELS_DIR,
    force_download: bool = False,
    offline_mode: bool = False
) -> bool:
    """
    Ensure all required MediaPipe models are available.
    Downloads missing models automatically unless in offline mode.
    
    Args:
        models_dir: Directory where models should be located
        force_download: Force re-download even if files exist
        offline_mode: Skip download attempts (for air-gapped systems)
        
    Returns:
        True if all models are available, False otherwise
        
    Raises:
        RuntimeError: If models are missing and cannot be downloaded
    """
    # Ensure models directory exists
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Check which models are missing
    all_exist, missing = check_models_exist(models_dir)
    
    if all_exist and not force_download:
        logger.info("All MediaPipe models are ready")
        return True
    
    if offline_mode:
        if missing:
            error_msg = f"Offline mode: Missing models {missing}. Please download manually."
            logger.error(error_msg)
            print(f"\n❌ {error_msg}\n", flush=True)
            raise RuntimeError(error_msg)
        logger.info("Offline mode: All models present")
        return True
    
    # Download missing or all models (if force)
    models_to_download = MODEL_URLS.keys() if force_download else missing
    
    if models_to_download:
        print(f"\n{'🔄 Re-downloading' if force_download else '📦 Setting up'} MediaPipe models...", flush=True)
        logger.info(f"Downloading {len(models_to_download)} model(s)")
    
    success_count = 0
    for model_name in models_to_download:
        url = MODEL_URLS[model_name]
        destination = models_dir / model_name
        
        if download_model(url, destination, force=force_download):
            success_count += 1
        else:
            logger.warning(f"Failed to download {model_name}")
    
    # Final verification
    all_exist, still_missing = check_models_exist(models_dir)
    
    if all_exist:
        total_size = sum((models_dir / name).stat().st_size for name in MODEL_URLS.keys())
        size_mb = total_size / (1024 * 1024)
        print(f"\n✅ All MediaPipe models ready ({size_mb:.1f} MB total)\n", flush=True)
        logger.info(f"All models ready ({size_mb:.1f} MB)")
        return True
    else:
        error_msg = f"Failed to download required models: {still_missing}"
        logger.error(error_msg)
        print(f"\n❌ {error_msg}\n", flush=True)
        print("💡 Troubleshooting:", flush=True)
        print("   1. Check your internet connection", flush=True)
        print("   2. Download manually from https://developers.google.com/mediapipe", flush=True)
        print("   3. Place .task files in the models/ folder", flush=True)
        print("   4. Use --offline flag to skip auto-download\n", flush=True)
        raise RuntimeError(error_msg)


def get_model_info(models_dir: Path = MODELS_DIR) -> Dict[str, Dict[str, any]]:
    """
    Get information about available models.
    
    Args:
        models_dir: Directory where models are located
        
    Returns:
        Dict mapping model names to info dicts with keys: exists, size_mb, path
    """
    info = {}
    
    for model_name in MODEL_URLS.keys():
        model_path = models_dir / model_name
        exists = model_path.exists()
        
        info[model_name] = {
            'exists': exists,
            'size_mb': model_path.stat().st_size / (1024 * 1024) if exists else 0,
            'path': str(model_path),
            'url': MODEL_URLS[model_name]
        }
    
    return info


if __name__ == '__main__':
    """Standalone model download script."""
    import sys
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    force = '--force' in sys.argv or '-f' in sys.argv
    
    try:
        ensure_models_exist(force_download=force)
        print("✅ Model setup complete!")
        sys.exit(0)
    except RuntimeError as e:
        print(f"\n❌ Model setup failed: {e}")
        sys.exit(1)
