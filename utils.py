"""Utility functions for the Instagram Helper."""

import logging
import os
from datetime import datetime
from pathlib import Path

from fake_useragent import UserAgent

# --- User-Agent ---
try:
    ua: UserAgent | None = UserAgent(platforms="pc", browsers=["chrome", "edge"])
except Exception:
    ua = None


def get_user_agent() -> str:
    """Returns a realistic User-Agent string."""
    return (
        ua.random
        if ua
        else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    )


# --- Logging Configuration ---
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)
LOG_FORMAT_CONSOLE = "[%(levelname)s] %(message)s"
LOG_FORMAT_FILE = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    name: str = __name__,
    log_dir: Path | None = None,
) -> logging.Logger:
    """Configure and return a logger instance.

    Args:
        name: The name for the logger.
        log_dir: Optional directory to save log files.

    Returns:
        A configured logging.Logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
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
