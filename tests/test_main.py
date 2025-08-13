"""Tests for the core scraping and reporting functionality."""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from _pytest.monkeypatch import MonkeyPatch
from freezegun import freeze_time


@pytest.fixture(autouse=True)
def set_env_variables(monkeypatch: MonkeyPatch) -> None:
    """Set environment variables required for testing."""
    monkeypatch.setenv("BROWSER_PATH", "/usr/bin/mock-browser")
    monkeypatch.setenv("BROWSER_USER_DATA_DIR", "/tmp/mock-user-data")


from config import settings
from instagram_scraper import (
    InstagramPost,
    InstagramScraper,
)
from report_generator import ReportData, generate_html_report

# Mock data for testing
FROZEN_TIME = "2024-01-01 12:00:00"
MOCK_POST_URL = "https://www.instagram.com/p/123/"
MOCK_ACCOUNT = "test_account"


@pytest.fixture
def mock_page() -> MagicMock:
    """Provides a mock Playwright Page object."""
    page = MagicMock()
    page.query_selector_all.return_value = []
    page.query_selector.return_value = None
    page.goto.return_value = None
    return page


def test_get_post_urls_success(mock_page: MagicMock) -> None:
    """Test that valid post and reel URLs are correctly identified and normalized."""
    mock_link_p = MagicMock()
    mock_link_p.get_attribute.return_value = "/p/123/"
    mock_link_reel = MagicMock()
    mock_link_reel.get_attribute.return_value = "/reel/456/"
    mock_page.query_selector_all.return_value = [mock_link_p, mock_link_reel]

    scraper = InstagramScraper(mock_page, settings)
    urls = scraper._get_post_urls(MOCK_ACCOUNT)
    assert len(urls) == 2
    assert "https://www.instagram.com/p/123" in urls
    assert "https://www.instagram.com/reel/456" in urls


def test_get_post_urls_no_links(mock_page: MagicMock) -> None:
    """Test that an empty list is returned when no valid links are found."""
    mock_link_story = MagicMock()
    mock_link_story.get_attribute.return_value = "/stories/789/"
    mock_page.query_selector_all.return_value = [mock_link_story]
    scraper = InstagramScraper(mock_page, settings)
    assert not scraper._get_post_urls(MOCK_ACCOUNT)


def test_get_post_caption_found(mock_page: MagicMock) -> None:
    """Test that a post caption is correctly extracted and stripped."""
    mock_locator = MagicMock()
    mock_element = MagicMock()
    mock_element.is_visible.return_value = True
    mock_element.inner_text.return_value = "  A test caption.  "
    mock_locator.first = mock_element
    mock_page.locator.return_value = mock_locator

    scraper = InstagramScraper(mock_page, settings)
    assert scraper._get_post_caption() == "A test caption."


def test_get_post_caption_not_found(mock_page: MagicMock) -> None:
    """Test that an empty string is returned if no caption element is found."""
    mock_locator = MagicMock()
    mock_element = MagicMock()
    mock_element.is_visible.return_value = False
    mock_locator.first = mock_element
    mock_page.locator.return_value = mock_locator

    scraper = InstagramScraper(mock_page, settings)
    assert scraper._get_post_caption() == ""


@freeze_time(FROZEN_TIME)
def test_get_post_date_found(mock_page: MagicMock) -> None:
    """Test correct extraction and timezone conversion of a post date."""
    mock_time_element = MagicMock()
    mock_time_element.get_attribute.return_value = "2024-01-01T10:00:00Z"
    mock_page.query_selector.return_value = mock_time_element
    scraper = InstagramScraper(mock_page, settings)
    post_date = scraper._get_post_date()
    assert post_date is not None
    assert post_date.year == 2024
    assert post_date.month == 1
    assert post_date.day == 1
    assert post_date.hour == 12
    assert post_date.tzinfo is not None


def test_get_post_date_not_found(mock_page: MagicMock) -> None:
    """Test that None is returned when the time element is not found."""
    mock_page.query_selector.return_value = None
    scraper = InstagramScraper(mock_page, settings)
    assert scraper._get_post_date() is None


@freeze_time(FROZEN_TIME)
@patch("instagram_scraper.InstagramScraper._extract_post_data")
def test_process_account_success(
    mock_extract_post_data: MagicMock, mock_page: MagicMock
) -> None:
    """Test successful processing of an account with multiple posts."""
    post1 = InstagramPost(
        "url1", MOCK_ACCOUNT, "caption1", datetime.now(UTC) - timedelta(hours=1)
    )
    post2 = InstagramPost(
        "url2", MOCK_ACCOUNT, "caption2", datetime.now(UTC) - timedelta(hours=2)
    )
    mock_extract_post_data.side_effect = [post1, post2, None]

    scraper = InstagramScraper(mock_page, settings)
    with patch.object(scraper, "_get_post_urls", return_value=["url1", "url2", "url3"]):
        cutoff_date = datetime.now(UTC) - timedelta(days=1)
        result = scraper.process_account(MOCK_ACCOUNT, cutoff_date)

        assert len(result) == 2
        assert result[0] == post1
        assert result[1] == post2
        mock_page.goto.assert_called()
        assert mock_extract_post_data.call_count == 3


def test_process_account_navigation_fails(mock_page: MagicMock) -> None:
    """Test that account processing returns an empty list if navigation fails."""
    mock_page.goto.side_effect = Exception("Navigation failed")
    cutoff_date = datetime.now(UTC) - timedelta(days=1)
    scraper = InstagramScraper(mock_page, settings)
    result = scraper.process_account(MOCK_ACCOUNT, cutoff_date)
    assert result == []


@freeze_time(FROZEN_TIME)
def test_generate_html_report_success(tmp_path: Path) -> None:
    """Test successful generation of the HTML report."""
    posts = [
        InstagramPost(
            MOCK_POST_URL,
            MOCK_ACCOUNT,
            "Caption",
            datetime.now(UTC),
        )
    ]
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    template_path = template_dir / "template.html"
    template_path.write_text("<html>{{ total_posts }} posts</html>")

    report_data = ReportData(
        posts=posts, cutoff_date=datetime.now(UTC) - timedelta(days=1)
    )
    report_path = generate_html_report(report_data, tmp_path, str(template_path))

    assert report_path is not None
    report_file = Path(report_path)
    assert report_file.exists()
    assert "1 posts" in report_file.read_text()


def test_generate_html_report_no_posts(tmp_path: Path) -> None:
    """Test that no report is generated if there are no posts."""
    report_data = ReportData(
        posts=[], cutoff_date=datetime.now(UTC) - timedelta(days=1)
    )
    report_path = generate_html_report(report_data, tmp_path, "dummy.html")
    assert report_path is None
