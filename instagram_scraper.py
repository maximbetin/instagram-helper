"""Instagram scraping functionality."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
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
    """Encapsulates all logic for scraping posts from Instagram accounts."""

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
        for i, post_url in enumerate(post_urls):
            logger.debug(f"@{account}: Processing post {i + 1}/{len(post_urls)}")

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

    def _get_post_date_from_url(self, post_url: str) -> datetime | None:
        """Quickly extracts the post date without full navigation."""
        try:
            # Navigate to the post
            if not self._navigate_to_url(post_url, "post date check"):
                return None

            # Get the date
            post_date = self._get_post_date()

            # Go back to the account page - extract account name from post URL
            if "/p/" in post_url:
                account_part = post_url.split("/p/")[0]
            elif "/reel/" in post_url:
                account_part = post_url.split("/reel/")[0]
            else:
                return post_date  # Can't determine account, just return the date

            account_name = account_part.split("/")[-1]
            account_url = f"{self.settings.INSTAGRAM_URL}{account_name}/"
            self._navigate_to_url(account_url, "account page return")

            return post_date
        except Exception as e:
            logger.debug(f"Failed to get date for {post_url}: {e}")
            return None

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
        """Navigates to a URL."""
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
        """Extracts the post caption using the specific XPath."""
        try:
            # Use the exact XPath provided
            xpath = "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span"
            element = self.page.query_selector(f"xpath={xpath}")

            if element:
                caption = element.text_content()
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
                # Convert to the configured timezone
                if self.settings.TIMEZONE:
                    return utc_dt.astimezone(self.settings.TIMEZONE)
                return utc_dt
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
