"""Utility functions for the Instagram Helper."""

import logging
import os
from datetime import UTC, datetime
from pathlib import Path


def get_user_agent() -> str:
    """Returns a reliable Chromium User-Agent string."""
    return (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )


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

    # Get log level from environment
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

    # File Handler (optional)
    if log_dir:
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / f"{datetime.now(UTC).strftime('%d-%m-%Y')}.log"

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(file_handler)

        except OSError as e:
            logger.error(f"Failed to set up file logging in {log_dir}: {e}")

    return logger
