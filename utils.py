"""Utility functions and shared logger configuration."""

import logging
import os
from datetime import datetime
from typing import Optional

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"


def setup_logging(
    name: Optional[str] = None,
    log_dir: Optional[str] = None,
    log_level: Optional[int] = None,
) -> logging.Logger:
    """
    Configure and return a logger instance with consistent formatting.

    Args:
        name: Logger name (optional)
        log_dir: Directory path for file logging (optional). If provided, logs will be written to both console and file.
        log_level: Logging level to apply to the logger and its handlers (optional). If not provided, defaults to LOG_LEVEL.

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name or __name__)

    # Determine effective level
    effective_level = log_level if log_level is not None else LOG_LEVEL
    logger.setLevel(effective_level)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    console_formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(effective_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # Add file logging if directory is specified
    if log_dir:
        try:
            # Create log directory if it doesn't exist
            os.makedirs(log_dir, exist_ok=True)

            # Generate log filename with current date
            log_filename = f"{datetime.now().strftime('%d-%m-%Y')}.log"
            log_filepath = os.path.join(log_dir, log_filename)

            # File formatter with more detailed information
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            # File handler
            file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
            file_handler.setLevel(effective_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            logger.info(f"File logging enabled. Log file: {log_filepath}")
        except (OSError, ValueError) as e:
            logger.warning(f"Failed to setup file logging: {e}")

    return logger
