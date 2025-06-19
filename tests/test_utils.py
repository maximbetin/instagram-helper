import logging
import os
import sys

import pytest

from utils import LOG_DATE_FORMAT, LOG_FORMAT, LOG_LEVEL, setup_logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Reset logging to a known state before each test
@pytest.fixture(autouse=True)
def reset_logging():
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)  # Default level


def test_setup_logging():
    """Test that the logger is configured correctly."""
    logger = setup_logging('test_logger')
    assert logger.name == 'test_logger'
    assert logging.root.level == LOG_LEVEL

    # Check that the handler is configured correctly
    assert len(logging.getLogger().handlers) > 0
    handler = logging.getLogger().handlers[0]
    formatter = handler.formatter
    assert formatter is not None
    assert formatter._fmt == LOG_FORMAT
    assert formatter.datefmt == LOG_DATE_FORMAT


def test_setup_logging_default_name():
    """Test that the logger gets a default name if none is provided."""
    # The default name will be 'utils' because that's where the function is defined.
    logger = setup_logging()
    assert logger.name == 'utils'
