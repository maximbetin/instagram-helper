"""Tests for Instagram scraping functionality."""

from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import settings
from instagram_scraper import InstagramScraper


@pytest.fixture
def mock_page() -> MagicMock:
    """Provides a mock Playwright Page object."""
    page = MagicMock()
    page.query_selector_all.return_value = []
    page.query_selector.return_value = None
    page.goto.return_value = None
    page.set_extra_http_headers.return_value = None
    return page


@pytest.fixture
def scraper(mock_page: MagicMock) -> InstagramScraper:
    """Provides a scraper instance with mocked page."""
    return InstagramScraper(mock_page, settings)


def test_scraper_initialization(mock_page: MagicMock) -> None:
    """Test scraper initialization."""
    scraper = InstagramScraper(mock_page, settings)
    assert scraper.page == mock_page
    assert scraper.settings == settings


def test_get_post_urls_max_posts_limit(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test that post URL collection stops at max posts limit."""
    # Mock the locator and its methods
    mock_locator = MagicMock()
    mock_page.locator.return_value = mock_locator

    # Mock the count method to return a number
    mock_locator.count.return_value = 5

    # Mock the nth method to return mock elements with href attributes
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "/p/post_1/"
    mock_locator.nth.return_value = mock_element

    # Mock wait_for_selector to not raise timeout
    mock_page.wait_for_selector.return_value = None

    # Mock mouse wheel and wait_for_timeout
    mock_page.mouse.wheel.return_value = None
    mock_page.wait_for_timeout.return_value = None

    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    urls = scraper._get_post_urls("test_account", cutoff_date)

    # Should return URLs up to the limit
    max_posts = scraper.settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT
    assert len(urls) <= max_posts


def test_get_post_urls_collects_all_urls(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test that URL collection gathers all available post URLs without date filtering."""
    # Mock the locator and its methods
    mock_locator = MagicMock()
    mock_page.locator.return_value = mock_locator

    # Mock the count method to return 3
    mock_locator.count.return_value = 3

    # Mock the nth method to return mock elements with href attributes
    mock_element = MagicMock()
    mock_element.get_attribute.return_value = "/p/post_1/"
    mock_locator.nth.return_value = mock_element

    # Mock wait_for_selector to not raise timeout
    mock_page.wait_for_selector.return_value = None

    # Mock mouse wheel and wait_for_timeout
    mock_page.mouse.wheel.return_value = None
    mock_page.wait_for_timeout.return_value = None

    cutoff_date = datetime.now(UTC) - timedelta(days=5)
    urls = scraper._get_post_urls("test_account", cutoff_date)

    # Should collect URLs (date filtering happens during processing)
    assert len(urls) > 0


def test_get_post_urls_exception_handling(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test that exceptions in URL collection are handled gracefully."""
    mock_page.query_selector_all.side_effect = Exception("Page error")

    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    urls = scraper._get_post_urls("test_account", cutoff_date)

    assert urls == []


def test_extract_post_data_navigation_failure(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post data extraction when navigation fails."""
    with patch.object(scraper, "_navigate_to_url", return_value=False):
        result = scraper._extract_post_data(
            "https://example.com/p/123/", "test_account", datetime.now(UTC)
        )

        assert result is None


def test_extract_post_data_no_date(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post data extraction when date cannot be determined."""
    with (
        patch.object(scraper, "_navigate_to_url", return_value=True),
        patch.object(scraper, "_get_post_date", return_value=None),
    ):
        result = scraper._extract_post_data(
            "https://example.com/p/123/", "test_account", datetime.now(UTC)
        )

        assert result is None


def test_extract_post_data_old_post(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post data extraction for posts older than cutoff."""
    old_date = datetime.now(UTC) - timedelta(days=10)
    cutoff_date = datetime.now(UTC) - timedelta(days=5)

    with (
        patch.object(scraper, "_navigate_to_url", return_value=True),
        patch.object(scraper, "_get_post_date", return_value=old_date),
    ):
        result = scraper._extract_post_data(
            "https://example.com/p/123/", "test_account", cutoff_date
        )

        assert result is None


def test_extract_post_data_success(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test successful post data extraction."""
    recent_date = datetime.now(UTC) - timedelta(hours=1)
    cutoff_date = datetime.now(UTC) - timedelta(days=5)

    with (
        patch.object(scraper, "_navigate_to_url", return_value=True),
        patch.object(scraper, "_get_post_date", return_value=recent_date),
        patch.object(scraper, "_get_post_caption", return_value="Test caption"),
    ):
        result = scraper._extract_post_data(
            "https://example.com/p/123/", "test_account", cutoff_date
        )

        assert result is not None
        assert result.url == "https://example.com/p/123/"
        assert result.account == "test_account"
        assert result.caption == "Test caption"
        assert result.date_posted == recent_date


def test_navigate_to_url_success(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test successful URL navigation."""
    # Mock the response object
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response

    # Mock the wait_for_selector method
    mock_page.wait_for_selector.return_value = None

    # Mock the consent and login page checks
    with (
        patch.object(scraper, "_dismiss_consent_if_present"),
        patch.object(scraper, "_is_login_page", return_value=False),
    ):
        result = scraper._navigate_to_url("https://example.com", "test operation")

        assert result is True
        mock_page.goto.assert_called_once()


def test_navigate_to_url_timeout_failure(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test URL navigation failure due to timeout."""
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")

    result = scraper._navigate_to_url("https://example.com", "test operation")

    assert result is False


def test_navigate_to_url_exception_failure(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test URL navigation failure due to exception."""
    mock_page.goto.side_effect = Exception("Navigation error")

    result = scraper._navigate_to_url("https://example.com", "test operation")

    assert result is False


def test_get_post_date_success(mock_page: MagicMock, scraper: InstagramScraper) -> None:
    """Test successful post date extraction."""
    # Mock the locator and its methods
    mock_locator = MagicMock()
    mock_page.locator.return_value = mock_locator

    # Mock the count method to return 1
    mock_locator.count.return_value = 1

    # Mock the first element and its get_attribute method
    mock_first = MagicMock()
    mock_first.get_attribute.return_value = "2024-01-01T10:00:00Z"
    mock_locator.first = mock_first

    result = scraper._get_post_date()

    assert result is not None
    assert result.year == 2024
    assert result.month == 1
    assert result.day == 1


def test_get_post_date_no_element(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction when time element is not found."""
    mock_page.query_selector.return_value = None

    result = scraper._get_post_date()

    assert result is None


def test_get_post_date_no_datetime_attribute(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction when datetime attribute is missing."""
    mock_time_element = MagicMock()
    mock_time_element.get_attribute.return_value = None
    mock_page.query_selector.return_value = mock_time_element

    result = scraper._get_post_date()

    assert result is None


def test_get_post_date_parsing_error(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction with invalid datetime format."""
    mock_time_element = MagicMock()
    mock_time_element.get_attribute.return_value = "invalid-date-format"
    mock_page.query_selector.return_value = mock_time_element

    result = scraper._get_post_date()

    assert result is None


def test_is_valid_post_url() -> None:
    """Test post URL validation."""
    assert InstagramScraper._is_valid_post_url("https://instagram.com/p/123/") is True
    assert (
        InstagramScraper._is_valid_post_url("https://instagram.com/reel/123/") is True
    )
    assert (
        InstagramScraper._is_valid_post_url("https://instagram.com/story/123/") is False
    )
    assert InstagramScraper._is_valid_post_url("https://instagram.com/") is False


def test_normalize_post_url(scraper: InstagramScraper) -> None:
    """Test post URL normalization."""
    # Relative URL
    result = scraper._normalize_post_url("/p/123/")
    assert result == "https://www.instagram.com/p/123"

    # Absolute URL
    result = scraper._normalize_post_url("https://www.instagram.com/p/123/")
    assert result == "https://www.instagram.com/p/123"

    # URL with query parameters
    result = scraper._normalize_post_url(
        "https://www.instagram.com/p/123/?utm_source=test"
    )
    assert result == "https://www.instagram.com/p/123"

    # Invalid URL
    result = scraper._normalize_post_url("https://instagram.com/story/123/")
    assert result is None
