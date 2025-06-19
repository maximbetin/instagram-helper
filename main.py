"""Instagram browser launcher with post fetching."""

import os
import pdb
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
    """Extract post's caption from Instagram post."""
    caption_element = page.query_selector('h1[dir="auto"]')
    if caption_element:
        caption_text = caption_element.inner_text().strip()
        if caption_text and len(caption_text) > 5:
            return caption_text
    return ''


def get_post_date(page: Page) -> Optional[datetime]:
    """Extract post's date from Instagram post page."""
    date_element = page.query_selector('time[datetime]')
    if date_element:
        datetime_attr = date_element.get_attribute('datetime')
        if datetime_attr:
            return datetime.fromisoformat(datetime_attr.replace('Z', '+02:00'))
    return None


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


def get_post_data(post_url: str, cutoff_date: datetime, account: str, page: Page) -> Optional[Dict]:
    """Goes over the post URLs and returns a list of the recent ones."""
    post = {
        'account': account,
        'url': post_url,
        'caption': '',
        'date_posted': '',
    }

    post_date_dt = get_post_date(page)
    if post_date_dt:
        # If the date is older than the cutoff date, stop processing more posts
        if post_date_dt < cutoff_date:
            return None

        # Extract details from current page
        post['caption'] = get_post_caption(page)
        post['date_posted'] = post_date_dt.strftime('%d-%m-%Y')

    return post


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

            all_posts = []
            for account in INSTAGRAM_ACCOUNTS:
                account_posts = []
                logger.info(f"@{account}: Processing posts...")
                account_url = f"{INSTAGRAM_URL}{account}/"

                logger.debug(f"Navigating to {account_url}...")
                page.goto(account_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
                time.sleep(BROWSER_LOAD_DELAY)

                logger.debug(f"@{account}: Fetching posts URLs...")
                post_urls = get_post_urls(page)

                logger.debug(f"@{account}: Fetching recent posts...")
                posts_checked = 0
                for post_url in post_urls:
                    if posts_checked >= INSTAGRAM_MAX_POSTS_PER_ACCOUNT:
                        break

                    logger.debug(f"@{account}: Fetching post {post_url}...")
                    page.goto(post_url, wait_until="domcontentloaded", timeout=BROWSER_LOAD_TIMEOUT)
                    time.sleep(BROWSER_LOAD_DELAY)
                    post = get_post_data(post_url, cutoff_date, account, page)
                    if post:
                        account_posts.append(post)
                    posts_checked += 1

                logger.info(f"@{account}: {len(account_posts)} recent post(s) found")
                all_posts.extend(account_posts)

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
