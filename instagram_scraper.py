"""Instagram scraping functionality."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PWTimeoutError

from utils import setup_logging

if TYPE_CHECKING:
    from config import Settings

logger = setup_logging(__name__)

# --- Selectors ---------------------------------------------------------------

# Links to individual posts (grid & reels)
POST_LINK_SELECTOR = "a[href*='/p/'], a[href*='/reel/']"
# Time element inside a post
POST_DATE_SELECTOR = "time[datetime]"

# Primary (fragile) XPath for caption — keep as first try; see fallbacks below.
CAPTION_XPATH = (
    "/html/body/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div[1]/section/main/"
    "div/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div[2]/div/span/div/span"
)


# --- Data model --------------------------------------------------------------


@dataclass
class InstagramPost:
    url: str
    account: str
    caption: str
    date_posted: datetime


# --- Scraper ----------------------------------------------------------------


class InstagramScraper:
    """Scrape posts for one or more Instagram accounts using a Playwright Page.

    Notes:
    - Set the browser context user agent when creating the context
      (e.g. `browser.new_context(user_agent=...)`). Do not rely on
      `set_extra_http_headers` for User-Agent overrides.
    - This class uses Playwright's Locator API and targeted waits instead of sleeps.
    """

    def __init__(self, page: Page, app_settings: Settings):
        self.page = page
        self.settings = app_settings

    # ---- Public -------------------------------------------------------------

    def process_account(
        self, account: str, cutoff_date: datetime
    ) -> list[InstagramPost]:
        """Fetch recent posts for a single account."""
        logger.info(f"Processing account: @{account}")
        account_url = f"{self.settings.INSTAGRAM_URL.rstrip('/')}/{account}/"

        if not self._navigate_to_url(account_url, "account page"):
            return []

        post_urls = self._get_post_urls(account, cutoff_date)
        if not post_urls:
            return []

        posts: list[InstagramPost] = []
        old_streak = 0
        max_old_streak = 3  # stop early after this many consecutive old posts

        for i, post_url in enumerate(post_urls, start=1):
            logger.debug(f"@{account}: Processing post {i}/{len(post_urls)}")
            post = self._extract_post_data(post_url, account, cutoff_date)
            if post:
                posts.append(post)
                old_streak = 0
            else:
                old_streak += 1
                if old_streak >= max_old_streak:
                    logger.debug(
                        f"@{account}: Stopping early after {old_streak} old posts in a row"
                    )
                    break

        logger.info(
            f"@{account}: Processed {len(post_urls)} URLs, {len(posts)} recent posts found."
        )
        return posts

    # ---- Internals ----------------------------------------------------------

    def _get_post_urls(self, account: str, cutoff_date: datetime) -> list[str]:
        """Collect post URLs from the account page (with light scrolling)."""
        logger.debug(f"@{account}: Collecting post URLs...")
        try:
            urls = self._collect_links(self.settings.INSTAGRAM_MAX_POSTS_PER_ACCOUNT)
            logger.info(f"@{account}: Found {len(urls)} candidate post URLs.")
            return urls
        except Exception as e:
            logger.error(f"@{account}: Failed to collect post URLs: {e}")
            return []

    def _collect_links(self, max_links: int) -> list[str]:
        """Scroll the grid a bit to collect up to max_links post URLs."""
        loc = self.page.locator(POST_LINK_SELECTOR)
        seen: set[str] = set()

        # Initially wait for at least one link (short timeout to avoid hanging)
        try:
            self.page.wait_for_selector(POST_LINK_SELECTOR, timeout=3_000)
        except PWTimeoutError:
            return []

        # Perform a few scroll steps to surface more posts
        last_count = -1
        for _ in range(10):  # safety cap
            count = loc.count()
            if count == last_count or count >= max_links:
                break
            last_count = count
            self.page.mouse.wheel(0, 2000)
            self.page.wait_for_timeout(350)

        # Extract hrefs
        urls: list[str] = []
        count = min(loc.count(), max_links)
        for i in range(count):
            href = loc.nth(i).get_attribute("href")
            if not href:
                continue
            n = self._normalize_post_url(href)
            if n and n not in seen:
                urls.append(n)
                seen.add(n)
                if len(urls) >= max_links:
                    break
        return urls

    def _extract_post_data(
        self, post_url: str, account: str, cutoff_date: datetime
    ) -> InstagramPost | None:
        """Open a post URL; return data if recent enough."""
        if not self._navigate_to_url(post_url, "post"):
            return None

        post_date = self._get_post_date()
        if not post_date:
            logger.warning(f"@{account}: No date for {post_url}")
            return None

        if post_date.tzinfo is None:
            logger.warning(f"@{account}: Post date is naive (no tz): {post_url}")
            return None

        if post_date < cutoff_date:
            return None

        caption = self._get_post_caption()
        return InstagramPost(
            url=post_url, account=account, caption=caption, date_posted=post_date
        )

    def _navigate_to_url(self, url: str, operation: str) -> bool:
        """Navigate with targeted waits, minimal retries, and basic walls handling."""
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                resp = self.page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=self.settings.INSTAGRAM_POST_LOAD_TIMEOUT,
                )
                if resp and resp.status >= 400:
                    logger.warning(f"{operation} HTTP {resp.status} at {url}")

                # Handle consent/login walls if they appear
                self._dismiss_consent_if_present()
                if self._is_login_page():
                    logger.error("Login page detected; session is not authenticated.")
                    return False

                # Basic content readiness
                try:
                    self.page.wait_for_selector("main", timeout=3_000)
                except PWTimeoutError:
                    pass  # not fatal

                return True
            except Exception as e:
                logger.error(
                    f"Attempt {attempt}/{attempts}: failed to load {operation} at {url}: {e}"
                )
                if attempt < attempts:
                    self.page.wait_for_timeout(1_000 * attempt)
        return False

    def _dismiss_consent_if_present(self) -> None:
        """Dismiss common consent dialogs if present (best-effort)."""
        try:
            btn = self.page.locator(
                "button:has-text('Only allow essential') , "
                "button:has-text('Allow all') , "
                "button:has-text('Accept all') , "
                "button:has-text('Accept')"
            )
            if btn.count():
                btn.first.click(timeout=1_000)
        except PWTimeoutError:
            pass
        except Exception:
            pass

    def _is_login_page(self) -> bool:
        """Heuristic: detect login screen."""
        loc = self.page.locator("input[name='username'], input[name='password']")
        return loc.count() >= 2

    def _get_post_caption(self) -> str:
        """Try fragile XPath first, then fall back to safer heuristics."""
        # 1) Primary XPath (keep first to preserve existing behavior)
        try:
            el = self.page.locator(f"xpath={CAPTION_XPATH}")
            if el.count():
                text = el.first.inner_text().strip()
                if text:
                    logger.debug("Caption extracted via primary XPath.")
                    return text
        except Exception as e:
            logger.debug(f"Primary XPath caption extraction failed: {e}")

        # 2) Fallbacks (heuristics; keep conservative to avoid unrelated text)
        candidates = [
            "article section span[dir='auto']",
            "div[role='dialog'] article span[dir='auto']",
            "article h1, article h2",
        ]
        for sel in candidates:
            try:
                loc = self.page.locator(sel).first
                if loc.count():
                    text = loc.inner_text().strip()
                    if text:
                        logger.debug(f"Caption extracted via fallback selector: {sel}")
                        return text
            except Exception:
                continue

        logger.debug("Caption not found; returning empty string.")
        return ""

    def _get_post_date(self) -> datetime | None:
        """Extract the post's datetime and convert to configured timezone if set."""
        try:
            el = self.page.locator(POST_DATE_SELECTOR).first
            if not el.count():
                logger.warning("No time[datetime] element.")
                return None

            dt_raw = el.get_attribute("datetime") or ""
            try:
                utc_dt = datetime.fromisoformat(dt_raw.replace("Z", "+00:00"))
            except Exception:
                logger.warning(f"Unrecognized datetime format: {dt_raw!r}")
                return None

            if getattr(self.settings, "TIMEZONE", None):
                return utc_dt.astimezone(self.settings.TIMEZONE)
            return utc_dt
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return None

    # ---- URL helpers --------------------------------------------------------

    @staticmethod
    def _is_valid_post_url(url: str) -> bool:
        return "/p/" in url or "/reel/" in url

    def _normalize_post_url(self, url: str) -> str | None:
        if not self._is_valid_post_url(url):
            return None
        base = self.settings.INSTAGRAM_URL.rstrip("/")
        full = f"{base}{url}" if url.startswith("/") else url
        return full.split("?")[0].rstrip("/")
