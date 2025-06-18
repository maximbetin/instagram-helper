"""Instagram browser launcher with post fetching."""

import os
import re
import subprocess
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import Page, sync_playwright

from config import *
from utils import logger


def get_cutoff_date() -> datetime:
    """Get the cutoff date for filtering posts."""
    current_time = datetime.now(TIMEZONE)
    cutoff = current_time - timedelta(days=INSTAGRAM_MAX_POST_AGE)
    logger.debug(f"Current time: {current_time}")
    logger.debug(f"Cutoff date ({INSTAGRAM_MAX_POST_AGE} days back): {cutoff}")
    return cutoff


def parse_post_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a post date string into a datetime object."""
    if not date_str:
        return None

    try:
        if 'UTC' in date_str and '+' in date_str:
            cleaned_date = date_str.replace(' UTC', '')
            dt = datetime.fromisoformat(cleaned_date)
            result = dt.astimezone(TIMEZONE)
            return result

            # Try parsing ISO format (from datetime attribute)
        if 'T' in date_str and ('Z' in date_str or '+' in date_str):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            result = dt.astimezone(TIMEZONE)
            return result

        # Try parsing other common formats
        formats = [
            '%Y-%m-%d %H:%M:%S %Z',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S UTC%z',  # Handle UTC+01:00 format
            '%B %d, %Y',
            '%d %B %Y',
        ]

        for fmt in formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                # If no timezone info, assume Madrid timezone
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=TIMEZONE)
                result = parsed.astimezone(TIMEZONE)
                return result
            except ValueError as e:
                continue

    except Exception as e:
        logger.debug(f"Could not parse date '{date_str}': {e}")

    return None


def is_post_recent(date_str: Optional[str], cutoff_date: datetime) -> bool:
    """Check if a post date is within the recent timeframe."""
    if not date_str:
        # If we can't parse the date, assume it might be recent and check it
        return True

    post_date = parse_post_date(date_str)
    if not post_date:
        # If we can't parse the date, assume it might be recent and check it
        return True
    return post_date >= cutoff_date


def check_if_logged_in(page: Page) -> bool:
    """Check if user is properly logged into Instagram."""
    try:
        time.sleep(2)  # Wait for page to stabilize

        # Check for logged-in indicators
        for selector in HTML_SELECTORS['login_indicators']:
            try:
                if page.query_selector(selector):
                    return True
            except Exception:
                continue

        # Check if we're on the login page
        for selector in HTML_SELECTORS['login_page_indicators']:
            try:
                if page.query_selector(selector):
                    return False
            except Exception:
                continue

        return True  # Assume logged in if we can't determine

    except Exception as e:
        logger.warning(f"Error checking login status: {e}")
        if ERROR_EXECUTION_CONTEXT in str(e):
            logger.info("Page is navigating, waiting for it to stabilize...")
            time.sleep(3)
            try:
                page.wait_for_selector('body', timeout=5000)
                return True
            except Exception:
                return False
        return False


def extract_caption(page: Page) -> str:
    """Extract caption from Instagram post."""
    for selector in HTML_SELECTORS['caption']:
        try:
            caption_element = page.query_selector(selector)
            if caption_element:
                caption_text = caption_element.inner_text().strip()
                if caption_text and len(caption_text) > 5:
                    return caption_text
        except Exception as e:
            if ERROR_EXECUTION_CONTEXT in str(e):
                logger.warning("Execution context destroyed while extracting caption")
                break
            continue
    return ''


def extract_post_date(page: Page, post_url: Optional[str] = None) -> Optional[str]:
    """Extract post date from Instagram post page."""
    try:
        if post_url:
            logger.debug(f"Date extraction for: {post_url}")
            # Navigate to post if URL provided
            page.goto(post_url, wait_until="domcontentloaded", timeout=TIMEOUT_POST_NAVIGATION)
            time.sleep(1)  # Brief wait for content

        # Try to extract date from current page
        for selector in HTML_SELECTORS['date']:
            try:
                date_element = page.query_selector(selector)
                if not date_element:
                    continue

                # Try datetime attribute first
                datetime_attr = date_element.get_attribute('datetime')
                if datetime_attr:
                    try:
                        dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        dt_madrid = dt.astimezone(TIMEZONE)
                        return dt_madrid.strftime('%Y-%m-%d %H:%M:%S %Z')
                    except Exception:
                        return datetime_attr

                # Try title attribute
                title_attr = date_element.get_attribute('title')
                if title_attr:
                    return title_attr

                # Try inner text
                inner_text = date_element.inner_text().strip()
                if inner_text and re.search(r'\d{4}', inner_text):
                    return inner_text

            except Exception as e:
                if ERROR_EXECUTION_CONTEXT in str(e):
                    logger.warning("Execution context destroyed while extracting date")
                    break
                continue

        return None

    except Exception as e:
        logger.debug(f"Date extraction failed: {e}")
        return None


def create_base_post_data(account: str, post_url: str) -> Dict:
    """Create base post data structure."""
    return {
        'account': account,
        'url': post_url,
        'caption': '',
        'date_posted': '',
        'timestamp': datetime.now().isoformat()
    }


def extract_post_urls(page: Page, account: str) -> List[str]:
    """Extract post URLs from account page."""
    for selector in HTML_SELECTORS['post']:
        try:
            links = page.query_selector_all(selector)
            if links:
                logger.debug(f"Found {len(links)} posts using selector: {selector}")

                post_urls = []
                for link in links[:INSTAGRAM_MAX_POSTS_PER_ACCOUNT]:
                    try:
                        post_url = link.get_attribute('href')
                        if post_url and any(path in post_url for path in ['/p/', '/reel/', '/tv/']):
                            full_url = (f"https://www.instagram.com{post_url}"
                                        if post_url.startswith('/') else post_url)
                            post_urls.append(full_url)
                    except Exception as e:
                        logger.debug(f"Error extracting URL from post: {e}")
                        continue

                return post_urls
        except Exception:
            continue

    return []


def fetch_posts_from_account(page: Page, account: str) -> List[Dict]:
    """Fetch recent posts from a specific Instagram account."""
    try:
        url = f"https://www.instagram.com/{account}/"
        logger.info(f"Fetching recent posts from @{account}")

        cutoff_date = get_cutoff_date()
        logger.debug(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Navigate to account
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_ACCOUNT_NAVIGATION)
        except Exception as e:
            logger.error(f"Failed to navigate to @{account}: {e}")
            return []

        # Validate we're on the correct page
        if account not in page.url:
            logger.warning(f"Redirected away from @{account} to {page.url}")
            return []

        # Check login status
        if not check_if_logged_in(page):
            logger.error("Not properly logged in to Instagram")
            return []

        # Extract post URLs
        post_urls = extract_post_urls(page, account)
        if not post_urls:
            logger.warning(f"No post links found for @{account}")
            return []

        logger.info(f"Found {len(post_urls)} posts to check")

        # Process posts with date filtering
        recent_posts = []
        posts_checked = 0
        posts_too_old = 0

        for post_url in post_urls:
            if posts_checked >= INSTAGRAM_MAX_POSTS_PER_ACCOUNT:
                logger.debug(f"Reached maximum post check limit for @{account}")
                break

            try:
                posts_checked += 1
                logger.debug(f"Checking post {posts_checked}/{min(len(post_urls), INSTAGRAM_MAX_POSTS_PER_ACCOUNT)}")

                # Quick date check first
                post_date_str = extract_post_date(page, post_url)

                # Check if post is too old
                is_recent_post = is_post_recent(post_date_str, cutoff_date)

                if post_date_str:
                    parsed_date = parse_post_date(post_date_str)
                    if parsed_date:
                        is_recent_comparison = parsed_date >= cutoff_date

                if not is_recent_post:
                    posts_too_old += 1
                    # Since posts are usually ordered by date (newest first),
                    # if one post is outside our range, stop processing more posts
                    # but keep the recent posts we already found
                    break

                # Extract details from current page (already navigated by extract_post_date)
                post_data = create_base_post_data(account, post_url)
                post_data['caption'] = extract_caption(page)
                post_data['date_posted'] = post_date_str  # Use the date we already extracted

                # Double-check the date after full processing (only if we didn't get a date initially)
                if not post_data.get('date_posted'):
                    fallback_date = extract_post_date(page)  # Try again without URL since we're already on the page
                    post_data['date_posted'] = fallback_date
                    if fallback_date and not is_post_recent(fallback_date, cutoff_date):
                        # Since posts are usually ordered by date, stop processing more posts
                        # but keep the recent posts we already found
                        break

                recent_posts.append(post_data)
                logger.debug(f"Added recent post (total: {len(recent_posts)})")

                time.sleep(1)  # Small delay between posts

            except Exception as e:
                logger.warning(f"Error processing post {posts_checked}: {e}")
                continue

        logger.info(f"@{account}: {len(recent_posts)} recent posts found ({posts_checked} checked, {posts_too_old} too old)")
        return recent_posts

    except Exception as e:
        logger.error(f"Error fetching posts from @{account}: {e}")
        return []


def display_posts_summary(posts_by_account: Dict[str, List[Dict]]) -> None:
    """Display a summary of fetched posts."""
    # Calculate stats excluding the special sorting key
    real_accounts = {k: v for k, v in posts_by_account.items() if k != '_all_sorted'}
    total_posts = sum(len(posts) for posts in real_accounts.values())
    cutoff_date = get_cutoff_date()
    current_time = datetime.now(TIMEZONE)

    logger.info("=== SUMMARY ===")
    logger.info(f"Date range: {cutoff_date.strftime('%Y-%m-%d')} to {current_time.strftime('%Y-%m-%d')} ({INSTAGRAM_MAX_POST_AGE} days)")
    logger.info(f"Accounts: {len(real_accounts)}/{len(INSTAGRAM_ACCOUNTS)} with posts | Total posts: {total_posts}")

    if real_accounts:
        logger.info("Posts by account:")
        for account, posts in real_accounts.items():
            logger.info(f"  @{account}: {len(posts)} posts")

    logger.info("=" * 15)


def get_desktop_path() -> str:
    """Get the path to the user's desktop directory."""
    return os.path.join(os.path.expanduser('~'), 'Desktop')


def generate_html_report(posts_by_account: Dict[str, List[Dict]], output_file: Optional[str] = None) -> str:
    """Generate a beautiful HTML report of fetched posts using template."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Generate filename with date format if not provided
    if output_file is None:
        date_checked = datetime.now().strftime('%Y%m%d')
        filename = f"instagram_updates_{date_checked}.html"
        output_file = os.path.join(get_desktop_path(), filename)

    # Prepare template data
    cutoff_date = get_cutoff_date()
    date_range = f"{cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"

    # Calculate stats excluding the special sorting key
    real_accounts = {k: v for k, v in posts_by_account.items() if k != '_all_sorted'}
    total_posts = sum(len(posts) for posts in real_accounts.values())

    # Prepare posts data with clean URLs
    all_posts_sorted = posts_by_account.get('_all_sorted', [])
    for post in all_posts_sorted:
        post['clean_url'] = post.get('url', '')

    # Also add clean URLs to individual account posts
    for posts in real_accounts.values():
        for post in posts:
            post['clean_url'] = post.get('url', '')

    template_data = {
        'timestamp': timestamp,
        'max_post_age': INSTAGRAM_MAX_POST_AGE,
        'date_range': date_range,
        'total_accounts': len(INSTAGRAM_ACCOUNTS),
        'accounts_with_posts': len(real_accounts),
        'total_posts': total_posts,
        'all_posts_sorted': all_posts_sorted,
        'posts_by_account': real_accounts
    }

    # Load and render template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_content = template.render(**template_data)

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")
    return output_file


def setup_browser_context(playwright_instance):
    """Set up browser and context with proper configuration."""
    browser = playwright_instance.chromium.launch(headless=False, args=BROWSER_ARGS)

    context = browser.new_context(
        viewport=BROWSER_VIEWPORT,
        user_agent=BROWSER_USER_AGENT,
        locale=BROWSER_LOCALE,
        timezone_id=BROWSER_TIMEZONE
    )

    return browser, context


def sort_posts_by_date(posts: List[Dict]) -> List[Dict]:
    """Sort posts by published date, newest first."""
    def get_sort_key(post):
        date_str = post.get('date_posted', '')
        if not date_str:
            return datetime.min.replace(tzinfo=TIMEZONE)

        parsed_date = parse_post_date(date_str)
        return parsed_date if parsed_date else datetime.min.replace(tzinfo=TIMEZONE)

    return sorted(posts, key=get_sort_key, reverse=True)


def fetch_all_posts(page: Page) -> Dict[str, List[Dict]]:
    """Fetch posts from all configured accounts."""
    posts_by_account = {}
    all_posts = []

    for account in INSTAGRAM_ACCOUNTS:
        posts = fetch_posts_from_account(page, account)
        if posts:
            posts_by_account[account] = posts
            all_posts.extend(posts)

        # Delay between accounts (except last one)
        if account != INSTAGRAM_ACCOUNTS[-1]:
            time.sleep(INSTAGRAM_DELAY_BETWEEN_ACCOUNTS)

    # Sort all posts globally by date (newest first)
    all_posts_sorted = sort_posts_by_date(all_posts)

    # Store the globally sorted posts under a special key
    posts_by_account['_all_sorted'] = all_posts_sorted

    return posts_by_account


def open_html_file(file_path: str) -> None:
    """Open HTML file in default browser."""
    try:
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            logger.info(f"Opening HTML report in default browser: {abs_path}")
            os.startfile(abs_path)
        else:
            logger.error(f"HTML file not found: {abs_path}")
    except Exception as e:
        logger.warning(f"Could not auto-open HTML file: {e}")
        logger.info(f"Please manually open: {os.path.abspath(file_path)}")


def main():
    """Open Instagram for login, then fetch posts from specified accounts."""
    try:
        logger.info("Opening Instagram main page...")

        with sync_playwright() as p:
            browser, context = setup_browser_context(p)
            page = context.new_page()

            logger.info("Navigating to Instagram...")
            page.goto(INSTAGRAM_URL, wait_until="domcontentloaded", timeout=TIMEOUT_MAIN_PAGE)

            logger.info("Please log in manually, press Enter to continue...")
            input()

            logger.info("User logged in, fetching posts from specified accounts...")

            # Fetch posts from all accounts
            posts_by_account = fetch_all_posts(page)

            # Display results and generate report
            display_posts_summary(posts_by_account)
            html_file = generate_html_report(posts_by_account)
            logger.info(f"HTML report saved to: {html_file}")

            # Close browser on completion
            logger.info("Closing browser...")
            context.close()
            browser.close()

            # Auto-open the HTML file
            open_html_file(html_file)

            logger.info("Done :)")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
