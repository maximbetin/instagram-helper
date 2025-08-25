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
    """Test scraper initialization and user agent setting."""
    InstagramScraper(mock_page, settings)
    mock_page.set_extra_http_headers.assert_called_once()
    assert "User-Agent" in mock_page.set_extra_http_headers.call_args[0][0]


def test_get_post_urls_max_posts_limit(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test that post URL collection stops at max posts limit."""
    # Create mock links that exceed the max posts limit
    mock_links = []
    for i in range(10):  # More than the default limit
        mock_link = MagicMock()
        mock_link.get_attribute.return_value = f"/p/post_{i}/"
        mock_links.append(mock_link)

    mock_page.query_selector_all.return_value = mock_links

    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    urls = scraper._get_post_urls("test_account", cutoff_date)

    # Should only return up to max posts limit (could be 3 or 5 depending on config)
    max_posts = scraper.settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT
    assert len(urls) == max_posts
    assert len(urls) <= 5  # Should not exceed 5


def test_get_post_urls_collects_all_urls(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test that URL collection gathers all available post URLs without date filtering."""
    # Create mock links with dates
    mock_links = []
    for i in range(3):
        mock_link = MagicMock()
        mock_link.get_attribute.return_value = f"/p/post_{i}/"
        mock_links.append(mock_link)

    mock_page.query_selector_all.return_value = mock_links

    cutoff_date = datetime.now(UTC) - timedelta(days=5)
    urls = scraper._get_post_urls("test_account", cutoff_date)

    # Should collect all URLs (date filtering happens during processing)
    assert len(urls) == 3
    assert "https://www.instagram.com/p/post_0" in urls
    assert "https://www.instagram.com/p/post_1" in urls
    assert "https://www.instagram.com/p/post_2" in urls


def test_get_post_urls_exception_handling(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test that exceptions in URL collection are handled gracefully."""
    mock_page.query_selector_all.side_effect = Exception("Page error")

    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    urls = scraper._get_post_urls("test_account", cutoff_date)

    assert urls == []


def test_get_post_date_from_url_post_type(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction for regular posts."""
    post_url = "https://www.instagram.com/test_account/p/123/"

    # Mock successful navigation and date extraction
    with (
        patch.object(scraper, "_navigate_to_url", return_value=True),
        patch.object(scraper, "_get_post_date", return_value=datetime.now(UTC)),
        patch.object(scraper, "_navigate_to_url") as mock_nav,
    ):
        result = scraper._get_post_date_from_url(post_url)

        assert result is not None
        # Should navigate back to account page
        assert mock_nav.call_count == 2


def test_get_post_date_from_url_reel_type(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction for reel posts."""
    post_url = "https://www.instagram.com/test_account/reel/123/"

    with (
        patch.object(scraper, "_navigate_to_url", return_value=True),
        patch.object(scraper, "_get_post_date", return_value=datetime.now(UTC)),
        patch.object(scraper, "_navigate_to_url") as mock_nav,
    ):
        result = scraper._get_post_date_from_url(post_url)

        assert result is not None
        assert mock_nav.call_count == 2


def test_get_post_date_from_url_unknown_type(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction for unknown post types."""
    post_url = "https://www.instagram.com/test_account/story/123/"

    with (
        patch.object(scraper, "_navigate_to_url", return_value=True),
        patch.object(scraper, "_get_post_date", return_value=datetime.now(UTC)),
    ):
        result = scraper._get_post_date_from_url(post_url)

        # Should return the date without trying to navigate back
        assert result is not None


def test_get_post_date_from_url_navigation_failure(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test post date extraction when navigation fails."""
    post_url = "https://www.instagram.com/test_account/p/123/"

    with patch.object(scraper, "_navigate_to_url", return_value=False):
        result = scraper._get_post_date_from_url(post_url)

        assert result is None


def test_get_post_date_from_url_exception_handling(
    mock_page: MagicMock, scraper: InstagramScraper
) -> None:
    """Test exception handling in post date extraction."""
    post_url = "https://www.instagram.com/test_account/p/123/"

    with patch.object(
        scraper, "_navigate_to_url", side_effect=Exception("Navigation error")
    ):
        result = scraper._get_post_date_from_url(post_url)

        assert result is None


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
    mock_page.goto.return_value = None

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
    mock_time_element = MagicMock()
    mock_time_element.get_attribute.return_value = "2024-01-01T10:00:00Z"
    mock_page.query_selector.return_value = mock_time_element

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
