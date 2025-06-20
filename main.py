"""Instagram browser launcher with post fetching."""

import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import Browser, Page, sync_playwright

from config import *
from utils import logger


def get_account_post_urls(page: Page) -> List[str]:
    """Fetch all post URLs from a specific Instagram account page, preserving order."""
    post_urls = []  # Use a list to preserve order.
    seen_urls = set()  # Use a set for efficient duplicate checking.
    # Selectors for posts, reels, and tagged content might need updates if Instagram changes layout.
    # Using a broad selector and filtering is more robust than specific selectors that break often.
    links = page.query_selector_all('a')

    for link in links:
        post_url = link.get_attribute('href')
        if post_url and any(path in post_url for path in ['/p/', '/reel/']):
            # Clean up the URL for better mobile compatibility
            if post_url.startswith('/'):
                # Build a full, clean URL from a relative path
                full_url = f"{INSTAGRAM_URL.rstrip('/')}{post_url}"
            else:
                full_url = post_url

            # Remove trailing slashes and query parameters for the cleanest possible URL
            full_url = full_url.split('?')[0].rstrip('/')

            if full_url not in seen_urls:
                post_urls.append(full_url)
                seen_urls.add(full_url)
    return post_urls


def get_post_caption(page: Page) -> str:
    """Extract post's caption from Instagram post."""
    # The main heading is usually the post caption.
    caption_element = page.query_selector('h1')
    return caption_element.inner_text().strip() if caption_element else ''


def get_post_date(page: Page) -> Optional[datetime]:
    """Extract post's date from Instagram post page."""
    date_element = page.query_selector('time[datetime]')
    if date_element:
        datetime_attr = date_element.get_attribute('datetime')
        if datetime_attr:
            # The datetime attribute from Instagram is in UTC ('Z' suffix).
            # Parse it into a timezone-aware datetime object.
            utc_datetime = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
            # Convert to the local timezone specified in the configuration.
            return utc_datetime.astimezone(TIMEZONE)
    return None


def extract_post_data(post_url: str, cutoff_date: datetime, account: str, page: Page) -> Optional[Dict]:
    """Extracts the post data from the post URL."""
    page.goto(post_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
    time.sleep(BROWSER_LOAD_DELAY)

    post_date = get_post_date(page)
    if not post_date or post_date < cutoff_date:
        return None

    return {
        'url': post_url,
        'account': account,
        'caption': get_post_caption(page),
        'date_posted': post_date,  # Keep datetime object for sorting
    }


def generate_html_report(posts: List[Dict], cutoff_date: datetime, output_dir: str, template_path: str) -> str:
    """Generate a stylized HTML report of fetched posts using a template."""
    # Sort posts by date, newest first, regardless of the account
    posts.sort(key=lambda p: p['date_posted'], reverse=True)

    # Format date after sorting
    for post in posts:
        post['date_posted'] = post['date_posted'].strftime('%d-%m-%Y')

    generated_on = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    filename = f"instagram_updates_{datetime.now().strftime('%Y%m%d')}.html"
    output_file = os.path.join(output_dir, filename)

    date_range = f"{cutoff_date.strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')}"

    template_data = {
        'posts': posts,
        'date_range': date_range,
        'total_posts': len(posts),
        'generated_on': generated_on,
        'max_post_age': INSTAGRAM_MAX_POST_AGE,
        'total_accounts': len(INSTAGRAM_ACCOUNTS),
    }

    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    template = env.get_template(os.path.basename(template_path))
    html_content = template.render(**template_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")
    return output_file


def setup_browser(playwright) -> Browser:
    """Launch and connect to the browser instance."""
    logger.info(f"Starting the browser at page {INSTAGRAM_URL}...")
    subprocess.Popen([BROWSER_PATH, f"--remote-debugging-port={BROWSER_DEBUG_PORT}", INSTAGRAM_URL])
    logger.debug(f"Waiting {BROWSER_LOAD_DELAY} seconds for the browser to load...")
    time.sleep(BROWSER_LOAD_DELAY)
    logger.debug(f"Connecting to the browser at port {BROWSER_DEBUG_PORT}...")
    return playwright.chromium.connect_over_cdp(f"http://localhost:{BROWSER_DEBUG_PORT}")


def process_account(account: str, page: Page, cutoff_date: datetime) -> List[Dict]:
    """Process a single Instagram account and return its recent posts."""
    logger.info(f"@{account}: Processing posts...")
    account_url = f"{INSTAGRAM_URL}{account}/"
    page.goto(account_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
    time.sleep(BROWSER_LOAD_DELAY)

    logger.debug(f"@{account}: Fetching posts URLs...")
    post_urls = get_account_post_urls(page)
    if not post_urls:
        logger.warning(f"@{account}: No post URLs found.")
        return []

    logger.debug(f"@{account}: Found {len(post_urls)} post URLs. Fetching post details...")
    account_posts = []
    for i, post_url in enumerate(post_urls):
        if i >= INSTAGRAM_MAX_POSTS_PER_ACCOUNT:
            logger.debug(f"@{account}: Reached max posts per account ({INSTAGRAM_MAX_POSTS_PER_ACCOUNT}).")
            break
        logger.debug(f"@{account}: Fetching post {i + 1}/{len(post_urls)}: {post_url}")
        post_data = extract_post_data(post_url, cutoff_date, account, page)
        if post_data:
            account_posts.append(post_data)
        else:
            # If we find one older than the cutoff, we can safely assume the rest are also old.
            logger.info(f"@{account}: Found post older than cutoff date, stopping for this account.")
            break

    logger.info(f"@{account}: Found {len(account_posts)} recent post(s).")
    return account_posts


def main():
    """Main function to run the Instagram scraper."""
    try:
        with sync_playwright() as p:
            browser = setup_browser(p)
            page = browser.contexts[0].pages[0]

            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=INSTAGRAM_MAX_POST_AGE)
            logger.info(f"Fetching posts not older than {cutoff_date.strftime('%d-%m-%Y')}.")

            all_posts = []
            for account in INSTAGRAM_ACCOUNTS:
                all_posts.extend(process_account(account, page, cutoff_date))

            if all_posts:
                logger.info("Generating the HTML report...")
                output_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
                template_path = 'template.html'
                report_path = generate_html_report(all_posts, cutoff_date, output_dir, template_path)
                logger.info("Opening the HTML report...")
                os.startfile(report_path)
            else:
                logger.info("No new posts found to generate a report.")

        logger.info("Done :)")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":  # pragma: no cover
    main()
