"""Instagram scraping functionality."""

import time
from datetime import datetime
from typing import Optional

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import (
    BROWSER_LOAD_TIMEOUT,
    INSTAGRAM_ACCOUNT_LOAD_DELAY,
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT,
    INSTAGRAM_POST_LOAD_DELAY,
    INSTAGRAM_POST_LOAD_TIMEOUT,
    INSTAGRAM_RETRY_DELAY,
    INSTAGRAM_URL,
    TIMEZONE,
)
from utils import setup_logging

logger = setup_logging(__name__)


def get_account_post_urls(page: Page) -> list[str]:
    """Fetch all post URLs from a specific Instagram account page, preserving order."""
    post_urls = []
    seen_urls = set()

    links = page.query_selector_all("a")

    for link in links:
        post_url = link.get_attribute("href")
        if post_url and any(path in post_url for path in ["/p/", "/reel/"]):
            if post_url.startswith("/"):
                full_url = f"{INSTAGRAM_URL.rstrip('/')}{post_url}"
            else:
                full_url = post_url

            full_url = full_url.split("?")[0].rstrip("/")

            if full_url not in seen_urls:
                post_urls.append(full_url)
                seen_urls.add(full_url)

    return post_urls


def get_post_caption(page: Page) -> str:
    """Extract post's caption from Instagram post."""
    caption_element = page.query_selector("h1")
    return caption_element.inner_text().strip() if caption_element else ""


def get_post_date(page: Page) -> Optional[datetime]:
    """Extract post's date from Instagram post page."""
    date_element = page.query_selector("time[datetime]")
    if date_element:
        datetime_attr = date_element.get_attribute("datetime")
        if datetime_attr:
            utc_datetime = datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
            return utc_datetime.astimezone(TIMEZONE)
    return None


def extract_post_data(
    post_url: str, cutoff_date: datetime, account: str, page: Page, max_retries: int = 2
) -> Optional[dict]:
    """Extract post data from the post URL with error handling and retries."""
    for attempt in range(max_retries + 1):
        try:
            page.goto(
                post_url,
                wait_until="domcontentloaded",
                timeout=INSTAGRAM_POST_LOAD_TIMEOUT,
            )
            time.sleep(INSTAGRAM_POST_LOAD_DELAY / 1000)

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
                logger.warning(
                    f"@{account}: Timeout loading post {post_url} "
                    f"(attempt {attempt + 1}/{max_retries + 1}). Retrying..."
                )
                time.sleep(INSTAGRAM_RETRY_DELAY / 1000)
                continue
            else:
                logger.error(
                    f"@{account}: Failed to load post {post_url} "
                    f"after {max_retries + 1} attempts: {e}"
                )
                return None
        except (ValueError, OSError) as e:
            logger.error(f"@{account}: System error loading post {post_url}: {e}")
            return None
        except Exception as e:
            logger.error(f"@{account}: Unexpected error loading post {post_url}: {e}")
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
            timeout=BROWSER_LOAD_TIMEOUT,
        )
        time.sleep(INSTAGRAM_ACCOUNT_LOAD_DELAY / 1000)
    except PlaywrightTimeoutError as e:
        logger.error(f"@{account}: Failed to load account page: {e}")
        return []
    except (ValueError, OSError) as e:
        logger.error(f"@{account}: System error loading account page: {e}")
        return []
    except Exception as e:
        logger.error(f"@{account}: Unexpected error loading account page: {e}")
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
                f"@{account}: Found post older than cutoff date, "
                f"stopping for this account."
            )
            break

    logger.info(f"@{account}: Found {len(account_posts)} recent post(s).")
    return account_posts
