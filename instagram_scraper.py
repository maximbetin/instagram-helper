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
    SECONDS_IN_MS,
    TIMEZONE,
)
from utils import setup_logging

logger = setup_logging(__name__)


def debug_page_structure(page: Page, account: str) -> None:
    """Debug function to analyze the current page structure and help find the right selectors."""
    try:
        logger.debug(f"@{account}: === PAGE STRUCTURE DEBUG ===")
        
        # Check for common Instagram elements
        article_count = len(page.query_selector_all("article"))
        h1_count = len(page.query_selector_all("h1"))
        time_count = len(page.query_selector_all("time"))
        ul_count = len(page.query_selector_all("ul"))
        li_count = len(page.query_selector_all("li"))
        
        logger.debug(f"@{account}: Found {article_count} articles, {h1_count} h1 elements, {time_count} time elements")
        logger.debug(f"@{account}: Found {ul_count} ul elements, {li_count} li elements")
        
        # Look for elements that might contain captions
        caption_candidates = page.query_selector_all("h1, h2, h3, p, span, div")
        caption_texts = []
        
        for i, element in enumerate(caption_candidates[:10]):  # Check first 10 elements
            try:
                text = element.inner_text().strip()
                if text and len(text) > 10 and len(text) < 500:  # Reasonable caption length
                    tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                    caption_texts.append(f"{tag_name}: '{text[:100]}...'")
            except Exception:
                continue
        
        if caption_texts:
            logger.debug(f"@{account}: Potential caption elements:")
            for text in caption_texts[:5]:  # Show first 5
                logger.debug(f"@{account}:   {text}")
        
        # Look for time elements
        time_elements = page.query_selector_all("time")
        for i, time_elem in enumerate(time_elements[:3]):
            try:
                datetime_attr = time_elem.get_attribute("datetime")
                text_content = time_elem.inner_text().strip()
                logger.debug(f"@{account}: Time element {i+1}: datetime='{datetime_attr}', text='{text_content}'")
            except Exception as e:
                logger.debug(f"@{account}: Could not read time element {i+1}: {e}")
        
        # Save page HTML for manual analysis if debug is enabled
        try:
            import os
            from datetime import datetime
            
            debug_dir = os.path.join(os.getcwd(), "debug_html")
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{account}_{timestamp}.html"
            filepath = os.path.join(debug_dir, filename)
            
            html_content = page.content()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logger.debug(f"@{account}: Saved debug HTML to: {filepath}")
        except Exception as e:
            logger.debug(f"@{account}: Failed to save debug HTML: {e}")
        
        logger.debug(f"@{account}: === END DEBUG ===")
        
    except Exception as e:
        logger.debug(f"@{account}: Debug function failed: {e}")


def _handle_scraping_error(
    account: str, operation: str, error: Exception, retry_attempt: Optional[int] = None
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
    elif isinstance(error, (ValueError, OSError)):
        logger.error(f"@{account}: System error during {operation}: {error}")
    else:
        logger.error(f"@{account}: Unexpected error during {operation}: {error}")


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
                if post_url and any(path in post_url for path in ["/p/", "/reel/"]):
                    if post_url.startswith("/"):
                        full_url = f"{INSTAGRAM_URL.rstrip('/')}{post_url}"
                    else:
                        full_url = post_url

                    full_url = full_url.split("?")[0].rstrip("/")

                    if full_url not in seen_urls:
                        post_urls.append(full_url)
                        seen_urls.add(full_url)
                        logger.debug(f"Found post URL: {full_url}")
            
            # If we found posts with this selector, no need to try others
            if post_urls:
                break
                
        except Exception as e:
            logger.debug(f"Selector {selector} failed: {e}")
            continue

    logger.info(f"Total unique post URLs found: {len(post_urls)}")
    return post_urls


def get_post_caption(page: Page) -> str:
    """Extract post's caption from Instagram post."""
    # Try multiple selectors for caption - Instagram changes their HTML structure frequently
    caption_selectors = [
        # Based on the xPath you provided: /html/body/div[7]/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div[1]/li/div/div/div[2]/div[1]/h1
        "article div div div div div ul div li div div div div h1",  # More specific path
        "article div div div div div ul div li div div div div h1",  # Simplified version
        "article ul div li div div div div h1",  # Even more simplified
        "article ul li div div div div h1",  # Further simplified
        "article div div div div h1",  # Generic article path
        "div[role='button'] h1",  # More specific h1 within button
        "article h1",  # h1 within article
        "div[data-testid='post-caption'] h1",  # Instagram's test ID
        "div[data-testid='post-caption'] span",  # Alternative caption format
        "article div[role='button'] h1",  # h1 within button in article
        "div[data-testid='post-caption'] div",  # Another caption format
        "h1",  # Generic h1 (fallback)
    ]
    
    # Also try to find elements by looking for text that looks like a caption
    try:
        # Look for elements with substantial text content that might be captions
        all_elements = page.query_selector_all("*")
        for element in all_elements:
            try:
                text = element.inner_text().strip()
                # Look for text that's likely a caption (substantial length, not just navigation)
                if (text and 
                    10 < len(text) < 1000 and 
                    not any(skip in text.lower() for skip in ['follow', 'like', 'comment', 'share', 'save', 'more'])):
                    
                    tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                    # If it's an h1, h2, h3, p, or span, it's more likely to be a caption
                    if tag_name in ['h1', 'h2', 'h3', 'p', 'span', 'div']:
                        logger.debug(f"Found potential caption in {tag_name}: '{text[:100]}...'")
                        return text
            except Exception:
                continue
    except Exception as e:
        logger.debug(f"Alternative caption search failed: {e}")
    
    for selector in caption_selectors:
        try:
            caption_element = page.query_selector(selector)
            if caption_element and caption_element.inner_text().strip():
                caption = caption_element.inner_text().strip()
                logger.debug(f"Found caption using selector: {selector}")
                return caption
        except Exception as e:
            logger.debug(f"Selector {selector} failed: {e}")
            continue
    
    logger.warning("Could not find post caption with any selector")
    return ""


def get_post_date(page: Page) -> Optional[datetime]:
    """Extract post's date from Instagram post page."""
    # Try multiple selectors for date - Instagram changes their HTML structure frequently
    date_selectors = [
        "time[datetime]",  # Standard time element with datetime attribute
        "time",  # Any time element
        "a[href*='/p/'] time[datetime]",  # Time within post link
        "article time[datetime]",  # Time within article
        "div[data-testid='post-timestamp'] time[datetime]",  # Instagram's test ID
        "div[data-testid='post-timestamp']",  # Alternative timestamp format
    ]
    
    for selector in date_selectors:
        try:
            date_element = page.query_selector(selector)
            if date_element:
                # Try to get datetime attribute first
                datetime_attr = date_element.get_attribute("datetime")
                if datetime_attr:
                    utc_datetime = datetime.fromisoformat(datetime_attr.replace("Z", "+00:00"))
                    logger.debug(f"Found date using selector: {selector}")
                    return utc_datetime.astimezone(TIMEZONE)
                
                # Fallback: try to get text content and parse it
                date_text = date_element.inner_text().strip()
                if date_text:
                    logger.debug(f"Found date text using selector {selector}: {date_text}")
                    # You might need to add date parsing logic here for text-based dates
        except Exception as e:
            logger.debug(f"Date selector {selector} failed: {e}")
            continue
    
    logger.warning("Could not find post date with any selector")
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
            time.sleep(INSTAGRAM_POST_LOAD_DELAY / SECONDS_IN_MS)

            # Debug: Log the current page structure for troubleshooting
            if attempt == 0:  # Only log on first attempt to avoid spam
                debug_page_structure(page, account)

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
        except (ValueError, OSError) as e:
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
            timeout=BROWSER_LOAD_TIMEOUT,
        )
        time.sleep(INSTAGRAM_ACCOUNT_LOAD_DELAY / SECONDS_IN_MS)
    except PlaywrightTimeoutError as e:
        _handle_scraping_error(account, "loading account page", e)
        return []
    except (ValueError, OSError) as e:
        _handle_scraping_error(account, "loading account page", e)
        return []
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
