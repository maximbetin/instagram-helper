"""Instagram scraping functionality."""

import time
from datetime import datetime

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import (
    INSTAGRAM_ACCOUNT_LOAD_DELAY,
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT,
    INSTAGRAM_POST_LOAD_DELAY,
    INSTAGRAM_POST_LOAD_TIMEOUT,
    INSTAGRAM_RETRY_DELAY,
    INSTAGRAM_URL,
    SECONDS_IN_MS,
    TIMEZONE,
)
from utils import setup_logging

logger = setup_logging(__name__)

# Constants for caption extraction
CAPTION_SELECTORS = [
    "div[data-testid='post-caption'] h1",
    "div[data-testid='post-caption'] span",
    "div[data-testid='post-caption'] div",
    "article h1",
    "div[role='button'] h1",
    "h1",
]

# Constants for date extraction
DATE_SELECTORS = [
    "time[datetime]",
    "time",
    "div[data-testid='post-timestamp'] time[datetime]",
    "div[data-testid='post-timestamp']",
]

# Constants for post link detection
POST_PATH_PATTERNS = ["/p/", "/reel/"]
SKIP_TEXT_PATTERNS = [
    "follow", "like", "comment", "share", "save", "more"
]


def _handle_scraping_error(
    account: str, operation: str, error: Exception, retry_attempt: int | None = None
) -> None:
    """Handle common scraping errors with consistent logging."""
    if isinstance(error, PlaywrightTimeoutError):
        if retry_attempt is not None:
            logger.warning(
                f"@{account}: Timeout during {operation} "
                f"(attempt {retry_attempt + 1}). Retrying..."
            )
        else:
            logger.error(f"@{account}: Timeout during {operation}: {error}")
    elif isinstance(error, ValueError | OSError):
        logger.error(f"@{account}: System error during {operation}: {error}")
    else:
        logger.error(f"@{account}: Unexpected error during {operation}: {error}")


def _is_valid_post_url(url: str) -> bool:
    """Check if a URL is a valid Instagram post URL."""
    return any(pattern in url for pattern in POST_PATH_PATTERNS)


def _normalize_post_url(url: str) -> str:
    """Normalize a post URL by removing query parameters and trailing slashes."""
    if url.startswith("/"):
        full_url = f"{INSTAGRAM_URL.rstrip('/')}{url}"
    else:
        full_url = url

    return full_url.split("?")[0].rstrip("/")


def get_account_post_urls(page: Page) -> list[str]:
    """Fetch all post URLs from a specific Instagram account page, preserving order."""
    post_urls = []
    seen_urls = set()

    # Try multiple approaches to find post links
    link_selectors = [
        "a[href*='/p/']",  # Direct post links
        "a[href*='/reel/']",  # Reel links
        "a",  # All links as fallback
    ]

    for selector in link_selectors:
        try:
            links = page.query_selector_all(selector)
            logger.debug(f"Found {len(links)} links with selector: {selector}")

            for link in links:
                post_url = link.get_attribute("href")
                if post_url and _is_valid_post_url(post_url):
                    normalized_url = _normalize_post_url(post_url)

                    if normalized_url not in seen_urls:
                        post_urls.append(normalized_url)
                        seen_urls.add(normalized_url)
                        logger.debug(f"Found post URL: {normalized_url}")

            # If we found posts with this selector, no need to try others
            if post_urls:
                break

        except Exception as e:
            logger.debug(f"Selector {selector} failed: {e}")
            continue

    logger.info(f"Total unique post URLs found: {len(post_urls)}")
    return post_urls


def _try_caption_selector(page: Page, selector: str) -> str | None:
    """Try to extract caption using a specific selector."""
    try:
        caption_element = page.query_selector(selector)
        if caption_element and caption_element.inner_text().strip():
            caption = caption_element.inner_text().strip()
            logger.debug(f"Found caption using selector: {selector}")
            return caption
    except Exception as e:
        logger.debug(f"Selector {selector} failed: {e}")
    return None


def _find_caption_by_text_content(page: Page) -> str:
    """Find caption by looking for elements with substantial text content."""
    try:
        all_elements = page.query_selector_all("*")
        for element in all_elements:
            try:
                text = element.inner_text().strip()
                # Look for text that's likely a caption (substantial length, not just navigation)
                if (
                    text
                    and 10 < len(text) < 1000
                    and not any(
                        skip in text.lower() for skip in SKIP_TEXT_PATTERNS
                    )
                ):
                    tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                    # If it's an h1, h2, h3, p, or span, it's more likely to be a caption
                    if tag_name in ["h1", "h2", "h3", "p", "span", "div"]:
                        logger.debug(
                            f"Found potential caption in {tag_name}: '{text[:100]}...'"
                        )
                        return text
            except Exception:
                continue
    except Exception as e:
        logger.debug(f"Alternative caption search failed: {e}")

    return ""


def get_post_caption(page: Page) -> str:
    """Extract post's caption from Instagram post."""
    # Try selectors first
    for selector in CAPTION_SELECTORS:
        caption = _try_caption_selector(page, selector)
        if caption:
            return caption

    # Fallback: look for elements with substantial text content
    caption = _find_caption_by_text_content(page)
    if caption:
        return caption

    logger.warning("Could not find post caption with any selector")
    return ""


def _try_date_selector(page: Page, selector: str) -> datetime | None:
    """Try to extract date using a specific selector."""
    try:
        date_element = page.query_selector(selector)
        if date_element:
            datetime_attr = date_element.get_attribute("datetime")
            if datetime_attr:
                utc_datetime = datetime.fromisoformat(
                    datetime_attr.replace("Z", "+00:00")
                )
                logger.debug(f"Found date using selector: {selector}")
                return utc_datetime.astimezone(TIMEZONE)
    except Exception as e:
        logger.debug(f"Date selector {selector} failed: {e}")
    return None


def get_post_date(page: Page) -> datetime | None:
    """Extract post's date from Instagram post page."""
    for selector in DATE_SELECTORS:
        post_date = _try_date_selector(page, selector)
        if post_date:
            return post_date

    logger.warning("Could not find post date with any selector")
    return None


def extract_post_data(
    post_url: str, cutoff_date: datetime, account: str, page: Page, max_retries: int = 2
) -> dict | None:
    """Extract post data from the post URL with error handling and retries."""
    for attempt in range(max_retries + 1):
        try:
            page.goto(
                post_url,
                wait_until="domcontentloaded",
                timeout=INSTAGRAM_POST_LOAD_TIMEOUT,
            )
            time.sleep(INSTAGRAM_POST_LOAD_DELAY / SECONDS_IN_MS)

            post_date = get_post_date(page)
            if not post_date or post_date < cutoff_date:
                return None

            return {
                "url": post_url,
                "account": account,
                "caption": get_post_caption(page),
                "date_posted": post_date,
            }

        except PlaywrightTimeoutError as e:
            if attempt < max_retries:
                _handle_scraping_error(account, f"loading post {post_url}", e, attempt)
                time.sleep(INSTAGRAM_RETRY_DELAY / SECONDS_IN_MS)
                continue
            else:
                _handle_scraping_error(account, f"loading post {post_url}", e)
                return None
        except Exception as e:
            _handle_scraping_error(account, f"loading post {post_url}", e)
            return None

    return None


def process_account(account: str, page: Page, cutoff_date: datetime) -> list[dict]:
    """Process a single Instagram account and return its recent posts."""
    logger.info(f"@{account}: Processing posts...")

    try:
        account_url = f"{INSTAGRAM_URL}{account}/"
        page.goto(
            account_url,
            wait_until="domcontentloaded",
            timeout=INSTAGRAM_POST_LOAD_TIMEOUT,
        )
        time.sleep(INSTAGRAM_ACCOUNT_LOAD_DELAY / SECONDS_IN_MS)
    except Exception as e:
        _handle_scraping_error(account, "loading account page", e)
        return []

    logger.debug(f"@{account}: Fetching post URLs...")
    post_urls = get_account_post_urls(page)
    if not post_urls:
        logger.warning(f"@{account}: No post URLs found.")
        return []

    logger.debug(
        f"@{account}: Found {len(post_urls)} post URLs. Fetching post details..."
    )
    account_posts = []

    for i, post_url in enumerate(post_urls[:INSTAGRAM_MAX_POSTS_PER_ACCOUNT]):
        logger.debug(
            f"@{account}: Fetching post {i + 1}/"
            f"{min(len(post_urls), INSTAGRAM_MAX_POSTS_PER_ACCOUNT)}: {post_url}"
        )
        post_data = extract_post_data(post_url, cutoff_date, account, page)
        if post_data:
            account_posts.append(post_data)
        else:
            logger.info(
                f"@{account}: Found post older than cutoff date, stopping for this account."
            )
            break

    logger.info(f"@{account}: Found {len(account_posts)} recent post(s).")
    return account_posts
