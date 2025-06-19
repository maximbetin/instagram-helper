"""Utility functions and shared logger configuration."""

import logging
from typing import Optional

# Logging configuration
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(levelname)s] %(message)s'
LOG_DATE_FORMAT = '%H:%M:%S'


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger instance with consistent formatting."""
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )
    return logging.getLogger(name or __name__)


# Create a default logger instance
logger = setup_logging()
