"""
utils/logger.py

Configures structured logging for Flask.
Writes to stdout (always) and to logs/deepscan.log (if LOG_DIR is writable).
"""

import os
import logging
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    log_dir   = app.config.get("LOG_DIR", "logs")

    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Stream handler (stdout)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    stream_handler.setLevel(log_level)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.addHandler(stream_handler)

    # Rotating file handler
    try:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "deepscan.log"),
            maxBytes=10 * 1024 * 1024,   # 10 MB
            backupCount=5,
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(log_level)
        root.addHandler(file_handler)
    except Exception as exc:
        app.logger.warning(f"Could not create log file handler: {exc}")

    # Suppress noisy third-party loggers
    for noisy in ("urllib3", "PIL", "matplotlib"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    app.logger.info(f"Logging initialised at level {logging.getLevelName(log_level)}")
