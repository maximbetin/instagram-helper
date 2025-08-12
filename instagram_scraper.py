"""Instagram scraping functionality."""

import time
from dataclasses import dataclass
from datetime import datetime

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from config import (
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT,
    INSTAGRAM_POST_LOAD_TIMEOUT,
    INSTAGRAM_URL,
    TIMEZONE,
)
from utils import setup_logging

logger = setup_logging(__name__)

# XPath selectors for post captions. The first one is the most recent and specific.
CAPTION_XPATHS = [
    "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span",
]

@dataclass
class InstagramPost:
    """Represents a single scraped Instagram post."""

    url: str
    account: str
    caption: str
    date_posted: datetime


def _is_valid_post_url(url: str) -> bool:
    """Check if a URL is a valid Instagram post URL."""
    return any(pattern in url for pattern in ["/p/", "/reel/"])


def _normalize_post_url(url: str) -> str:
    """Normalize a post URL by ensuring it's absolute and clean."""
    base_url = INSTAGRAM_URL.rstrip("/")
    if url.startswith("/"):
        full_url = f"{base_url}{url}"
    else:
        full_url = url
    return full_url.split("?")[0].rstrip("/")


def _get_post_urls(page: Page, account: str) -> list[str]:
    """Fetch all unique post URLs from the account's page."""
    logger.debug(f"@{account}: Searching for post URLs...")
    selector = "a[href*='/p/'], a[href*='/reel/']"
    try:
        links = page.query_selector_all(selector)
        if not links:
            logger.warning(f"@{account}: No post links found with selector: {selector}")
            return []

        post_urls = []
        seen_urls = set()
        for link in links:
            href = link.get_attribute("href")
            if href and _is_valid_post_url(href):
                normalized_url = _normalize_post_url(href)
                if normalized_url not in seen_urls:
                    post_urls.append(normalized_url)
                    seen_urls.add(normalized_url)

        logger.info(
            f"@{account}: Found {len(post_urls)} unique post URLs."
            f" Limited to {INSTAGRAM_MAX_POSTS_PER_ACCOUNT}."
        )
        return post_urls[:INSTAGRAM_MAX_POSTS_PER_ACCOUNT]

    except Exception as e:
        logger.error(f"@{account}: Failed to query for post URLs: {e}")
        return []


def _try_caption_xpath(page: Page, xpath: str) -> str | None:
    """Attempt to extract a caption using a specific XPath selector."""
    try:
        caption_element = page.locator(f"xpath={xpath}").first
        if caption_element and caption_element.is_visible(timeout=1000):
            caption = caption_element.inner_text().strip()
            if caption:
                logger.debug(f"Successfully extracted caption with XPath: {xpath}")
                return caption
    except Exception as e:
        logger.debug(f"XPath lookup failed for '{xpath}': {e}")
    return None


def _get_post_caption(page: Page) -> str:
    """Extract the post caption by trying a list of XPath selectors."""
    for xpath in CAPTION_XPATHS:
        caption = _try_caption_xpath(page, xpath)
        if caption:
            return caption
    logger.warning("Could not find post caption.")
    return ""


def _get_post_date(page: Page) -> datetime | None:
    """Extract the post's date from the page."""
    selector = "time[datetime]"
    try:
        time_element = page.query_selector(selector)
        if time_element and (datetime_attr := time_element.get_attribute("datetime")):
            utc_dt = datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
            return utc_dt.astimezone(TIMEZONE)
        logger.warning("Could not find time element with a datetime attribute.")
    except Exception as e:
        logger.error(f"Error parsing date from time element: {e}")
    return None


def _navigate_to_url(
    page: Page, url: str, account: str, operation: str, max_retries: int = 1
) -> bool:
    """Navigate to a URL with retries and consistent error handling."""
    for attempt in range(max_retries + 1):
        try:
            page.goto(
                url, wait_until="domcontentloaded", timeout=INSTAGRAM_POST_LOAD_TIMEOUT
            )
            # A small, fixed delay can help if content loads lazily after the DOM is ready.
            time.sleep(1)
            return True
        except PlaywrightTimeoutError:
            logger.warning(
                f"@{account}: Timeout loading {operation} at {url} "
                f"(Attempt {attempt + 1}/{max_retries + 1})."
            )
        except Exception as e:
            logger.error(f"@{account}: Failed to load {operation} at {url}: {e}")
            break  # Don't retry on unexpected errors
    return False


def _extract_post_data(
    page: Page, post_url: str, account: str, cutoff_date: datetime
) -> InstagramPost | None:
    """Navigate to a post and extract its data if it's recent enough."""
    if not _navigate_to_url(page, post_url, account, "post"):
        return None

    post_date = _get_post_date(page)
    if not post_date:
        logger.warning(f"@{account}: Could not determine post date for {post_url}.")
        return None

    if post_date < cutoff_date:
        logger.debug(
            f"@{account}: Skipping post from {post_date.date()} (older than cutoff)."
        )
        return None

    return InstagramPost(
        url=post_url,
        account=account,
        caption=_get_post_caption(page),
        date_posted=post_date,
    )


def process_account(
    account: str, page: Page, cutoff_date: datetime
) -> list[InstagramPost]:
    """
    Process a single Instagram account:
    - Navigate to the account page.
    - Find all post URLs.
    - For each post, extract data if it's newer than the cutoff date.
    """
    logger.info(f"Processing account: @{account}")
    account_url = f"{INSTAGRAM_URL}{account}/"

    if not _navigate_to_url(page, account_url, account, "account page"):
        return []

    post_urls = _get_post_urls(page, account)
    if not post_urls:
        return []

    account_posts: list[InstagramPost] = []
    for i, post_url in enumerate(post_urls):
        logger.debug(
            f"@{account}: Processing post {i + 1}/{len(post_urls)}: {post_url}"
        )

        post_data = _extract_post_data(page, post_url, account, cutoff_date)
        if post_data:
            account_posts.append(post_data)
        elif post_data is None:
            # This means the post was older than the cutoff, so we can stop.
            # Assumes posts are chronological.
            logger.info(
                f"@{account}: Reached a post older than the cutoff date. "
                "Moving to the next account."
            )
            break

    logger.info(f"@{account}: Found {len(account_posts)} new posts.")
    return account_posts
