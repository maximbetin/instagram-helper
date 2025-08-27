"""Tests for browser_manager module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from browser_manager import (
    _connect_over_cdp_with_retry,
    _launch_user_profile_browser,
    setup_browser,
    setup_profile_context_and_page,
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
    mock = MagicMock()
    mock.contexts = [MagicMock()]
    mock.contexts[0].pages = [MagicMock()]
    mock.version.return_value = "Chrome/120.0.0.0"
    return mock


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

    def test_setup_browser_connect_to_existing(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test successful connection to existing browser."""
        with (
            patch("browser_manager._is_port_open") as mock_port_open,
            patch("browser_manager._connect_over_cdp_with_retry") as mock_connect,
            patch("browser_manager._launch_user_profile_browser") as mock_launch,
        ):
            mock_port_open.return_value = True
            mock_connect.return_value = mock_browser

            result = setup_browser(mock_playwright)

            assert result == mock_browser
            mock_port_open.assert_called_once()
            mock_connect.assert_called_once()
            mock_launch.assert_not_called()

    def test_setup_browser_launch_and_connect(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test launching browser and connecting when port is closed."""
        with (
            patch("browser_manager._is_port_open") as mock_port_open,
            patch("browser_manager._connect_over_cdp_with_retry") as mock_connect,
            patch("browser_manager._launch_user_profile_browser") as mock_launch,
        ):
            mock_port_open.return_value = False
            mock_connect.return_value = mock_browser

            result = setup_browser(mock_playwright)

            assert result == mock_browser
            mock_port_open.assert_called_once()
            mock_launch.assert_called_once()
            mock_connect.assert_called_once()

    def test_setup_browser_connection_failed(self, mock_playwright: MagicMock) -> None:
        """Test when connection fails after launching browser."""
        with (
            patch("browser_manager._is_port_open") as mock_port_open,
            patch("browser_manager._connect_over_cdp_with_retry") as mock_connect,
            patch("browser_manager._launch_user_profile_browser"),
        ):
            mock_port_open.return_value = False
            mock_connect.return_value = None

            with pytest.raises(ConnectionError):
                setup_browser(mock_playwright)


class TestLaunchUserProfileBrowser:
    """Test the _launch_user_profile_browser function."""

    def test_launch_user_profile_browser_success(self) -> None:
        """Test successful browser launch."""
        with (
            patch("browser_manager.settings") as mock_settings,
            patch("subprocess.Popen") as mock_popen,
            patch("pathlib.Path.exists") as mock_exists,
        ):
            mock_settings.BROWSER_PATH = Path("/usr/bin/brave")
            mock_settings.BROWSER_USER_DATA_DIR = Path("/tmp/user-data")
            mock_settings.BROWSER_DEBUG_PORT = 9222
            mock_settings.BROWSER_PROFILE_DIR = "Default"
            mock_settings.BROWSER_START_URL = "https://example.com"

            # Mock that the browser path exists
            mock_exists.return_value = True
            mock_popen.return_value = MagicMock()

            result = _launch_user_profile_browser(mock_settings)

            assert result is not None
            mock_popen.assert_called_once()

    def test_launch_user_profile_browser_no_path(self) -> None:
        """Test browser launch when BROWSER_PATH is None."""
        with (
            patch("browser_manager.settings") as mock_settings,
        ):
            mock_settings.BROWSER_PATH = None

            result = _launch_user_profile_browser(mock_settings)

            assert result is None


class TestConnectOverCdpWithRetry:
    """Test the _connect_over_cdp_with_retry function."""

    def test_connect_over_cdp_success(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test successful CDP connection."""
        mock_playwright.chromium.connect_over_cdp.return_value = mock_browser

        result = _connect_over_cdp_with_retry(mock_playwright, "http://localhost:9222")

        assert result == mock_browser
        mock_playwright.chromium.connect_over_cdp.assert_called_once_with(
            "http://localhost:9222"
        )

    def test_connect_over_cdp_failure(self, mock_playwright: MagicMock) -> None:
        """Test CDP connection failure after all attempts."""
        mock_playwright.chromium.connect_over_cdp.side_effect = Exception(
            "Connection failed"
        )

        result = _connect_over_cdp_with_retry(mock_playwright, "http://localhost:9222")

        assert result is None


class TestSetupProfileContextAndPage:
    """Test the setup_profile_context_and_page function."""

    def test_setup_profile_context_and_page_success(
        self,
        mock_playwright: MagicMock,
        mock_browser: MagicMock,
        mock_context: MagicMock,
        mock_page: MagicMock,
    ) -> None:
        """Test successful context and page setup."""
        with (
            patch("browser_manager.setup_browser") as mock_setup_browser,
            patch("browser_manager.settings") as mock_settings,
        ):
            mock_setup_browser.return_value = mock_browser
            mock_browser.contexts = [mock_context]
            # Mock that there are no existing pages, so new_page() will be called
            mock_context.pages = []
            mock_context.new_page.return_value = mock_page
            mock_settings.INSTAGRAM_POST_LOAD_TIMEOUT = 30000

            result = setup_profile_context_and_page(mock_playwright)

            assert result == (mock_browser, mock_context, mock_page)
            mock_context.new_page.assert_called_once()

    def test_setup_profile_context_and_page_no_contexts(
        self, mock_playwright: MagicMock, mock_browser: MagicMock
    ) -> None:
        """Test setup when no contexts are available."""
        with (
            patch("browser_manager.setup_browser") as mock_setup_browser,
            patch("time.sleep"),
        ):
            mock_setup_browser.return_value = mock_browser
            mock_browser.contexts = []

            with pytest.raises(RuntimeError, match="No browser contexts available"):
                setup_profile_context_and_page(mock_playwright)
