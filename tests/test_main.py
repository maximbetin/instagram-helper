"""Tests for main functionality."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from browser_manager import setup_browser
from instagram_scraper import (
    extract_post_data,
    get_account_post_urls,
    get_post_caption,
    get_post_date,
    process_account,
)
from report_generator import generate_html_report

# Mock data for testing
MOCK_POST_DATA = {
    "url": "https://www.instagram.com/p/123/",
    "account": "test_account",
    "caption": "Test post caption",
    "date_posted": datetime.now(timezone.utc),
}

MOCK_ACCOUNT_POSTS = [MOCK_POST_DATA]


@pytest.fixture
def mock_page() -> MagicMock:
    """Create a mock page for testing."""
    page = MagicMock()
    page.query_selector_all.return_value = []
    page.query_selector.return_value = None
    page.goto.return_value = None
    return page


@pytest.fixture
def mock_browser() -> MagicMock:
    """Create a mock browser for testing."""
    browser = MagicMock()
    context = MagicMock()
    page = MagicMock()
    context.pages = [page]
    browser.contexts = [context]
    return browser


@pytest.fixture
def mock_playwright() -> MagicMock:
    """Create a mock playwright for testing."""
    playwright = MagicMock()
    playwright.chromium.connect_over_cdp.return_value = mock_browser()
    return playwright


def test_get_account_post_urls(mock_page: MagicMock) -> None:
    """Test getting post URLs from an account page."""
    # Mock link elements
    mock_link1 = MagicMock()
    mock_link1.get_attribute.return_value = "/p/123/"
    mock_link2 = MagicMock()
    mock_link2.get_attribute.return_value = "/reel/456/"
    mock_link3 = MagicMock()
    mock_link3.get_attribute.return_value = "/stories/789/"

    mock_page.query_selector_all.return_value = [mock_link1, mock_link2, mock_link3]

    urls = get_account_post_urls(mock_page)

    assert len(urls) == 2
    assert any("p/123" in url for url in urls)
    assert any("reel/456" in url for url in urls)
    assert not any("stories/789" in url for url in urls)


def test_get_post_caption(mock_page: MagicMock) -> None:
    """Test extracting post caption."""
    mock_caption = MagicMock()
    mock_caption.inner_text.return_value = "  Test caption  "
    mock_page.query_selector.return_value = mock_caption

    caption = get_post_caption(mock_page)
    assert caption == "Test caption"


def test_get_post_caption_no_element(mock_page: MagicMock) -> None:
    """Test extracting post caption when no caption element exists."""
    mock_page.query_selector.return_value = None

    caption = get_post_caption(mock_page)
    assert caption == ""


def test_get_post_date(mock_page: MagicMock) -> None:
    """Test extracting post date."""
    mock_time = MagicMock()
    mock_time.get_attribute.return_value = "2024-01-01T12:00:00Z"
    mock_page.query_selector.return_value = mock_time

    date = get_post_date(mock_page)
    assert date is not None
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 1


def test_get_post_date_no_element(mock_page: MagicMock) -> None:
    """Test extracting post date when no time element exists."""
    mock_page.query_selector.return_value = None

    date = get_post_date(mock_page)
    assert date is None


@patch("time.sleep")
def test_extract_post_data_success(mock_sleep: MagicMock, mock_page: MagicMock) -> None:
    """Test successful post data extraction."""
    cutoff_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

    # Mock page.goto to not raise exceptions
    mock_page.goto.return_value = None

    # Mock caption and date elements
    mock_caption = MagicMock()
    mock_caption.inner_text.return_value = "Test caption"
    mock_time = MagicMock()
    mock_time.get_attribute.return_value = "2024-01-01T12:00:00Z"

    # Mock the query_selector calls
    def mock_query_selector(selector: str) -> MagicMock | None:
        if selector == "h1":
            return mock_caption
        elif selector == "time[datetime]":
            return mock_time
        return None

    mock_page.query_selector.side_effect = mock_query_selector

    result = extract_post_data(
        "https://www.instagram.com/p/123/", cutoff_date, "test_account", mock_page
    )

    assert result is not None
    assert result["url"] == "https://www.instagram.com/p/123/"
    assert result["account"] == "test_account"
    assert result["caption"] == "Test caption"


def test_extract_post_data_old_post(mock_page: MagicMock) -> None:
    """Test post data extraction for old posts."""
    cutoff_date = datetime(2024, 1, 2, tzinfo=timezone.utc)

    # Mock caption and date elements
    mock_caption = MagicMock()
    mock_caption.inner_text.return_value = "Test caption"
    mock_time = MagicMock()
    mock_time.get_attribute.return_value = "2024-01-01T12:00:00Z"

    # Mock the query_selector calls
    def mock_query_selector(selector: str) -> MagicMock | None:
        if selector == "h1":
            return mock_caption
        elif selector == "time[datetime]":
            return mock_time
        return None

    mock_page.query_selector.side_effect = mock_query_selector

    result = extract_post_data(
        "https://www.instagram.com/p/123/", cutoff_date, "test_account", mock_page
    )

    assert result is None


def test_process_account_success(mock_page: MagicMock) -> None:
    """Test successful account processing."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    # Mock successful page load and post URLs
    mock_page.goto.return_value = None
    mock_page.query_selector_all.return_value = []

    result = process_account("test_account", mock_page, cutoff_date)

    assert isinstance(result, list)
    mock_page.goto.assert_called_once()


def test_process_account_failure(mock_page: MagicMock) -> None:
    """Test account processing failure."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    # Mock page load failure
    mock_page.goto.side_effect = Exception("Connection error")

    result = process_account("test_account", mock_page, cutoff_date)

    assert result == []


@patch("os.path.exists")
@patch("builtins.open", create=True)
@patch("report_generator.FileSystemLoader")
@patch("report_generator.Environment")
@patch("os.path.basename")
def test_generate_html_report(
    mock_basename: MagicMock,
    mock_env_class: MagicMock,
    mock_loader_class: MagicMock,
    mock_open: MagicMock,
    mock_exists: MagicMock,
) -> None:
    """Test HTML report generation."""
    mock_exists.return_value = True
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    # Mock the Jinja2 environment and template
    mock_basename.return_value = "template.html"
    mock_loader = MagicMock()
    mock_loader_class.return_value = mock_loader
    mock_env = MagicMock()
    mock_template = MagicMock()
    mock_template.render.return_value = "<html>test</html>"
    mock_env.get_template.return_value = mock_template
    mock_env_class.return_value = mock_env

    posts = [MOCK_POST_DATA]
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    result = generate_html_report(posts, cutoff_date, "/tmp", "templates/template.html")

    assert result.endswith(".html")
    mock_file.write.assert_called_once()


@patch("browser_manager.BROWSER_ATTACH_ONLY", False)
@patch("subprocess.Popen")
@patch("time.sleep")
def test_setup_browser(mock_sleep: MagicMock, mock_popen: MagicMock) -> None:
    """Test browser setup."""
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_playwright.chromium.connect_over_cdp.return_value = mock_browser

    result = setup_browser(mock_playwright)

    assert result is not None
    mock_popen.assert_called_once()
    mock_playwright.chromium.connect_over_cdp.assert_called_once()
