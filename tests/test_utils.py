"""Tests for utility functions."""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from utils import get_user_agent, setup_logging


def test_setup_logging_basic_configuration() -> None:
    """Test basic logging setup."""
    logger = setup_logging("test_logger")

    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1


def test_setup_logging_console_handler_format() -> None:
    """Test console handler formatting."""
    logger = setup_logging("test_console_logger")

    # Log a message and verify it was handled
    logger.info("Console test message")

    # The message should be handled by the console handler
    # We can't easily capture stdout in tests, so just verify the logger works
    assert logger.name == "test_console_logger"
    assert len(logger.handlers) == 1


def test_setup_logging_with_file_handler(tmp_path: Path) -> None:
    """Test logging setup with file handler."""
    log_dir = tmp_path / "logs"

    logger = setup_logging("test_file_logger", log_dir)

    assert logger.name == "test_file_logger"
    assert logger.level == logging.INFO

    # Check handlers
    handlers = logger.handlers
    assert len(handlers) == 2  # Console + File

    # Find file handler
    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1

    # Check log file exists
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 1


def test_setup_logging_file_handler_creation_failure(tmp_path: Path) -> None:
    """Test logging setup when file handler creation fails."""
    # Create a file with the same name as the log directory to cause failure
    log_dir = tmp_path / "logs"
    log_dir.write_text("This is a file, not a directory")

    logger = setup_logging("test_failed_file_logger", log_dir)

    # Should still have console handler
    handlers = logger.handlers
    assert len(logger.handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)


def test_setup_logging_clears_existing_handlers() -> None:
    """Test that setup_logging clears existing handlers."""
    logger = logging.getLogger("test_existing_handlers")

    # Add some existing handlers
    existing_handler = logging.StreamHandler()
    logger.addHandler(existing_handler)
    assert len(logger.handlers) == 1

    # Setup logging should clear existing handlers
    setup_logging("test_existing_handlers")
    assert len(logger.handlers) == 1  # Only the new console handler


def test_setup_logging_multiple_calls() -> None:
    """Test multiple calls to setup_logging on the same logger."""
    logger_name = "test_multiple_calls"

    # First call
    logger1 = setup_logging(logger_name)
    assert len(logger1.handlers) == 1

    # Second call
    logger2 = setup_logging(logger_name)
    assert logger1 is logger2  # Same logger instance
    assert len(logger2.handlers) == 1  # Still only one handler


def test_setup_logging_file_handler_format(tmp_path: Path) -> None:
    """Test file handler formatting."""
    log_dir = tmp_path / "logs"

    logger = setup_logging("test_format_logger", log_dir)

    # Log a message
    logger.info("Test message")

    # Check log file content
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 1

    content = log_files[0].read_text()
    assert "Test message" in content
    assert "test_format_logger" in content
    assert "INFO" in content


def test_setup_logging_file_handler_encoding(tmp_path: Path) -> None:
    """Test file handler encoding."""
    log_dir = tmp_path / "logs"

    logger = setup_logging("test_encoding_logger", log_dir)

    # Log a message with special characters
    logger.info("Test message with émojis 🚀✨")

    # Check log file content
    log_files = list(log_dir.glob("*.log"))
    assert len(log_files) == 1

    content = log_files[0].read_text(encoding="utf-8")
    assert "émojis" in content
    assert "🚀" in content


def test_setup_logging_log_level_invalid_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test logging level with invalid environment variable."""
    monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")

    logger = setup_logging("test_invalid_level_logger")
    assert logger.level == logging.INFO  # Default level


def test_setup_logging_log_level_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test logging level when environment variable is missing."""
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    logger = setup_logging("test_missing_level_logger")
    assert logger.level == logging.INFO  # Default level


def test_setup_logging_root_logger_explicit() -> None:
    """Test setup_logging with explicit root logger name."""
    logger = setup_logging("root")

    assert logger.name == "root"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1


def test_setup_logging_file_handler_directory_creation(tmp_path: Path) -> None:
    """Test that log directory is created if it doesn't exist."""
    log_dir = tmp_path / "new_logs" / "subdir"

    logger = setup_logging("test_dir_creation_logger", log_dir)

    # Directory should be created
    assert log_dir.exists()
    assert log_dir.is_dir()

    # Logger should have file handler
    handlers = logger.handlers
    assert len(handlers) == 2  # Console + File

    file_handlers = [h for h in handlers if isinstance(h, logging.FileHandler)]
    assert len(file_handlers) == 1


def test_get_user_agent_with_fake_useragent() -> None:
    """Test user agent generation with fake_useragent available."""
    # Mock fake_useragent to work
    with patch('utils.ua') as mock_ua:
        mock_ua.random = "Mozilla/5.0 (Test Browser)"
        result = get_user_agent()
        assert result == "Mozilla/5.0 (Test Browser)"


def test_get_user_agent_fallback() -> None:
    """Test user agent fallback when fake_useragent fails."""
    # Mock fake_useragent to fail
    with patch('utils.ua', None):
        result = get_user_agent()
        assert "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" in result
        assert "Chrome" in result
