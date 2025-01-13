import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)

def sanitize_filename(title: str) -> str:
    """Sanitize a string to be used as a filename"""
    return "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in title)

def ensure_dir(path: Union[str, Path]) -> Path:
    """Ensure a directory exists and return its Path object"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_size(file_path: Union[str, Path]) -> str:
    """Get human-readable file size"""
    size = Path(file_path).stat().st_size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB" 