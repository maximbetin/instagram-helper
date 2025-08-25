"""Tests for browser management functionality."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from browser_manager import setup_browser


@pytest.fixture
def mock_playwright() -> MagicMock:
    """Provides a mock Playwright instance."""
    playwright = MagicMock()
    playwright.start.return_value = playwright
    return playwright


@pytest.fixture
def mock_browser() -> MagicMock:
    """Provides a mock Browser instance."""
    browser = MagicMock()
    browser.contexts = []
    return browser


@pytest.fixture
def mock_context() -> MagicMock:
    """Provides a mock BrowserContext instance."""
    context = MagicMock()
    context.pages = []
    return context


def test_setup_browser_local_browser_success(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test successful local browser setup."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._launch_local_browser", return_value=mock_browser),
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

        result = setup_browser(mock_playwright)

        assert result == mock_browser


def test_setup_browser_fallback_to_playwright(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test fallback to Playwright-managed browser when local browser fails."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._launch_local_browser", return_value=None),
        patch("browser_manager._launch_playwright_chromium", return_value=mock_browser),
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

        result = setup_browser(mock_playwright)

        assert result == mock_browser


def test_setup_browser_all_attempts_fail(mock_playwright: MagicMock) -> None:
    """Test that setup_browser raises ConnectionError when all attempts fail."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._launch_local_browser", return_value=None),
        patch(
            "browser_manager._launch_playwright_chromium",
            side_effect=Exception("Browser launch failed"),
        ),
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

        with pytest.raises(ConnectionError, match="Could not launch any browser"):
            setup_browser(mock_playwright)


def test_launch_local_browser_success(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test successful local browser launch."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._kill_existing_browser_processes"),
        patch("subprocess.Popen") as mock_popen,
        patch("time.sleep"),
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

        from browser_manager import _launch_local_browser

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result == mock_browser
        mock_popen.assert_called_once()


def test_launch_local_browser_no_browser_path(mock_playwright: MagicMock) -> None:
    """Test local browser launch when no browser path is configured."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_PATH = None

        from browser_manager import _launch_local_browser

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None


def test_launch_local_browser_path_not_exists(mock_playwright: MagicMock) -> None:
    """Test local browser launch when browser path doesn't exist."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_PATH = Path("/nonexistent/browser")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

        from browser_manager import _launch_local_browser

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None


def test_launch_local_browser_connection_refused(mock_playwright: MagicMock) -> None:
    """Test local browser launch when connection is refused."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._kill_existing_browser_processes"),
        patch("subprocess.Popen") as mock_popen,
        patch("time.sleep"),
        patch.object(mock_playwright, "chromium") as mock_chromium,
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_settings.BROWSER_START_URL = "https://example.com"
        mock_settings.BROWSER_LOAD_DELAY = 5000
        mock_settings.BROWSER_CONNECT_SCHEME = "http"
        mock_settings.BROWSER_REMOTE_HOST = "localhost"

        mock_popen.return_value = MagicMock()
        mock_chromium.connect_over_cdp.side_effect = Exception("ECONNREFUSED")

        from browser_manager import _launch_local_browser

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None


def test_launch_local_browser_other_connection_error(
    mock_playwright: MagicMock,
) -> None:
    """Test local browser launch with other connection errors."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._kill_existing_browser_processes"),
        patch("subprocess.Popen") as mock_popen,
        patch("time.sleep"),
        patch.object(mock_playwright, "chromium") as mock_chromium,
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_settings.BROWSER_START_URL = "https://example.com"
        mock_settings.BROWSER_LOAD_DELAY = 5000
        mock_settings.BROWSER_CONNECT_SCHEME = "http"
        mock_settings.BROWSER_REMOTE_HOST = "localhost"

        mock_popen.return_value = MagicMock()
        mock_chromium.connect_over_cdp.side_effect = Exception("Other connection error")

        from browser_manager import _launch_local_browser

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None


def test_launch_local_browser_subprocess_error(mock_playwright: MagicMock) -> None:
    """Test local browser launch when subprocess fails."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._kill_existing_browser_processes"),
        patch("subprocess.Popen", side_effect=Exception("Subprocess error")),
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
        mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")

        from browser_manager import _launch_local_browser

        result = _launch_local_browser(mock_playwright, mock_settings)

        assert result is None


def test_launch_playwright_chromium_success(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test successful Playwright Chromium launch."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_playwright.chromium.launch.return_value = mock_browser

        from browser_manager import _launch_playwright_chromium

        result = _launch_playwright_chromium(mock_playwright, mock_settings)

        assert result == mock_browser
        mock_playwright.chromium.launch.assert_called_once()


def test_launch_playwright_chromium_failure(mock_playwright: MagicMock) -> None:
    """Test Playwright Chromium launch failure."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_DEBUG_PORT = 9222
        mock_playwright.chromium.launch.side_effect = Exception("Launch failed")

        from browser_manager import _launch_playwright_chromium

        with pytest.raises(Exception, match="Launch failed"):
            _launch_playwright_chromium(mock_playwright, mock_settings)


def test_kill_existing_browser_processes_brave_linux() -> None:
    """Test killing existing Brave processes on Linux."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("subprocess.run") as mock_run,
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/brave")

        # Import after mocking
        import browser_manager
        browser_manager._kill_existing_browser_processes()

        mock_run.assert_called_once_with(
            ["pkill", "-f", "brave"],
            capture_output=True,
            check=False,
            text=True,
        )


def test_kill_existing_browser_processes_not_brave() -> None:
    """Test that process killing is skipped for non-Brave browsers."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("subprocess.run") as mock_run,
    ):
        mock_settings.BROWSER_PATH = Path("/usr/bin/chrome")

        # Import after mocking
        import browser_manager
        browser_manager._kill_existing_browser_processes()

        mock_run.assert_not_called()


def test_kill_existing_browser_processes_no_browser_path() -> None:
    """Test that process killing is skipped when no browser path is configured."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("subprocess.run") as mock_run,
    ):
        mock_settings.BROWSER_PATH = None

        # Import after mocking
        import browser_manager
        browser_manager._kill_existing_browser_processes()

        mock_run.assert_not_called()


def test_kill_existing_browser_processes_taskkill_not_found() -> None:
    """Test that process killing handles missing taskkill.exe gracefully."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager.os.name", "nt"),  # Windows
        patch(
            "subprocess.run", side_effect=FileNotFoundError("taskkill.exe not found")
        ),
    ):
        mock_settings.BROWSER_PATH = Path(
            "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        )

        # Import after mocking
        import browser_manager
        # Should not raise an exception
        browser_manager._kill_existing_browser_processes()


def test_kill_existing_browser_processes_other_error() -> None:
    """Test that process killing handles other errors gracefully."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager.os.name", "nt"),  # Windows
        patch("subprocess.run", side_effect=Exception("Other error")),
    ):
        mock_settings.BROWSER_PATH = Path(
            "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        )

        # Import after mocking
        import browser_manager
        # Should not raise an exception
        browser_manager._kill_existing_browser_processes()


def test_browser_launch_arguments(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test that browser launch arguments are correctly formatted."""
    with (
        patch("browser_manager.settings") as mock_settings,
        patch("browser_manager._kill_existing_browser_processes"),
        patch("subprocess.Popen") as mock_popen,
        patch("time.sleep"),
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

        # Import after mocking
        import browser_manager
        browser_manager._launch_local_browser(mock_playwright, mock_settings)

        # Check that Popen was called with correct arguments
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]

        assert str(mock_settings.BROWSER_PATH) in call_args
        assert (
            f"--remote-debugging-port={mock_settings.BROWSER_DEBUG_PORT}" in call_args
        )
        assert f"--user-data-dir={mock_settings.BROWSER_USER_DATA_DIR}" in call_args
        assert mock_settings.BROWSER_START_URL in call_args


def test_playwright_chromium_launch_arguments(
    mock_playwright: MagicMock, mock_browser: MagicMock
) -> None:
    """Test that Playwright Chromium launch arguments are correct."""
    with patch("browser_manager.settings") as mock_settings:
        mock_settings.BROWSER_DEBUG_PORT = 9222

        # Import after mocking
        import browser_manager
        browser_manager._launch_playwright_chromium(mock_playwright, mock_settings)

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
                "--remote-debugging-port=9222",
            ],
        )
