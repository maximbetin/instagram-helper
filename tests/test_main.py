"""Tests for main functionality."""

import os
import sys
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

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock data for testing
MOCK_POST_DATA = {
    'url': 'https://www.instagram.com/p/123/',
    'account': 'test_account',
    'caption': 'Test post caption',
    'date_posted': datetime.now(timezone.utc),
}

MOCK_ACCOUNT_POSTS = [MOCK_POST_DATA]

@pytest.fixture
def mock_page():
    """Create a mock page for testing."""
    page = MagicMock()
    page.query_selector_all.return_value = []
    page.query_selector.return_value = None
    page.goto.return_value = None
    return page

@pytest.fixture
def mock_browser():
    """Create a mock browser for testing."""
    browser = MagicMock()
    context = MagicMock()
    page = MagicMock()
    context.pages = [page]
    browser.contexts = [context]
    return browser

@pytest.fixture
def mock_playwright():
    """Create a mock playwright for testing."""
    playwright = MagicMock()
    playwright.chromium.connect_over_cdp.return_value = mock_browser()
    return playwright

def test_get_account_post_urls(mock_page):
    """Test getting post URLs from an account page."""
    # Mock link elements
    mock_link1 = MagicMock()
    mock_link1.get_attribute.return_value = '/p/123/'
    mock_link2 = MagicMock()
    mock_link2.get_attribute.return_value = '/reel/456/'
    mock_link3 = MagicMock()
    mock_link3.get_attribute.return_value = '/stories/789/'

    mock_page.query_selector_all.return_value = [mock_link1, mock_link2, mock_link3]

    urls = get_account_post_urls(mock_page)

    assert len(urls) == 2
    assert any('/p/123/' in url for url in urls)
    assert any('/reel/456/' in url for url in urls)
    assert not any('/stories/789/' in url for url in urls)

def test_get_post_caption(mock_page):
    """Test extracting post caption."""
    mock_caption = MagicMock()
    mock_caption.inner_text.return_value = '  Test caption  '
    mock_page.query_selector.return_value = mock_caption

    caption = get_post_caption(mock_page)
    assert caption == 'Test caption'

def test_get_post_caption_no_element(mock_page):
    """Test extracting post caption when no caption element exists."""
    mock_page.query_selector.return_value = None

    caption = get_post_caption(mock_page)
    assert caption == ''

def test_get_post_date(mock_page):
    """Test extracting post date."""
    mock_time = MagicMock()
    mock_time.get_attribute.return_value = '2024-01-01T12:00:00Z'
    mock_page.query_selector.return_value = mock_time

    date = get_post_date(mock_page)
    assert date is not None
    assert date.year == 2024
    assert date.month == 1
    assert date.day == 1

def test_get_post_date_no_element(mock_page):
    """Test extracting post date when no time element exists."""
    mock_page.query_selector.return_value = None

    date = get_post_date(mock_page)
    assert date is None

def test_extract_post_data_success(mock_page):
    """Test successful post data extraction."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    # Mock caption and date elements
    mock_caption = MagicMock()
    mock_caption.inner_text.return_value = 'Test caption'
    mock_time = MagicMock()
    mock_time.get_attribute.return_value = '2024-01-01T12:00:00Z'

    mock_page.query_selector.side_effect = [mock_caption, mock_time]

    result = extract_post_data('https://www.instagram.com/p/123/', cutoff_date, 'test_account', mock_page)

    assert result is not None
    assert result['url'] == 'https://www.instagram.com/p/123/'
    assert result['account'] == 'test_account'
    assert result['caption'] == 'Test caption'

def test_extract_post_data_old_post(mock_page):
    """Test post data extraction for old posts."""
    cutoff_date = datetime.now(timezone.utc) + timedelta(days=1)  # Future date

    # Mock caption and date elements
    mock_caption = MagicMock()
    mock_caption.inner_text.return_value = 'Test caption'
    mock_time = MagicMock()
    mock_time.get_attribute.return_value = '2024-01-01T12:00:00Z'

    mock_page.query_selector.side_effect = [mock_caption, mock_time]

    result = extract_post_data('https://www.instagram.com/p/123/', cutoff_date, 'test_account', mock_page)

    assert result is None

def test_process_account_success(mock_page):
    """Test successful account processing."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    # Mock successful page load and post URLs
    mock_page.goto.return_value = None
    mock_page.query_selector_all.return_value = []

    result = process_account('test_account', mock_page, cutoff_date)

    assert isinstance(result, list)
    mock_page.goto.assert_called_once()

def test_process_account_failure(mock_page):
    """Test account processing failure."""
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    # Mock page load failure
    mock_page.goto.side_effect = Exception('Connection error')

    result = process_account('test_account', mock_page, cutoff_date)

    assert result == []

@patch('os.path.exists')
@patch('builtins.open', create=True)
def test_generate_html_report(mock_open, mock_exists):
    """Test HTML report generation."""
    mock_exists.return_value = True
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    posts = [MOCK_POST_DATA]
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=1)

    result = generate_html_report(posts, cutoff_date, '/tmp', 'templates/template.html')

    assert result.endswith('.html')
    mock_file.write.assert_called_once()

def test_setup_browser(mock_playwright):
    """Test browser setup."""
    with patch('subprocess.Popen') as mock_popen:
        with patch('time.sleep'):
            result = setup_browser(mock_playwright)

            assert result is not None
            mock_popen.assert_called_once()
            mock_playwright.chromium.connect_over_cdp.assert_called_once()

if __name__ == '__main__':
    pytest.main([__file__])
