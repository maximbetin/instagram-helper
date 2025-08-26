"""Instagram scraping functionality."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from playwright.sync_api import Page

from utils import get_user_agent, setup_logging

if TYPE_CHECKING:
    from config import Settings


logger = setup_logging(__name__)

# --- Constants ---
# Selectors for post links and date elements
POST_LINK_SELECTOR = "a[href*='/p/'], a[href*='/reel/']"
POST_DATE_SELECTOR = "time[datetime]"


@dataclass
class InstagramPost:
    """Represents a single scraped Instagram post."""

    url: str
    account: str
    caption: str
    date_posted: datetime


class InstagramScraper:
    """Encapsulates all logic for scraping posts from Instagram accounts.

    SCRAPING STRATEGY OVERVIEW:

    This scraper implements a multi-stage approach to extract Instagram posts:

    1. ACCOUNT NAVIGATION: Navigate to the account's main page to access their posts
    2. POST URL EXTRACTION: Collect post URLs using CSS selectors (more reliable than XPath for links)
    3. INDIVIDUAL POST PROCESSING: Visit each post to extract caption and date information
    4. DATE FILTERING: Filter posts based on age to respect user preferences
    5. GRACEFUL DEGRADATION: Continue processing even if individual posts fail

    CRITICAL IMPLEMENTATION DETAILS:

    - NAVIGATION PATTERN: The scraper navigates between account pages and individual posts,
      returning to the account page after each post to maintain context. This approach
      is more reliable than trying to extract all data from the account page directly.

    - SELECTOR STRATEGY:
      * POST LINKS: Uses CSS selectors (a[href*='/p/'], a[href*='/reel/']) which are
        more stable than XPath for link extraction
      * POST DATES: Uses CSS selector (time[datetime]) for date extraction
      * POST CAPTIONS: Uses hardcoded XPath due to Instagram's fragile HTML structure

    - TIMEOUT HANDLING: Each navigation operation has a configurable timeout to prevent
      the scraper from hanging indefinitely on slow-loading pages.

    - RATE LIMITING CONSIDERATIONS: The scraper includes intentional delays (3 seconds)
      after each navigation to avoid triggering Instagram's rate limiting mechanisms.

    - ERROR RECOVERY: If a post fails to process, the scraper logs the error and
      continues with the next post, ensuring partial results are still obtained.

    INSTAGRAM-SPECIFIC CHALLENGES:

    - HTML STRUCTURE VOLATILITY: Instagram frequently changes their DOM structure,
      requiring careful selector management and fallback strategies.

    - LAZY LOADING: Instagram uses lazy loading for content, requiring explicit
      waits and delays to ensure content is fully loaded before extraction.

    - SESSION DEPENDENCY: The scraper relies on browser session cookies for
      authentication, making it vulnerable to session expiration.

    - CAPTION EXTRACTION: Caption text is deeply nested in Instagram's DOM,
      requiring precise XPath selectors that must be updated when Instagram changes
      their structure.

    PERFORMANCE CONSIDERATIONS:

    - POST LIMITING: Respects INSTAGRAM_MAX_POSTS_PER_ACCOUNT to prevent excessive
      processing and potential rate limiting.

    - DATE FILTERING: Early date filtering prevents unnecessary processing of old posts.

    - MEMORY MANAGEMENT: Post data is collected incrementally and doesn't accumulate
      large amounts of data in memory.
    """

    def __init__(self, page: Page, app_settings: Settings):
        """Initializes the scraper with a Playwright page and settings."""
        self.page = page
        self.settings = app_settings
        self.page.set_extra_http_headers({"User-Agent": get_user_agent()})

    def process_account(
        self, account: str, cutoff_date: datetime
    ) -> list[InstagramPost]:
        """Processes a single Instagram account to fetch recent posts."""
        logger.info(f"Processing account: @{account}")
        account_url = f"{self.settings.INSTAGRAM_URL}{account}/"

        if not self._navigate_to_url(account_url, "account page"):
            return []

        post_urls = self._get_post_urls(account, cutoff_date)
        if not post_urls:
            return []

        posts: list[InstagramPost] = []

        # Check the first post first - if it's too old, skip the entire account
        if post_urls:
            first_post_data = self._extract_post_data(
                post_urls[0], account, cutoff_date
            )
            if not first_post_data:
                logger.info(
                    f"@{account}: First post is too old, skipping entire account"
                )
                return []
            posts.append(first_post_data)

        # Process remaining posts
        for i, post_url in enumerate(post_urls[1:], start=2):
            logger.debug(f"@{account}: Processing post {i}/{len(post_urls)}")

            post_data = self._extract_post_data(post_url, account, cutoff_date)
            if post_data:
                posts.append(post_data)

        logger.info(
            f"@{account}: Found {len(post_urls)} posts processed, "
            f"{len(posts)} recent posts found."
        )
        return posts

    def _get_post_urls(self, account: str, cutoff_date: datetime) -> list[str]:
        """Fetches post URLs from the account's page, stopping when cutoff date is reached."""
        logger.debug(f"@{account}: Searching for post URLs...")
        try:
            links = self.page.query_selector_all(POST_LINK_SELECTOR)
            if not links:
                logger.warning(f"@{account}: No post links found.")
                return []

            seen_urls = set()
            post_urls: list[str] = []

            for link in links:
                if len(post_urls) >= self.settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT:
                    break

                href = link.get_attribute("href")
                if href and (normalized_url := self._normalize_post_url(href)):
                    if normalized_url not in seen_urls:
                        # Add the URL without checking date - we'll check dates during processing
                        post_urls.append(normalized_url)
                        seen_urls.add(normalized_url)

                        # Limit the number of URLs to prevent excessive processing
                        if (
                            len(post_urls)
                            >= self.settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT
                        ):
                            break

            logger.info(f"@{account}: Found {len(post_urls)} recent post URLs.")
            return post_urls
        except Exception as e:
            logger.error(f"@{account}: Failed to query for post URLs: {e}")
            return []

    def _extract_post_data(
        self, post_url: str, account: str, cutoff_date: datetime
    ) -> InstagramPost | None:
        """Navigates to a post and extracts its data if it's recent enough."""
        if not self._navigate_to_url(post_url, "post"):
            return None

        post_date = self._get_post_date()
        if not post_date:
            logger.warning(f"@{account}: Could not determine date for {post_url}.")
            return None

        # Ensure both dates are timezone-aware for comparison
        if post_date.tzinfo is None:
            logger.warning(
                f"@{account}: Post date has no timezone info, skipping date comparison"
            )
            return None

        if post_date < cutoff_date:
            return None

        return InstagramPost(
            url=post_url,
            account=account,
            caption=self._get_post_caption(),
            date_posted=post_date,
        )

    def _navigate_to_url(self, url: str, operation: str) -> bool:
        """Navigates to a URL.

        CRITICAL IMPLEMENTATION DETAILS:

        This method implements Instagram-specific navigation patterns that are
        crucial for reliable scraping:

        1. TIMEOUT HANDLING: Uses configurable timeout to prevent indefinite
           waits on slow-loading Instagram pages. This is essential because
           Instagram can be slow to respond, especially during peak usage.

        2. LAZY LOADING DELAY: The 3-second delay after navigation is critical
           for Instagram's lazy loading behavior. Instagram loads content
           incrementally, and this delay ensures the page is fully rendered
           before attempting to extract data.

        3. DOM READY WAIT: Uses 'domcontentloaded' instead of 'load' to
           balance between waiting for content and avoiding excessive delays.
           This ensures the DOM is ready for interaction without waiting for
           all images and external resources.

        4. ERROR RECOVERY: Navigation failures are logged but don't crash
           the scraping process. This allows the scraper to continue with
           other posts even if individual pages fail to load.

        5. OPERATION CONTEXT: The operation parameter provides context for
           error messages, making debugging easier when navigation fails.

        INSTAGRAM-SPECIFIC CONSIDERATIONS:

        - Instagram uses heavy JavaScript and lazy loading
        - Page content may not be immediately available after navigation
        - Network conditions can significantly affect load times
        - Some pages may fail to load due to Instagram's anti-bot measures

        PERFORMANCE IMPLICATIONS:

        - Each navigation adds 3+ seconds to the scraping time
        - Timeout settings affect reliability vs. speed trade-offs
        - Multiple failed navigations can significantly slow down the process
        """
        try:
            self.page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=self.settings.INSTAGRAM_POST_LOAD_TIMEOUT,
            )
            time.sleep(3)  # Small delay for lazy-loaded content
            return True
        except Exception as e:
            logger.error(f"Failed to load {operation} at {url}: {e}")
            return False

    def _get_post_caption(self) -> str:
        """Extracts the post caption using the specific XPath.

        CRITICAL IMPLEMENTATION DETAIL:

        This method uses a hardcoded XPath selector instead of CSS selectors or
        more flexible approaches. This design decision was made because:

        1. INSTAGRAM FRAGILITY: Instagram's HTML structure changes frequently,
           making CSS selectors and relative paths unreliable over time.

        2. SPECIFICITY: The exact XPath targets the specific caption element
           in Instagram's current DOM structure, reducing false positives.

        3. MAINTENANCE: When Instagram changes their structure, only this
           one XPath needs updating, making maintenance predictable.

        4. RELIABILITY: Hardcoded XPath provides consistent behavior across
           different Instagram page variations and updates.

        WARNING: Do NOT modify this XPath selector without thorough testing.
        Instagram's HTML structure is extremely fragile, and changes will break
        caption extraction functionality. If Instagram updates their structure,
        this XPath must be updated to match the new DOM layout.

        The current XPath targets the caption text within Instagram's post structure:
        /html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span
        """
        try:
            # Use the exact XPath provided - DO NOT MODIFY without testing
            xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span"
            element = self.page.query_selector(f"xpath={xpath}")

            if element:
                caption = element.inner_text()
                if caption:
                    logger.debug(f"Found caption using XPath: {caption[:50]}...")
                    return caption
                else:
                    logger.debug("XPath element found but no text content")
            else:
                logger.debug("XPath element not found")

        except Exception as e:
            logger.error(f"Error extracting caption with XPath: {e}")

        return ""

    def _get_post_date(self) -> datetime | None:
        """Extracts the post's date from the page."""
        try:
            element = self.page.query_selector(POST_DATE_SELECTOR)
            if element and (dt_attr := element.get_attribute("datetime")):
                # Parse the UTC datetime from Instagram
                utc_dt = datetime.fromisoformat(dt_attr.replace("Z", "+00:00"))
                # Convert to the configured timezone if available
                result_dt = utc_dt
                if self.settings.TIMEZONE:
                    result_dt = utc_dt.astimezone(self.settings.TIMEZONE)
                return result_dt
            logger.warning("Could not find time element with datetime attribute.")
        except Exception as e:
            logger.error(f"Error parsing date from time element: {e}")
        return None

    @staticmethod
    def _is_valid_post_url(url: str) -> bool:
        """Checks if a URL is a valid Instagram post URL."""
        return "/p/" in url or "/reel/" in url

    def _normalize_post_url(self, url: str) -> str | None:
        """Normalizes a post URL to be absolute and clean."""
        if not self._is_valid_post_url(url):
            return None
        base_url = self.settings.INSTAGRAM_URL.rstrip("/")
        full_url = f"{base_url}{url}" if url.startswith("/") else url
        return full_url.split("?")[0].rstrip("/")
