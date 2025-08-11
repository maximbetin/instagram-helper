"""Tests for utility functions."""

import logging

import pytest

from utils import LOG_DATE_FORMAT, LOG_FORMAT, LOG_LEVEL, setup_logging


@pytest.fixture(autouse=True)
def reset_logging() -> None:
    """Reset logging to a known state before each test."""
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)  # Default level


def test_setup_logging() -> None:
    """Test that the logger is configured correctly."""
    logger = setup_logging("test_logger")
    assert logger.name == "test_logger"
    assert logger.level == LOG_LEVEL

    # Check that the handler is configured correctly
    assert len(logger.handlers) > 0
    handler = logger.handlers[0]
    formatter = handler.formatter
    assert formatter is not None
    assert formatter._fmt == LOG_FORMAT
    assert formatter.datefmt == LOG_DATE_FORMAT


def test_setup_logging_default_name() -> None:
    """Test that the logger gets a default name if none is provided."""
    logger = setup_logging()
    assert logger.name == "utils"  # Module name from utils.py
