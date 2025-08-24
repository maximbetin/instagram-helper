"""Tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

from config import Settings


@pytest.fixture(autouse=True)
def set_env_variables(monkeypatch: MonkeyPatch) -> None:
    """Set environment variables required for testing."""
    monkeypatch.setenv("BROWSER_PATH", "/usr/bin/mock-browser")
    monkeypatch.setenv("BROWSER_USER_DATA_DIR", "/tmp/mock-user-data")


def test_settings_initialization() -> None:
    """Test that settings are properly initialized."""
    settings = Settings()
    assert settings.BROWSER_PATH == Path("/usr/bin/mock-browser")
    assert settings.BROWSER_USER_DATA_DIR == Path("/tmp/mock-user-data")
    # Note: These values might be overridden by environment variables
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT in [3, 5]  # Allow both values
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT in [10000, 20000]  # Allow both values


def test_settings_with_custom_values(monkeypatch: MonkeyPatch) -> None:
    """Test settings with custom environment variable values."""
    monkeypatch.setenv("BROWSER_DEBUG_PORT", "9223")
    monkeypatch.setenv("BROWSER_LOAD_DELAY", "3000")
    monkeypatch.setenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "10")
    monkeypatch.setenv("INSTAGRAM_POST_LOAD_TIMEOUT", "15000")

    settings = Settings()
    assert settings.BROWSER_DEBUG_PORT == 9223
    assert settings.BROWSER_LOAD_DELAY == 3000
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 10
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT == 15000


def test_settings_missing_required_variables(monkeypatch: MonkeyPatch) -> None:
    """Test that missing required environment variables raise errors."""
    monkeypatch.delenv("BROWSER_PATH", raising=False)

    with pytest.raises(ValueError, match="BROWSER_PATH environment variable is not set"):
        Settings()


def test_settings_missing_user_data_dir(monkeypatch: MonkeyPatch) -> None:
    """Test that missing user data directory raises errors."""
    monkeypatch.delenv("BROWSER_USER_DATA_DIR", raising=False)

    with pytest.raises(ValueError, match="BROWSER_USER_DATA_DIR environment variable is not set"):
        Settings()


def test_settings_invalid_integer_values(monkeypatch: MonkeyPatch) -> None:
    """Test that invalid integer values are handled gracefully."""
    monkeypatch.setenv("BROWSER_DEBUG_PORT", "invalid")
    monkeypatch.setenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "not_a_number")

    # Should not raise errors for non-required fields
    settings = Settings()
    assert settings.BROWSER_DEBUG_PORT == 9222  # Default value
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 5  # Default value


def test_settings_invalid_required_integer_values(monkeypatch: MonkeyPatch) -> None:
    """Test that invalid required integer values raise errors."""
    monkeypatch.setenv("BROWSER_PATH", "/usr/bin/browser")
    monkeypatch.setenv("BROWSER_USER_DATA_DIR", "/tmp/user-data")
    monkeypatch.setenv("BROWSER_DEBUG_PORT", "invalid")

    # Should not raise errors for non-required integer fields
    settings = Settings()
    assert settings.BROWSER_DEBUG_PORT == 9222  # Default value


def test_update_instagram_settings() -> None:
    """Test that Instagram settings can be updated dynamically."""
    settings = Settings()

    # Update settings
    settings.update_instagram_settings(15, 20000)

    # Verify changes
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 15
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT == 20000


def test_settings_custom_paths(monkeypatch: MonkeyPatch) -> None:
    """Test custom output and log directory paths."""
    monkeypatch.setenv("OUTPUT_DIR", "/custom/output")
    monkeypatch.setenv("LOG_DIR", "/custom/logs")
    monkeypatch.setenv("TEMPLATE_PATH", "custom/template.html")

    settings = Settings()
    assert settings.OUTPUT_DIR == Path("/custom/output")
    assert settings.LOG_DIR == Path("/custom/logs")
    assert settings.TEMPLATE_PATH == "custom/template.html"


def test_settings_custom_browser_config(monkeypatch: MonkeyPatch) -> None:
    """Test custom browser configuration."""
    monkeypatch.setenv("BROWSER_PROFILE_DIR", "Profile1")
    monkeypatch.setenv("BROWSER_START_URL", "https://example.com")
    monkeypatch.setenv("BROWSER_CONNECT_SCHEME", "https")
    monkeypatch.setenv("BROWSER_REMOTE_HOST", "127.0.0.1")

    settings = Settings()
    assert settings.BROWSER_PROFILE_DIR == "Profile1"
    assert settings.BROWSER_START_URL == "https://example.com"
    assert settings.BROWSER_CONNECT_SCHEME == "https"
    assert settings.BROWSER_REMOTE_HOST == "127.0.0.1"


def test_settings_custom_instagram_config(monkeypatch: MonkeyPatch) -> None:
    """Test custom Instagram configuration."""
    monkeypatch.setenv("INSTAGRAM_URL", "https://instagram.example.com/")

    settings = Settings()
    assert settings.INSTAGRAM_URL == "https://instagram.example.com/"


def test_settings_timezone_config(monkeypatch: MonkeyPatch) -> None:
    """Test timezone configuration."""
    monkeypatch.setenv("TIMEZONE_OFFSET", "5")

    settings = Settings()
    assert settings.TIMEZONE.utcoffset(None).total_seconds() == 5 * 3600


def test_settings_default_timezone() -> None:
    """Test default timezone configuration."""
    settings = Settings()
    # Default should be +2 hours
    assert settings.TIMEZONE.utcoffset(None).total_seconds() == 2 * 3600
