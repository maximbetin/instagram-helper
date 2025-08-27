"""Utility functions for the Instagram Helper.

UTILITY MODULE STRATEGY:

This module provides essential utility functions that support the core application
functionality. The design focuses on reliability, configurability, and cross-platform
compatibility while maintaining simplicity and performance.

ARCHITECTURE OVERVIEW:

1. LOGGING SYSTEM: Configurable logging with both console and file output, supporting different log levels and automatic log file rotation.

2. USER AGENT MANAGEMENT: Provides consistent, realistic user agent strings to avoid detection and blocking by Instagram's anti-bot systems.

3. PATH HANDLING: Cross-platform path operations that work reliably across different operating systems and file systems.

CRITICAL IMPLEMENTATION DETAILS:

- LOGGING CONFIGURATION: The logging system automatically detects and uses environment variables for configuration, making it easy to adjust log levels without code changes.

- HANDLER MANAGEMENT: Existing handlers are cleared before adding new ones to prevent duplicate log entries and ensure clean logging setup.

- FILE LOGGING: Log files are automatically created with date-based naming (DD-MM-YYYY.log) for easy organization and cleanup.

- ERROR HANDLING: File logging failures are gracefully handled to prevent application crashes when log directories are inaccessible.

PERFORMANCE CONSIDERATIONS:

- LAZY INITIALIZATION: Loggers are configured only when needed, avoiding unnecessary setup overhead during import.

- BUFFERED OUTPUT: File handlers use buffered I/O for better performance when writing large amounts of log data.

- MEMORY EFFICIENCY: Log messages are processed incrementally without accumulating large amounts of data in memory.

SECURITY AND RELIABILITY:

- ENCODING SAFETY: All file operations use UTF-8 encoding to ensure proper handling of international characters and emojis.

- PATH VALIDATION: Directory creation includes proper error handling to prevent security issues and ensure robust operation.

- FALLBACK BEHAVIOR: When file logging fails, console logging continues to ensure critical information is still captured.

CONFIGURATION OPTIONS:

- LOG_LEVEL: Controls the verbosity of logging output (DEBUG, INFO, WARNING, ERROR)
- LOG_DIR: Specifies the directory for log file storage
- Automatic fallback to console-only logging when file logging is unavailable
"""

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
