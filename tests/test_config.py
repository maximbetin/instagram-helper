"""Tests for configuration management."""

from pathlib import Path

import pytest
from pytest import MonkeyPatch

from config import Settings


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch: MonkeyPatch) -> None:
    """Set up test environment variables."""
    monkeypatch.setenv("BROWSER_USER_DATA_DIR", "/tmp/mock-user-data")


def test_settings_initialization() -> None:
    """Test that settings are properly initialized."""
    settings = Settings()

    # Test that browser path exists and is valid
    assert settings.BROWSER_PATH is not None
    assert isinstance(settings.BROWSER_PATH, Path)

    # Test that user data directory path exists and is valid
    assert settings.BROWSER_USER_DATA_DIR is not None
    assert isinstance(settings.BROWSER_USER_DATA_DIR, Path)

    # Test other settings
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 3
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT == 20000


def test_settings_with_custom_values(monkeypatch: MonkeyPatch) -> None:
    """Test settings with hardcoded values."""
    # These fields are not overridden by environment variables anymore
    # They use their hardcoded values
    settings = Settings()
    assert settings.BROWSER_DEBUG_PORT == 9222  # Hardcoded value
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 3  # Hardcoded value
    assert settings.INSTAGRAM_POST_LOAD_TIMEOUT == 20000  # Hardcoded value


def test_settings_missing_required_variables(monkeypatch: MonkeyPatch) -> None:
    """Test that Settings works without environment variables."""
    # Clear the environment variables that might be set by .env file
    monkeypatch.delenv("BROWSER_PATH", raising=False)
    monkeypatch.delenv("BROWSER_USER_DATA_DIR", raising=False)
    # Clear CI environment to simulate non-testing environment
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    settings = Settings()
    # Settings should work without environment variables
    assert settings.BROWSER_PATH is not None
    assert settings.BROWSER_USER_DATA_DIR is not None


def test_settings_missing_user_data_dir(monkeypatch: MonkeyPatch) -> None:
    """Test that Settings works without environment variables."""
    # Clear the environment variables that might be set by .env file
    monkeypatch.delenv("BROWSER_PATH", raising=False)
    monkeypatch.delenv("BROWSER_USER_DATA_DIR", raising=False)
    # Clear CI environment to simulate non-testing environment
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    settings = Settings()
    # Settings should work without environment variables
    assert settings.BROWSER_PATH is not None
    assert settings.BROWSER_USER_DATA_DIR is not None


def test_settings_invalid_integer_values(monkeypatch: MonkeyPatch) -> None:
    """Test that integer values use hardcoded defaults."""
    # Clear any environment variables
    monkeypatch.delenv("BROWSER_DEBUG_PORT", raising=False)
    monkeypatch.delenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", raising=False)

    settings = Settings()
    # Settings now use hardcoded values regardless of environment
    assert settings.BROWSER_DEBUG_PORT == 9222  # Hardcoded value
    assert settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT == 3  # Hardcoded value


def test_settings_invalid_required_integer_values(monkeypatch: MonkeyPatch) -> None:
    """Test that integer values use hardcoded defaults."""
    # Clear any environment variables
    monkeypatch.delenv("BROWSER_DEBUG_PORT", raising=False)

    settings = Settings()
    # Settings now use hardcoded values regardless of environment
    assert settings.BROWSER_DEBUG_PORT == 9222  # Hardcoded value


def test_settings_custom_paths(monkeypatch: MonkeyPatch) -> None:
    """Test that path settings use hardcoded values."""
    # Clear any environment variables
    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    monkeypatch.delenv("LOG_DIR", raising=False)
    monkeypatch.setenv("TEMPLATE_PATH", "custom/template.html")

    settings = Settings()

    # Test that output and log directories are valid paths
    assert settings.OUTPUT_DIR is not None
    assert isinstance(settings.OUTPUT_DIR, Path)
    assert settings.LOG_DIR is not None
    assert isinstance(settings.LOG_DIR, Path)

    # Test that both directories point to the same location
    assert settings.OUTPUT_DIR == settings.LOG_DIR


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
    # Clear any environment variables
    monkeypatch.delenv("TIMEZONE_OFFSET", raising=False)

    settings = Settings()
    # Settings now use hardcoded values regardless of environment
    assert str(settings.TIMEZONE) == "Europe/Madrid"


def test_settings_default_timezone() -> None:
    """Test default timezone configuration."""
    settings = Settings()
    # Default should be Europe/Madrid (hardcoded)
    assert str(settings.TIMEZONE) == "Europe/Madrid"
