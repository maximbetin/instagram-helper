"""Integration tests for the main function."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from cli import main

# Mock data for testing
MOCK_POST_DATA = {
    "url": "https://www.instagram.com/p/123/",
    "account": "test_account",
    "caption": "Test post caption",
    "date_posted": "01-01-2024",
}


@pytest.fixture
def mock_playwright() -> MagicMock:
    """Create a mock playwright for testing."""
    playwright = MagicMock()
    browser = MagicMock()
    context = MagicMock()
    page = MagicMock()
    context.pages = [page]
    browser.contexts = [context]
    playwright.chromium.connect_over_cdp.return_value = browser
    return playwright


@pytest.fixture
def mock_browser_manager() -> Generator[MagicMock, None, None]:
    """Mock the browser manager module."""
    with patch("cli.setup_browser") as mock_setup:
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_context.pages = [mock_page]
        mock_browser.contexts = [mock_context]
        mock_setup.return_value = mock_browser
        yield mock_setup


@pytest.fixture
def mock_instagram_scraper() -> Generator[MagicMock, None, None]:
    """Mock the instagram scraper module."""
    with patch("cli.process_account") as mock_process:
        mock_process.return_value = [MOCK_POST_DATA]
        yield mock_process


@pytest.fixture
def mock_report_generator() -> Generator[MagicMock, None, None]:
    """Mock the report generator module."""
    with patch("cli.generate_html_report") as mock_generate:
        mock_generate.return_value = "/tmp/test_report.html"
        yield mock_generate


@pytest.fixture
def mock_os_startfile() -> Generator[MagicMock, None, None]:
    """Mock the webbrowser.open function."""
    with patch("cli.webbrowser.open") as mock_webbrowser:
        yield mock_webbrowser


def test_main_success(
    mock_browser_manager: MagicMock,
    mock_instagram_scraper: MagicMock,
    mock_report_generator: MagicMock,
    mock_os_startfile: MagicMock,
) -> None:
    """Test successful main execution."""
    with patch("cli.sync_playwright") as mock_sync_playwright:
        mock_p = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_p

        # Mock command line arguments
        with patch("cli.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.days = 1
            mock_args.accounts = None
            mock_args.output = "/tmp"
            mock_args.log_dir = "/tmp"
            mock_args.no_open = False
            mock_args.verbose = False
            mock_parse_args.return_value = mock_args

            # Mock logging setup
            with patch("cli.setup_logging") as mock_setup_logging:
                mock_logger = MagicMock()
                mock_setup_logging.return_value = mock_logger

                result = main()

                assert result == 0
                mock_browser_manager.assert_called_once_with(mock_p)
                mock_instagram_scraper.assert_called()
                mock_report_generator.assert_called_once()
                mock_os_startfile.assert_called_once_with(
                    "file:///tmp/test_report.html"
                )


def test_main_no_posts(
    mock_browser_manager: MagicMock,
    mock_instagram_scraper: MagicMock,
    mock_report_generator: MagicMock,
) -> None:
    """Test main execution when no posts are found."""
    with patch("cli.sync_playwright") as mock_sync_playwright:
        mock_p = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_p

        # Mock command line arguments
        with patch("cli.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.days = 1
            mock_args.accounts = None
            mock_args.output = "/tmp"
            mock_args.log_dir = "/tmp"
            mock_args.no_open = False
            mock_args.verbose = False
            mock_parse_args.return_value = mock_args

            # Mock logging setup
            with patch("cli.setup_logging") as mock_setup_logging:
                mock_logger = MagicMock()
                mock_setup_logging.return_value = mock_logger

                # Mock no posts found
                mock_instagram_scraper.return_value = []

                result = main()

                assert result == 0
                mock_report_generator.assert_not_called()


def test_main_browser_connection_error() -> None:
    """Test main execution when browser connection fails."""
    with patch("cli.sync_playwright") as mock_sync_playwright:
        mock_p = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_p

        # Mock command line arguments
        with patch("cli.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.days = 1
            mock_args.accounts = None
            mock_args.output = "/tmp"
            mock_args.log_dir = "/tmp"
            mock_args.no_open = False
            mock_args.verbose = False
            mock_parse_args.return_value = mock_args

            # Mock logging setup
            with patch("cli.setup_logging") as mock_setup_logging:
                mock_logger = MagicMock()
                mock_setup_logging.return_value = mock_logger

                # Mock browser connection error
                with patch("cli.setup_browser") as mock_setup_browser:
                    mock_setup_browser.side_effect = Exception("ECONNREFUSED")

                    result = main()

                    assert result == 1
                    mock_logger.error.assert_called()


def test_main_general_error() -> None:
    """Test main execution when a general error occurs."""
    with patch("cli.sync_playwright") as mock_sync_playwright:
        mock_p = MagicMock()
        mock_sync_playwright.return_value.__enter__.return_value = mock_p

        # Mock command line arguments
        with patch("cli.parse_args") as mock_parse_args:
            mock_args = MagicMock()
            mock_args.days = 1
            mock_args.accounts = None
            mock_args.output = "/tmp"
            mock_args.log_dir = "/tmp"
            mock_args.no_open = False
            mock_args.verbose = False
            mock_parse_args.return_value = mock_args

            # Mock logging setup
            with patch("cli.setup_logging") as mock_setup_logging:
                mock_logger = MagicMock()
                mock_setup_logging.return_value = mock_logger

                # Mock general error
                with patch("cli.setup_browser") as mock_setup_browser:
                    mock_setup_browser.side_effect = Exception("General error")

                    result = main()

                    assert result == 1
                    mock_logger.error.assert_called()
