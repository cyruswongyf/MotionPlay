"""
MotionPlay Models Package
Model management and downloading.
"""

from .model_manager import (
    ensure_models_exist,
    check_models_exist,
    download_model,
    get_model_info,
    MODEL_URLS,
    MODELS_DIR
)

__all__ = [
    'ensure_models_exist',
    'check_models_exist',
    'download_model',
    'get_model_info',
    'MODEL_URLS',
    'MODELS_DIR'
]
