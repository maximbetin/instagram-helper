"""Tests for utility functions."""

import logging
from pathlib import Path
from unittest.mock import patch

import pytest

from utils import (
    LOG_DATE_FORMAT,
    LOG_FORMAT_CONSOLE,
    LOG_FORMAT_FILE,
    setup_logging,
)


@pytest.fixture(autouse=True)
def reset_logging_handlers() -> None:
    """Ensure each test starts with a clean slate for logging handlers."""
    # This prevents handlers from accumulating across tests
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    # Also clear handlers for the logger under test if it exists
    test_logger = logging.getLogger("test_logger")
    if test_logger.hasHandlers():
        test_logger.handlers.clear()


def test_setup_logging_basic_configuration() -> None:
    """Test that the logger is configured with the correct name and level."""
    with patch.dict("os.environ", {"LOG_LEVEL": "INFO"}):
        logger = setup_logging(name="test_logger")
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        # Named loggers now propagate to parent loggers to ensure file logging works
        # This was changed to fix the issue where log files were not being written
        assert logger.propagate
        assert len(logger.handlers) == 1  # Should only have console handler


def test_setup_logging_console_handler_format() -> None:
    """Test that the console handler has the correct formatter."""
    logger = setup_logging(name="test_logger")
    console_handler = logger.handlers[0]
    formatter = console_handler.formatter
    assert isinstance(formatter, logging.Formatter)
    assert formatter._fmt == LOG_FORMAT_CONSOLE


def test_setup_logging_with_file_handler(tmp_path: Path) -> None:
    """Test that a file handler is correctly added and configured when a log directory is provided."""
    log_dir = tmp_path / "logs"
    logger = setup_logging(name="test_logger", log_dir=log_dir)

    assert len(logger.handlers) == 2  # Console and file handler

    # Find the file handler
    file_handler = None
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            file_handler = handler
            break

    assert file_handler is not None
    assert log_dir.exists()

    formatter = file_handler.formatter
    assert isinstance(formatter, logging.Formatter)
    assert formatter._fmt == LOG_FORMAT_FILE
    assert formatter.datefmt == LOG_DATE_FORMAT


def test_setup_logging_file_handler_creation_failure(tmp_path: Path) -> None:
    """Test that logger setup does not fail if file handler creation raises an error."""
    # Make the temp directory read-only to trigger a permission error
    log_dir = tmp_path / "readonly"
    log_dir.mkdir()
    log_dir.chmod(0o444)

    # We expect an error to be logged, but not an exception to be raised.
    # We can patch the logger's error method to confirm it's called.
    with patch.object(logging.getLogger("test_logger"), "error") as mock_error:
        logger = setup_logging(name="test_logger", log_dir=log_dir)

        # The logger should still have the console handler
        assert len(logger.handlers) == 1
        mock_error.assert_called_once()
        assert "Failed to set up file logging" in mock_error.call_args[0][0]

    # Clean up the read-only directory
    log_dir.chmod(0o755)
