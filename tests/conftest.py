"""Test configuration and fixtures for Instagram Helper."""

import sys
from datetime import timedelta, tzinfo
from unittest.mock import MagicMock

import pytest

# Mock ZoneInfo to avoid timezone data issues during testing


class MockZoneInfo(tzinfo):
    def __init__(self, timezone_str):
        self.timezone_str = timezone_str

    def __str__(self):
        return self.timezone_str

    def __repr__(self):
        return f"MockZoneInfo('{self.timezone_str}')"

    def utcoffset(self, dt):
        """Mock utcoffset method for testing."""
        if self.timezone_str == "Europe/Madrid":
            # Return 2 hours offset for Madrid timezone
            return timedelta(hours=2)
        return timedelta(hours=0)

    def dst(self, dt):
        """Mock dst method for testing."""
        return timedelta(0)

    def tzname(self, dt):
        """Mock tzname method for testing."""
        return self.timezone_str


# Mock the zoneinfo module before importing config
sys.modules["zoneinfo"] = MagicMock()
sys.modules["zoneinfo"].ZoneInfo = MockZoneInfo

# Import config after mocking - this is necessary for testing
# ruff: noqa: E402
import config


@pytest.fixture
def mock_settings():
    """Provide mocked settings for testing."""
    # Access settings through the mocked config
    return config.settings


@pytest.fixture
def temp_output_dir(tmp_path):
    """Provide a temporary output directory for testing."""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def temp_log_dir(tmp_path):
    """Provide a temporary log directory for testing."""
    log_dir = tmp_path / "test_logs"
    log_dir.mkdir()
    return log_dir
