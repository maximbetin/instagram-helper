"""Utility functions and shared logger configuration."""

import logging
import os

# Logging configuration
LOG_LEVEL = logging.DEBUG  # Changed from logging.INFO to enable verbose mode by default
LOG_FORMAT = "[%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"


def setup_logging(
    name: str | None = None,
    log_dir: str | None = None,
    log_level: int | None = None,
) -> logging.Logger:
    """
    Configure and return a logger instance with consistent formatting.

    Args:
        name: Logger name (optional)
        log_dir: Directory path for file logging (optional)
        log_level: Logging level to apply (optional, defaults to LOG_LEVEL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    effective_level = log_level if log_level is not None else LOG_LEVEL
    logger.setLevel(effective_level)

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(effective_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))
    logger.addHandler(console_handler)

    # Add file logging if directory is specified
    if log_dir:
        try:
            os.makedirs(log_dir, exist_ok=True)

            from datetime import datetime

            log_filename = f"{datetime.now().strftime('%d-%m-%Y')}.log"
            log_filepath = os.path.join(log_dir, log_filename)

            # File formatter with more detailed information
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
            file_handler.setLevel(effective_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            logger.info(f"File logging enabled. Log file: {log_filepath}")
        except (OSError, ValueError) as e:
            logger.warning(f"Failed to setup file logging: {e}")

    return logger
