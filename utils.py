"""Utility functions for the Instagram Helper."""

import logging
from datetime import datetime
from pathlib import Path

# --- Logging Configuration ---
LOG_LEVEL = logging.DEBUG
LOG_FORMAT_CONSOLE = "[%(levelname)s] %(message)s"
LOG_FORMAT_FILE = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    name: str = __name__,
    log_level: int = LOG_LEVEL,
    log_dir: Path | None = None,
) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: The name for the logger.
        log_level: The logging level to set.
        log_dir: Optional directory to save log files.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False  # Prevent duplicate logs in parent loggers

    # Clear existing handlers to avoid duplicate output
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT_CONSOLE))
    logger.addHandler(console_handler)

    # File Handler (optional)
    if log_dir:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.log"

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(LOG_FORMAT_FILE, datefmt=LOG_DATE_FORMAT)
            )
            logger.addHandler(file_handler)
        except OSError as e:
            logger.error(f"Failed to set up file logging in {log_dir}: {e}")

    return logger
