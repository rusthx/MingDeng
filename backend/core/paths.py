"""
Path helpers for locating writable data directories.
"""

import os
from pathlib import Path


def get_data_dir() -> Path:
    """
    Return the base data directory.
    Uses MINGDENG_DATA_DIR when provided (set by Tauri), otherwise defaults to ./data.
    """
    env_dir = os.environ.get("MINGDENG_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path("data")
