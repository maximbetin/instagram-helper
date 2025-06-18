"""Instagram browser launcher with post fetching."""

import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import Page, sync_playwright

from config import *
from utils import logger


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


def get_post_caption(page: Page) -> str:
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


def get_post_date(page: Page, post_url: Optional[str] = None) -> Optional[str]:
    """Extract post date from Instagram post page."""
    try:
        if post_url:
            logger.debug(f"Date extraction for: {post_url}")
            # Navigate to post if URL provided
            page.goto(post_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
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


def get_account_posts_urls(page: Page) -> List[str]:
    """Extract post URLs from account page."""
    for selector in HTML_SELECTORS['post']:
        try:
            links = page.query_selector_all(selector)
            if links:
                post_urls = []
                for link in links[:INSTAGRAM_MAX_POSTS_PER_ACCOUNT]:
                    try:
                        post_url = link.get_attribute('href')
                        if post_url and any(path in post_url for path in ['/p/', '/reel/', '/tv/']):
                            full_url = (f"https://www.instagram.com{post_url}" if post_url.startswith('/') else post_url)
                            post_urls.append(full_url)
                    except Exception as e:
                        logger.debug(f"Error extracting URL from post: {e}")
                        continue
                return post_urls
        except Exception:
            continue
    return []


def get_account_posts(page: Page, account: str, cutoff_date: datetime) -> List[Dict]:
    """Fetch recent posts from a specific Instagram account."""
    post_urls = get_account_posts_urls(page)
    if not post_urls:
        logger.warning(f"No posts found for account @{account}")
        return []

    recent_posts = []
    posts_checked = 0
    posts_too_old = 0

    for post_url in post_urls:
        if posts_checked >= INSTAGRAM_MAX_POSTS_PER_ACCOUNT:
            logger.debug(f"Reached maximum post check limit for account @{account}")
            break

        try:
            posts_checked += 1

            # Quick date check first
            post_date_str = get_post_date(page, post_url)

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
            post_data['caption'] = get_post_caption(page)
            post_data['date_posted'] = post_date_str  # Use the date we already extracted

            # Double-check the date after full processing (only if we didn't get a date initially)
            if not post_data.get('date_posted'):
                fallback_date = get_post_date(page)  # Try again without URL since we're already on the page
                post_data['date_posted'] = fallback_date
                if fallback_date and not is_post_recent(fallback_date, cutoff_date):
                    # Since posts are usually ordered by date, stop processing more posts
                    # but keep the recent posts we already found
                    break

            recent_posts.append(post_data)
            time.sleep(1)

        except Exception as e:
            logger.warning(f"Error processing post {posts_checked}: {e}")
            continue

    return recent_posts


def generate_html_report(all_posts: Dict[str, List[Dict]], cutoff_date: datetime) -> str:
    """Generate a beautiful HTML report of fetched posts using template."""
    timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    filename = f"instagram_updates_{datetime.now().strftime('%d-%m-%Y')}.html"
    output_file = os.path.join(desktop_path, filename)

    date_range = f"{cutoff_date.strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')}"

    # Calculate stats excluding the special sorting key
    real_accounts = {k: v for k, v in all_posts.items() if k != '_all_sorted'}
    total_posts = sum(len(posts) for posts in real_accounts.values())

    all_posts_sorted = all_posts.get('_all_sorted', [])
    for post in all_posts_sorted:
        post['clean_url'] = post.get('url', '')

    for posts in real_accounts.values():
        for post in posts:
            post['clean_url'] = post.get('url', '')

    template_data = {
        'timestamp': timestamp,
        'date_range': date_range,
        'total_posts': total_posts,
        'posts_by_account': real_accounts,
        'all_posts_sorted': all_posts_sorted,
        'max_post_age': INSTAGRAM_MAX_POST_AGE,
        'total_accounts': len(INSTAGRAM_ACCOUNTS),
        'accounts_with_posts': len(real_accounts),
    }

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_content = template.render(**template_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")
    return output_file


def sort_posts_by_date(posts: List[Dict]) -> List[Dict]:
    """Sort posts by published date, newest first."""
    def get_sort_key(post):
        date_str = post.get('date_posted', '')
        if not date_str:
            return datetime.min.replace(tzinfo=TIMEZONE)

        parsed_date = parse_post_date(date_str)
        return parsed_date if parsed_date else datetime.min.replace(tzinfo=TIMEZONE)

    return sorted(posts, key=get_sort_key, reverse=True)


def get_all_posts(page: Page, cutoff_date: datetime) -> Dict[str, List[Dict]]:
    """Fetch posts from all configured accounts."""
    all_posts = []
    account_posts = {}

    for account in INSTAGRAM_ACCOUNTS:
        account_url = f"{INSTAGRAM_URL}{account}/"

        logger.info(f"Navigating to {account_url}...")
        page.goto(account_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
        time.sleep(BROWSER_LOAD_DELAY)

        logger.info(f"@{account}: Getting recent posts...")
        posts = get_account_posts(page, account, cutoff_date)
        logger.info(f"@{account}: Found {len(posts)} recent posts!")

        account_posts[account] = posts
        all_posts.extend(posts)

    # Sort all posts globally by date (newest first)
    all_posts_sorted = sort_posts_by_date(all_posts)

    # Store the globally sorted posts under a special key
    account_posts['_all_sorted'] = all_posts_sorted

    return account_posts


def main():
    try:
        with sync_playwright() as p:
            logger.info(f"Starting the browser at page {INSTAGRAM_URL}...")
            subprocess.Popen([BROWSER_PATH, f"--remote-debugging-port={BROWSER_DEBUG_PORT}", INSTAGRAM_URL])

            logger.info(f"Waiting {BROWSER_LOAD_DELAY} seconds for the browser to load the page...")
            time.sleep(BROWSER_LOAD_DELAY)

            logger.info(f"Connecting to the browser at port {BROWSER_DEBUG_PORT}...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{BROWSER_DEBUG_PORT}", timeout=10000)

            logger.info("Getting the current page content...")
            page = browser.contexts[0].pages[0]

            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=INSTAGRAM_MAX_POST_AGE)

            logger.info("Getting posts from all accounts...")
            all_posts = get_all_posts(page, cutoff_date)

            logger.info("Generating the HTML report...")
            report = generate_html_report(all_posts, cutoff_date)

            logger.info("Opening the HTML report...")
            os.startfile(report)

        logger.info("Done :)")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
