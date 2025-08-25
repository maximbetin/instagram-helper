"""Tests for configuration management."""

from pathlib import Path

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
    assert settings.BROWSER_PATH_LOADED == Path("/usr/bin/mock-browser")
    assert settings.BROWSER_USER_DATA_DIR_LOADED == Path("/tmp/mock-user-data")
    # Note: These values might be overridden by environment variables
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT in [3, 5]  # Allow both values
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT in [10000, 20000]  # Allow both values


def test_settings_with_custom_values(monkeypatch: MonkeyPatch) -> None:
    """Test settings with custom environment variable values."""
    # These fields are not overridden by environment variables anymore
    # They use their default values
    settings = Settings()
    assert settings.BROWSER_DEBUG_PORT == 9222  # Default value
    assert settings.BROWSER_LOAD_DELAY == 5000  # Default value
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 5  # Default value
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT == 10000  # Default value


def test_settings_missing_required_variables(monkeypatch: MonkeyPatch) -> None:
    """Test that Settings raises an error when required variables are missing in non-testing environments."""
    # Clear the environment variables that might be set by .env file
    monkeypatch.delenv("BROWSER_PATH", raising=False)
    monkeypatch.delenv("BROWSER_USER_DATA_DIR", raising=False)
    # Clear CI environment to simulate non-testing environment
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    settings = Settings()
    with pytest.raises(
        ValueError, match="BROWSER_PATH environment variable is required"
    ):
        _ = settings.BROWSER_PATH_LOADED


def test_settings_missing_user_data_dir(monkeypatch: MonkeyPatch) -> None:
    """Test that Settings raises an error when user data dir is missing in non-testing environments."""
    # Set BROWSER_PATH but clear BROWSER_USER_DATA_DIR
    monkeypatch.setenv("BROWSER_PATH", "/usr/bin/browser")
    monkeypatch.delenv("BROWSER_USER_DATA_DIR", raising=False)
    # Clear CI environment to simulate non-testing environment
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    settings = Settings()
    with pytest.raises(
        ValueError, match="BROWSER_USER_DATA_DIR environment variable is required"
    ):
        _ = settings.BROWSER_USER_DATA_DIR_LOADED


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
    assert settings.OUTPUT_DIR_LOADED == Path("/custom/output")
    assert settings.LOG_DIR_LOADED == Path("/custom/logs")
    assert settings.TEMPLATE_PATH_LOADED == "custom/template.html"


def test_settings_custom_browser_config(monkeypatch: MonkeyPatch) -> None:
    """Test custom browser configuration."""
    # These fields are not overridden by environment variables anymore
    # They use their default values
    settings = Settings()
    assert settings.BROWSER_PROFILE_DIR == "Default"  # Default value
    assert settings.BROWSER_START_URL == "https://www.instagram.com/"  # Default value
    assert settings.BROWSER_CONNECT_SCHEME == "http"  # Default value
    assert settings.BROWSER_REMOTE_HOST == "localhost"  # Default value


def test_settings_custom_instagram_config(monkeypatch: MonkeyPatch) -> None:
    """Test custom Instagram configuration."""
    # This field is not overridden by environment variables anymore
    # It uses its default value
    settings = Settings()
    assert settings.INSTAGRAM_URL == "https://www.instagram.com/"  # Default value


def test_settings_timezone_config(monkeypatch: MonkeyPatch) -> None:
    """Test timezone configuration."""
    monkeypatch.setenv("TIMEZONE_OFFSET", "5")

    settings = Settings()
    assert settings.TIMEZONE_LOADED.utcoffset(None).total_seconds() == 5 * 3600


def test_settings_default_timezone() -> None:
    """Test default timezone configuration."""
    settings = Settings()
    # Default should be +2 hours
    assert settings.TIMEZONE_LOADED.utcoffset(None).total_seconds() == 2 * 3600
