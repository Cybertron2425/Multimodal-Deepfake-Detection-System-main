"""
services/file_validator.py

Validates uploaded files against the same rules as the React frontend.
Frontend (DropZone.jsx / api.js):
  ACCEPTED_FILES = { 'image/*': [...], 'video/*': [...], 'audio/*': [...] }
  MAX_FILE_SIZE  = 500 * 1024 * 1024   (500 MB)
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Maps media_type → which config key holds the allowed MIME set
_MIME_CONFIG_KEY = {
    "image": "ALLOWED_IMAGE_TYPES",
    "video": "ALLOWED_VIDEO_TYPES",
    "audio": "ALLOWED_AUDIO_TYPES",
}

# Human-readable format hints per type
_FORMAT_HINTS = {
    "image": "JPG, PNG, WEBP, GIF, BMP",
    "video": "MP4, AVI, MOV, MKV, WEBM",
    "audio": "MP3, WAV, FLAC, OGG, M4A",
}


class FileValidator:
    def __init__(self, config: dict):
        self.config = config

    def validate(self, file_storage, media_type: str) -> Optional[str]:
        """
        Returns an error string on failure, None on success.
        Checks:
          1. media_type is one of image/video/audio
          2. MIME type is in the allowed set for that media type
          3. File size ≤ MAX_CONTENT_LENGTH
        """
        if media_type not in _MIME_CONFIG_KEY:
            return f"Unknown media type '{media_type}'. Must be image, video, or audio."

        # ── MIME check ────────────────────────────────────────────────────────
        content_type = (file_storage.content_type or "").split(";")[0].strip().lower()
        allowed_mimes: set = self.config.get(_MIME_CONFIG_KEY[media_type], set())

        if content_type not in allowed_mimes:
            hint = _FORMAT_HINTS[media_type]
            logger.debug(f"MIME rejected: '{content_type}' not in {allowed_mimes}")
            return (
                f"Invalid file type '{content_type}' for {media_type} analysis. "
                f"Accepted formats: {hint}."
            )

        # ── Size check ────────────────────────────────────────────────────────
        # Seek to end to get size without reading the whole file into RAM
        file_storage.stream.seek(0, 2)   # seek to end
        size_bytes = file_storage.stream.tell()
        file_storage.stream.seek(0)      # rewind

        max_bytes = self.config.get("MAX_CONTENT_LENGTH", 500 * 1024 * 1024)
        if size_bytes > max_bytes:
            max_mb = max_bytes // (1024 * 1024)
            size_mb = size_bytes / (1024 * 1024)
            return (
                f"File too large ({size_mb:.1f} MB). "
                f"Maximum allowed size is {max_mb} MB."
            )

        return None   # all good
