"""Tests for browser_manager module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from browser_manager import (
    _launch_local_browser,
    _launch_playwright_chromium,
    setup_browser,
)


@pytest.fixture
def mock_playwright() -> MagicMock:
    """Mock Playwright instance."""
    mock = MagicMock()
    mock.chromium = MagicMock()
    return mock


@pytest.fixture
def mock_browser() -> MagicMock:
    """Mock browser instance."""
    return MagicMock()


@pytest.fixture
def mock_context() -> MagicMock:
    """Mock browser context instance."""
    return MagicMock()


@pytest.fixture
def mock_page() -> MagicMock:
    """Mock browser page instance."""
    return MagicMock()


class TestSetupBrowser:
    """Test the setup_browser function."""

    def test_setup_browser_local_browser_success(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test successful local browser setup."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._launch_local_browser") as mock_launch_local,
            patch(
                "browser_manager._launch_playwright_chromium"
            ) as mock_launch_playwright,
        ):
            mock_launch_local.return_value = mock_browser
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

            result = setup_browser(mock_playwright)

            assert result == mock_browser
            mock_launch_local.assert_called_once_with(mock_playwright, mock_settings)
            mock_launch_playwright.assert_not_called()

    def test_setup_browser_fallback_to_playwright(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test fallback to Playwright when local browser fails."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._launch_local_browser") as mock_launch_local,
            patch(
                "browser_manager._launch_playwright_chromium"
            ) as mock_launch_playwright,
        ):
            mock_launch_local.return_value = None
            mock_launch_playwright.return_value = mock_browser
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

            result = setup_browser(mock_playwright)

            assert result == mock_browser
            mock_launch_local.assert_called_once_with(mock_playwright, mock_settings)
            mock_launch_playwright.assert_called_once_with(
                mock_playwright, mock_settings
            )

    def test_setup_browser_all_attempts_fail(self, mock_playwright: MagicMock) -> None:
        """Test when both local browser and Playwright fail."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._launch_local_browser") as mock_launch_local,
            patch(
                "browser_manager._launch_playwright_chromium"
            ) as mock_launch_playwright,
        ):
            mock_launch_local.return_value = None
            mock_launch_playwright.return_value = None
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

            result = setup_browser(mock_playwright)

            assert result is None
            mock_launch_local.assert_called_once_with(mock_playwright, mock_settings)
            mock_launch_playwright.assert_called_once_with(
                mock_playwright, mock_settings
            )


class TestLaunchLocalBrowser:
    """Test the _launch_local_browser function."""

    def test_launch_local_browser_success(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test successful local browser launch."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._kill_existing_browser_processes"),
            patch("subprocess.Popen") as mock_popen,
            patch("time.sleep"),
            patch.object(mock_playwright, "chromium") as mock_chromium,
        ):
            # Mock the browser path to exist
            mock_browser_path = MagicMock()
            mock_browser_path.exists.return_value = True
            mock_settings.BROWSER_PATH = mock_browser_path
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")
            mock_settings.BROWSER_DEBUG_PORT = 9222
            mock_settings.BROWSER_START_URL = "https://example.com"
            mock_settings.BROWSER_LOAD_DELAY = 5000
            mock_settings.BROWSER_CONNECT_SCHEME = "http"
            mock_settings.BROWSER_REMOTE_HOST = "localhost"

            mock_popen.return_value = MagicMock()

            # Create a mock chromium instance
            mock_chromium = MagicMock()
            mock_chromium.connect_over_cdp.return_value = mock_browser
            mock_playwright.chromium = mock_chromium

            result = _launch_local_browser(mock_playwright, mock_settings)

            assert result == mock_browser
            mock_popen.assert_called_once()

    def test_launch_local_browser_no_browser_path(mock_playwright: MagicMock) -> None:
        """Test local browser launch when no browser path is configured."""
        with patch("browser_manager.settings") as mock_settings:
            mock_settings.BROWSER_PATH = None

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None

    def test_launch_local_browser_path_not_exists(mock_playwright: MagicMock) -> None:
        """Test local browser launch when browser path doesn't exist."""
        with patch("browser_manager.settings") as mock_settings:
            mock_settings.BROWSER_PATH = Path("/nonexistent/browser")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None

    def test_launch_local_browser_connection_refused(
        self, mock_playwright: MagicMock
    ) -> None:
        """Test local browser launch when connection is refused."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._kill_existing_browser_processes"),
            patch("subprocess.Popen") as mock_popen,
            patch("time.sleep"),
        ):
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")
            mock_settings.BROWSER_DEBUG_PORT = 9222
            mock_settings.BROWSER_START_URL = "https://example.com"
            mock_settings.BROWSER_LOAD_DELAY = 5000
            mock_settings.BROWSER_CONNECT_SCHEME = "http"
            mock_settings.BROWSER_REMOTE_HOST = "localhost"

            mock_popen.return_value = MagicMock()
            mock_playwright.chromium.connect_over_cdp.side_effect = Exception(
                "ECONNREFUSED"
            )

            result = _launch_local_browser(mock_playwright, mock_settings)

            assert result is None

    def test_launch_local_browser_other_connection_error(
        self, mock_playwright: MagicMock
    ) -> None:
        """Test local browser launch with other connection errors."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._kill_existing_browser_processes"),
            patch("subprocess.Popen") as mock_popen,
            patch("time.sleep"),
        ):
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")
            mock_settings.BROWSER_DEBUG_PORT = 9222
            mock_settings.BROWSER_START_URL = "https://example.com"
            mock_settings.BROWSER_LOAD_DELAY = 5000
            mock_settings.BROWSER_CONNECT_SCHEME = "http"
            mock_settings.BROWSER_REMOTE_HOST = "localhost"

            mock_popen.return_value = MagicMock()
            mock_playwright.chromium.connect_over_cdp.side_effect = Exception(
                "Other connection error"
            )

            result = _launch_local_browser(mock_playwright, mock_settings)

            assert result is None

    def test_launch_local_browser_subprocess_error(
        self, mock_playwright: MagicMock
    ) -> None:
        """Test local browser launch when subprocess fails."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("browser_manager._kill_existing_browser_processes"),
            patch("subprocess.Popen", side_effect=Exception("Subprocess error")),
        ):
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

            result = _launch_local_browser(mock_playwright, mock_settings)

            assert result is None


def test_launch_playwright_chromium_success(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test successful Playwright Chromium launch."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_playwright.chromium.launch.return_value = mock_browser

        result = _launch_playwright_chromium(mock_playwright, mock_settings)

        assert result == mock_browser
        mock_playwright.chromium.launch.assert_called_once()


def test_launch_playwright_chromium_failure(mock_playwright: MagicMock) -> None:
    """Test Playwright Chromium launch failure."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_playwright.chromium.launch.side_effect = Exception("Launch failed")

        with pytest.raises(Exception, match="Launch failed"):
            _launch_playwright_chromium(mock_playwright, mock_settings)


def test_browser_launch_arguments() -> None:
    """Test that browser launch arguments are correctly formatted."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._kill_existing_browser_processes"),
        patch("subprocess.Popen") as mock_popen,
        patch("time.sleep"),
    ):
        mock_browser_path = MagicMock(spec=Path)
        mock_browser_path.__str__ = MagicMock(return_value="/usr/bin/brave")
        mock_browser_path.exists = MagicMock(return_value=True)
        mock_settings.BROWSER_PATH = mock_browser_path
        mock_user_data_dir = MagicMock(spec=Path)
        mock_user_data_dir.__str__ = MagicMock(return_value="/tmp/user-data")
        mock_user_data_dir.exists = MagicMock(return_value=True)
        mock_settings.BROWSER_USER_DATA_DIR = mock_user_data_dir
        mock_settings.BROWSER_PROFILE_DIR = "Default"
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_settings.BROWSER_START_URL = "https://www.instagram.com/"
        mock_settings.BROWSER_LOAD_DELAY = 5000
        mock_settings.BROWSER_CONNECT_SCHEME = "http"
        mock_settings.BROWSER_REMOTE_HOST = "localhost"

        mock_popen.return_value = MagicMock()
        mock_playwright = MagicMock()
        mock_playwright.chromium.connect_over_cdp.return_value = MagicMock()

        _launch_local_browser(mock_playwright, mock_settings)

        # Check that Popen was called with the correct arguments
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        assert str(mock_settings.BROWSER_PATH) in call_args
        assert (
            f"--remote-debugging-port={mock_settings.BROWSER_DEBUG_PORT}" in call_args
        )
        assert f"--user-data-dir={mock_settings.BROWSER_USER_DATA_DIR}" in call_args
        assert mock_settings.BROWSER_START_URL in call_args


def test_playwright_chromium_launch_arguments() -> None:
    """Test that Playwright Chromium launch arguments are correctly formatted."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_playwright = MagicMock()
        mock_playwright.chromium.launch.return_value = MagicMock()

        _launch_playwright_chromium(mock_playwright, mock_settings)

        # Check that launch was called with the correct arguments
        mock_playwright.chromium.launch.assert_called_once_with(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--no-first-run",
                "--no-default-browser-check",
                f"--remote-debugging-port={mock_settings.BROWSER_DEBUG_PORT}",
            ],
        )
