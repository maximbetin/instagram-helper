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


def get_post_caption(page: Page) -> str:
    # TODO: Find the specific selector that works consistently
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


def get_post_date(page: Page, post_url: Optional[str] = None) -> str:
    # TODO: Seems a bit overkill, this likely can be simplified
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

        return ''

    except Exception as e:
        logger.debug(f"Date extraction failed: {e}")
        return ''


def create_base_post_data(account: str, post_url: str) -> Dict:
    # TODO: Perfect candidate for a class
    """Create base post data structure."""
    return {
        'account': account,
        'url': post_url,
        'caption': '',
        'date_posted': '',
    }


def get_post_urls(page: Page) -> List[str]:
    """Fetch recent posts from a specific Instagram account."""
    # TODO: Find specifically which is the one that works consistently
    for selector in HTML_SELECTORS['post']:
        links = page.query_selector_all(selector)
        if links:
            post_urls = []
            for link in links[:INSTAGRAM_MAX_POSTS_PER_ACCOUNT]:
                post_url = link.get_attribute('href')
                if post_url and any(path in post_url for path in ['/p/', '/reel/', '/tv/']):
                    full_url = (f"https://www.instagram.com{post_url}" if post_url.startswith('/') else post_url)
                    post_urls.append(full_url)
            return post_urls
    return []


def get_recent_posts(post_urls: List[str], cutoff_date: datetime, account: str, page: Page) -> List[Dict]:
    """Goes over the post URLs and returns a list of the recent ones."""
    recent_posts = []
    posts_checked = 0

    for post_url in post_urls:
        # Stop if we have reached the maximum number of posts to check
        if posts_checked >= INSTAGRAM_MAX_POSTS_PER_ACCOUNT:
            break

        posts_checked += 1

        # Obtain the date in string format
        post_date_str = get_post_date(page, post_url)

        # Convert the date to a datetime object
        post_date_dt = datetime.fromisoformat(post_date_str.replace('UTC', ''))

        # If the date is older than the cutoff date, stop processing more posts
        if post_date_dt < cutoff_date:
            break

        # Extract details from current page
        post_object = create_base_post_data(account, post_url)
        post_object['caption'] = get_post_caption(page)
        post_object['date_posted'] = post_date_dt.strftime('%d-%m-%Y')

        recent_posts.append(post_object)

    return recent_posts


def generate_html_report(posts: List[Dict], cutoff_date: datetime) -> str:
    """Generate a stylized HTML report of fetched posts using a template."""
    generated_on = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

    filename = f"ig_posts_report_{generated_on.replace(' ', '_').replace(':', '-')}.html"
    output_file = os.path.join(desktop_path, filename)

    date_range = f"{cutoff_date.strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')}"

    template_data = {
        'posts': posts,
        'date_range': date_range,
        'total_posts': len(posts),
        'generated_on': generated_on,
        'max_post_age': INSTAGRAM_MAX_POST_AGE,
        'total_accounts': len(INSTAGRAM_ACCOUNTS),
    }

    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    html_content = template.render(**template_data)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")
    return output_file


def main():
    try:
        with sync_playwright() as p:
            logger.info(f"Starting the browser at page {INSTAGRAM_URL}...")
            subprocess.Popen([BROWSER_PATH, f"--remote-debugging-port={BROWSER_DEBUG_PORT}", INSTAGRAM_URL])

            logger.debug(f"Waiting {BROWSER_LOAD_DELAY} seconds for the browser to load the page...")
            time.sleep(BROWSER_LOAD_DELAY)

            logger.debug(f"Connecting to the browser at port {BROWSER_DEBUG_PORT}...")
            browser = p.chromium.connect_over_cdp(f"http://localhost:{BROWSER_DEBUG_PORT}", timeout=10000)

            logger.debug("Getting the current page content...")
            page = browser.contexts[0].pages[0]

            logger.debug("Getting the cutoff date...")
            cutoff_date = datetime.now(TIMEZONE) - timedelta(days=INSTAGRAM_MAX_POST_AGE)

            logger.info("Iterating over each account...")
            posts = []

            for account in INSTAGRAM_ACCOUNTS:
                account_url = f"{INSTAGRAM_URL}{account}/"

                logger.debug(f"Navigating to {account_url}...")
                page.goto(account_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
                time.sleep(BROWSER_LOAD_DELAY)

                logger.info(f"@{account}: Fetching posts URLs...")
                post_urls = get_post_urls(page)

                logger.info(f"@{account}: Fetching recent posts...")
                account_posts = get_recent_posts(post_urls, cutoff_date, account, page)
                posts.extend(account_posts)
                logger.info(f"@{account}: {len(account_posts)} recent post(s) found")

        logger.info("Generating the HTML report...")
        report = generate_html_report(posts, cutoff_date)

        logger.info("Opening the HTML report...")
        os.startfile(report)

        logger.info("Done :)")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
