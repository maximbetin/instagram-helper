import builtins
import os
import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from browser_manager import setup_browser
from instagram_scraper import extract_post_data, get_account_post_urls, get_post_caption, get_post_date, process_account
from report_generator import generate_html_report

# Mock config constants
MOCK_INSTAGRAM_MAX_POSTS_PER_ACCOUNT = 4
MOCK_TIMEZONE = timezone(timedelta(hours=2))
MOCK_INSTAGRAM_URL = "https://www.instagram.com/"

# Add project root to path to allow absolute imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_page():
    """Fixture for a mocked Playwright page."""
    return MagicMock()

@pytest.fixture
def mock_element():
    """Fixture for a mocked Playwright element."""
    return MagicMock()

def test_get_account_post_urls(mock_page, mock_element):
    """Test fetching post URLs from an account page."""
    mock_link1 = MagicMock()
    mock_link1.get_attribute.return_value = '/p/C12345/'
    mock_link2 = MagicMock()
    mock_link2.get_attribute.return_value = '/reel/R67890/'
    mock_link3 = MagicMock()
    mock_link3.get_attribute.return_value = '/explore/tags/something/'
    mock_link4 = MagicMock()
    mock_link4.get_attribute.return_value = None

    mock_page.query_selector_all.return_value = [mock_link1, mock_link2, mock_link3, mock_link4]

    urls = get_account_post_urls(mock_page)

    assert f"{MOCK_INSTAGRAM_URL.rstrip('/')}/p/C12345" in urls
    assert f"{MOCK_INSTAGRAM_URL.rstrip('/')}/reel/R67890" in urls
    assert len(urls) == 2

def test_get_account_post_urls_absolute_url(mock_page, mock_element):
    """Test get_account_post_urls with an absolute post URL (does not start with '/')."""
    mock_element.get_attribute.side_effect = [
        'https://www.instagram.com/p/abc123/',  # absolute URL
        None
    ]
    mock_page.query_selector_all.return_value = [mock_element, mock_element]
    urls = get_account_post_urls(mock_page)
    assert urls == ['https://www.instagram.com/p/abc123']

def test_get_post_caption(mock_page, mock_element):
    """Test extracting a post's caption."""
    mock_element.inner_text.return_value = "  A nice caption  "
    mock_page.query_selector.return_value = mock_element

    caption = get_post_caption(mock_page)
    assert caption == "A nice caption"

def test_get_post_caption_no_caption(mock_page):
    """Test extracting a post's caption when none is found."""
    mock_page.query_selector.return_value = None
    caption = get_post_caption(mock_page)
    assert caption == ""

def test_get_post_date(mock_page, mock_element):
    """Test extracting a post's date."""
    utc_time_str = "2023-01-01T12:00:00.000Z"
    mock_element.get_attribute.return_value = utc_time_str
    mock_page.query_selector.return_value = mock_element

    post_date = get_post_date(mock_page)

    expected_date = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00')).astimezone(MOCK_TIMEZONE)
    assert post_date == expected_date

def test_get_post_date_no_date(mock_page):
    """Test extracting a post's date when no date element is found."""
    mock_page.query_selector.return_value = None
    post_date = get_post_date(mock_page)
    assert post_date is None

def test_get_post_date_no_datetime_attr(mock_page, mock_element):
    """Test extracting a post's date when the element has no datetime attribute."""
    mock_element.get_attribute.return_value = None
    mock_page.query_selector.return_value = mock_element
    post_date = get_post_date(mock_page)
    assert post_date is None

@patch('instagram_scraper.get_post_date')
@patch('instagram_scraper.get_post_caption')
@patch('instagram_scraper.time.sleep', return_value=None)
def test_extract_post_data(mock_sleep, mock_get_caption, mock_get_date, mock_page):
    """Test extracting all data from a post page."""
    post_url = "http://example.com/p/123"
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    account = "test_account"

    mock_get_date.return_value = datetime.now(MOCK_TIMEZONE)
    mock_get_caption.return_value = "A caption"

    data = extract_post_data(post_url, cutoff_date, account, mock_page)

    mock_page.goto.assert_called_once_with(post_url, wait_until="domcontentloaded", timeout=20000)
    assert data is not None
    assert data['url'] == post_url
    assert data['account'] == account
    assert data['caption'] == "A caption"
    assert data['date_posted'] is not None

@patch('instagram_scraper.get_post_date')
@patch('instagram_scraper.time.sleep', return_value=None)
def test_extract_post_data_too_old(mock_sleep, mock_get_date, mock_page):
    """Test extracting data from a post that is too old."""
    post_url = "http://example.com/p/123"
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    account = "test_account"

    mock_get_date.return_value = datetime.now(MOCK_TIMEZONE) - timedelta(days=2)

    data = extract_post_data(post_url, cutoff_date, account, mock_page)

    assert data is None

@patch('instagram_scraper.get_post_date', return_value=None)
@patch('instagram_scraper.time.sleep', return_value=None)
def test_extract_post_data_no_date(mock_sleep, mock_get_date, mock_page):
    """Test extracting data when no date is found."""
    post_url = "http://example.com/p/123"
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    account = "test_account"

    data = extract_post_data(post_url, cutoff_date, account, mock_page)

    assert data is None

@patch('instagram_scraper.get_post_date')
@patch('instagram_scraper.get_post_caption')
@patch('instagram_scraper.time.sleep', return_value=None)
def test_extract_post_data_timeout_retry(mock_sleep, mock_get_caption, mock_get_date, mock_page):
    """Test that extract_post_data retries on timeout errors."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    from config import INSTAGRAM_POST_LOAD_TIMEOUT

    post_url = "http://example.com/p/123"
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    account = "test_account"

    # First call raises timeout, second call succeeds
    mock_page.goto.side_effect = [PlaywrightTimeoutError("Timeout"), None]
    mock_get_date.return_value = datetime.now(MOCK_TIMEZONE)
    mock_get_caption.return_value = "A caption"

    data = extract_post_data(post_url, cutoff_date, account, mock_page)

    # Should have been called twice (retry)
    assert mock_page.goto.call_count == 2
    assert data is not None
    assert data['url'] == post_url
    assert data['account'] == account
    assert data['caption'] == "A caption"
    assert data['date_posted'] is not None

@patch('instagram_scraper.get_post_date')
@patch('instagram_scraper.get_post_caption')
@patch('instagram_scraper.time.sleep', return_value=None)
def test_extract_post_data_timeout_failure(mock_sleep, mock_get_caption, mock_get_date, mock_page):
    """Test that extract_post_data returns None after all retries fail."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    from config import INSTAGRAM_POST_LOAD_TIMEOUT

    post_url = "http://example.com/p/123"
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    account = "test_account"

    # All calls raise timeout
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")
    mock_get_date.return_value = datetime.now(MOCK_TIMEZONE)
    mock_get_caption.return_value = "A caption"

    data = extract_post_data(post_url, cutoff_date, account, mock_page)

    # Should have been called 3 times (initial + 2 retries)
    assert mock_page.goto.call_count == 3
    assert data is None

def test_generate_html_report(tmp_path):
    """Test the generation of the HTML report."""
    posts = [
        {'url': 'http://a.com', 'account': 'acc1', 'caption': 'cap1', 'date_posted': datetime(2023, 1, 2)},
        {'url': 'http://b.com', 'account': 'acc2', 'caption': 'cap2', 'date_posted': datetime(2023, 1, 1)},
    ]
    cutoff_date = datetime(2023, 1, 1)

    template_content = "<html><body>{{total_posts}} posts</body></html>"
    template_path = tmp_path / "test_template.html"
    template_path.write_text(template_content)

    output_dir = tmp_path
    report_path = generate_html_report(posts, cutoff_date, str(output_dir), str(template_path))

    assert os.path.exists(report_path)
    with open(report_path, 'r') as f:
        content = f.read()
        assert "2 posts" in content

@patch('browser_manager.subprocess.Popen')
@patch('browser_manager.time.sleep', return_value=None)
@patch('playwright.sync_api.sync_playwright')
def test_setup_browser(mock_playwright, mock_sleep, mock_popen):
    """Test setting up the browser connection."""
    mock_p = MagicMock()
    mock_playwright.return_value.__enter__.return_value = mock_p

    setup_browser(mock_p)

    mock_popen.assert_called_once()
    mock_p.chromium.connect_over_cdp.assert_called_once()

@patch('instagram_scraper.INSTAGRAM_MAX_POSTS_PER_ACCOUNT', 10)
@patch('instagram_scraper.extract_post_data')
@patch('instagram_scraper.get_account_post_urls')
@patch('instagram_scraper.time.sleep', return_value=None)
def test_process_account(mock_sleep, mock_get_urls, mock_extract, mock_page):
    """Test processing a single account."""
    account = 'test_account'
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    mock_get_urls.return_value = ['url1', 'url2', 'url3', 'url4']
    mock_extract.side_effect = [{'data': 1}, {'data': 2}, {'data': 3}, None]

    posts = process_account(account, mock_page, cutoff_date)

    assert len(posts) == 3
    assert mock_extract.call_count == 4  # Called for each URL until None is returned

@patch('instagram_scraper.extract_post_data')
@patch('instagram_scraper.get_account_post_urls')
@patch('instagram_scraper.time.sleep', return_value=None)
def test_process_account_stops_on_old_post(mock_sleep, mock_get_urls, mock_extract, mock_page):
    """Test that processing stops when an old post is found."""
    account = 'test_account'
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)
    mock_get_urls.return_value = ['url1', 'url2']
    mock_extract.side_effect = [{'data': 1}, None]

    posts = process_account(account, mock_page, cutoff_date)

    assert len(posts) == 1
    assert mock_extract.call_count == 2

@patch('instagram_scraper.get_account_post_urls', return_value=[])
@patch('instagram_scraper.time.sleep', return_value=None)
def test_process_account_no_posts(mock_sleep, mock_get_urls, mock_page):
    """Test processing an account with no posts."""
    account = 'test_account'
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)

    posts = process_account(account, mock_page, cutoff_date)

    assert len(posts) == 0

@patch('instagram_scraper.time.sleep', return_value=None)
def test_process_account_timeout_error(mock_sleep, mock_page):
    """Test that process_account handles timeout errors gracefully."""
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

    account = 'test_account'
    cutoff_date = datetime.now(MOCK_TIMEZONE) - timedelta(days=1)

    # Mock the page.goto to raise a timeout error
    mock_page.goto.side_effect = PlaywrightTimeoutError("Timeout")

    posts = process_account(account, mock_page, cutoff_date)

    assert len(posts) == 0
