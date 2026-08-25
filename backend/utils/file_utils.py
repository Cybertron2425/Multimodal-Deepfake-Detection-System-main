"""
utils/file_utils.py

Secure file I/O helpers.
Files are saved to a temp path under UPLOAD_FOLDER with a UUID prefix
so concurrent requests never collide.
"""

import os
import uuid
import logging
from pathlib import Path
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


def save_temp_file(file_storage: FileStorage, upload_dir: str, original_filename: str) -> str:
    """
    Save an uploaded FileStorage object to disk under upload_dir.
    Returns the full absolute path of the saved file.

    Uses secure_filename() + UUID prefix to prevent:
      - Path traversal attacks
      - Filename collisions under concurrent load
    """
    safe_name  = secure_filename(original_filename) or "upload"
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    dest_path   = os.path.join(upload_dir, unique_name)

    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(dest_path)

    logger.debug(f"Saved temp file: {dest_path} ({_human_size(os.path.getsize(dest_path))})")
    return dest_path


def delete_file(path: str) -> None:
    """Delete a file, logging but not raising if it is already gone."""
    try:
        os.unlink(path)
        logger.debug(f"Deleted temp file: {path}")
    except FileNotFoundError:
        pass
    except Exception as exc:
        logger.warning(f"Could not delete temp file {path}: {exc}")


def _human_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"
