"""Instagram browser launcher with post fetching."""

import os
import re
import time
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from playwright.sync_api import Page, sync_playwright

from config import *
from utils import logger


def get_cutoff_date() -> datetime:
    """Get the cutoff date for filtering posts."""
    return datetime.now(MADRID_TZ) - timedelta(days=DAYS_BACK_TO_FETCH)


def parse_post_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse a post date string into a datetime object."""
    if not date_str:
        return None

    if 'UTC' in date_str and '+' in date_str:
        cleaned_date = date_str.replace(' UTC', '')
        dt = datetime.fromisoformat(cleaned_date)
        return dt.astimezone(MADRID_TZ)

    # Try parsing ISO format (from datetime attribute)
    if 'T' in date_str and ('Z' in date_str or '+' in date_str):
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.astimezone(MADRID_TZ)

    # Try parsing other common formats
    formats = [
        '%Y-%m-%d %H:%M:%S %Z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S UTC%z',
        '%B %d, %Y',
        '%d %B %Y',
    ]

    for fmt in formats:
        parsed = datetime.strptime(date_str, fmt)
        if parsed.tzinfo:
            parsed = parsed.replace(tzinfo=MADRID_TZ)
        return parsed.astimezone(MADRID_TZ)

    return None


def is_post_recent(date_str: Optional[str], cutoff_date: datetime) -> bool:
    """Check if a post date is within the recent timeframe."""
    # If we can't parse the date, assume it might be recent and check it
    if not date_str:
        return True

    post_date = parse_post_date(date_str)
    if not post_date:
        return True
    return post_date >= cutoff_date


def wait_for_page_load(page: Page) -> None:
    """Wait for page to load."""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT_PAGE_LOAD)
    except Exception as e:
        logger.warning(f"Page load timeout: {e}")


def extract_caption(page: Page) -> str:
    """Extract caption from Instagram post."""
    for selector in SELECTORS['caption']:
        try:
            caption_element = page.query_selector(selector)
            if caption_element:
                caption_text = caption_element.inner_text().strip()
                return caption_text if caption_text and len(caption_text) > 5 else ''
        except Exception as e:
            if EXECUTION_CONTEXT_ERROR in str(e):
                logger.warning("Execution context destroyed while extracting caption")
                break
            continue
    return ''


def extract_post_date(page: Page, post_url: Optional[str] = None) -> Optional[str]:
    """Extract post date from Instagram post page."""
    try:
        if post_url:
            logger.debug(f"Date extraction for: {post_url}")
            page.goto(post_url, wait_until="domcontentloaded", timeout=TIMEOUT_POST_NAVIGATION)
            time.sleep(1)

        # Try to extract date from current page
        for selector in SELECTORS['date']:
            try:
                date_element = page.query_selector(selector)
                if not date_element:
                    continue

                # Try datetime attribute first
                datetime_attr = date_element.get_attribute('datetime')
                if datetime_attr:
                    try:
                        dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        dt_madrid = dt.astimezone(MADRID_TZ)
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
                if EXECUTION_CONTEXT_ERROR in str(e):
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


def extract_post_urls(page: Page) -> List[str]:
    """Extract post URLs from account page."""
    for selector in SELECTORS['post']:
        try:
            links = page.query_selector_all(selector)
            if links:
                logger.debug(f"Found {len(links)} posts using selector: {selector}")

                post_urls = []
                for link in links[:MAX_POSTS_TO_CHECK]:
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
        logger.info(f"Fetching posts from @{account}...")

        cutoff_date = get_cutoff_date()
        page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_ACCOUNT_NAVIGATION)
        wait_for_page_load(page)

        post_urls = extract_post_urls(page)
        if post_urls:
            logger.info(f"Checking {len(post_urls)} posts...")

            recent_posts = []
            posts_checked = 0
            posts_too_old = 0

            for post_url in post_urls:
                if posts_checked >= MAX_POSTS_TO_CHECK:
                    logger.debug(f"Reached maximum post check limit for @{account}")
                    break

                posts_checked += 1
                logger.debug(f"Checking post {posts_checked}/{min(len(post_urls), MAX_POSTS_TO_CHECK)}")
                post_date_str = extract_post_date(page, post_url)

                if post_date_str and is_post_recent(post_date_str, cutoff_date):
                    post_data = create_base_post_data(account, post_url)
                    post_data['caption'] = extract_caption(page)
                    post_data['date_posted'] = post_date_str

                    recent_posts.append(post_data)
                    logger.debug(f"Added recent post (total: {len(recent_posts)})")

                    time.sleep(1)

                else:
                    posts_too_old += 1
                    break

            logger.info(f"@{account}: {len(recent_posts)} recent posts found ({posts_checked} checked, {posts_too_old} too old)")
            return recent_posts

        else:
            logger.warning(f"No post links found for @{account}")
            return []

    except Exception as e:
        logger.error(f"Error fetching posts from @{account}: {e}")
        return []


def display_posts_summary(posts_by_account: Dict[str, List[Dict]]) -> None:
    """Display a summary of fetched posts."""
    # Calculate stats excluding the special sorting key
    real_accounts = {k: v for k, v in posts_by_account.items() if k != '_all_sorted'}
    total_posts = sum(len(posts) for posts in real_accounts.values())
    cutoff_date = get_cutoff_date()
    current_time = datetime.now(MADRID_TZ)

    logger.info("=== SUMMARY ===")
    logger.info(f"Date range: {cutoff_date.strftime('%Y-%m-%d')} to {current_time.strftime('%Y-%m-%d')} ({DAYS_BACK_TO_FETCH} days)")
    logger.info(f"Accounts: {len(real_accounts)}/{len(INSTAGRAM_ACCOUNTS)} with posts | Total posts: {total_posts}")
    logger.info("Image fetching disabled - focusing on text content and dates")

    if real_accounts:
        logger.info("Posts by account:")
        for account, posts in real_accounts.items():
            logger.info(f"  @{account}: {len(posts)} posts")

    logger.info("=" * 15)


def generate_html_styles() -> str:
    """Generate CSS styles for HTML report."""
    return """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #667eea; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h1 { margin: 0; font-size: 2.5rem; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 25px; }
        .stat-item { text-align: center; background: #f8f9fa; padding: 20px; border-radius: 8px; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; font-size: 0.9rem; text-transform: uppercase; }
        .account-section { margin: 20px; border: 1px solid #e1e5e9; border-radius: 8px; overflow: hidden; }
        .account-header { background: #667eea; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }
        .account-name { font-size: 1.3rem; font-weight: bold; }
        .post-count { background: rgba(255,255,255,0.2); padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; }
        .posts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; padding: 20px; }
        .post-card { border: 1px solid #e1e5e9; border-radius: 8px; overflow: hidden; transition: transform 0.2s; }
        .post-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .post-content { padding: 15px; }
        .post-account { color: #667eea; font-size: 0.9rem; font-weight: 600; margin-bottom: 6px; }
        .post-date { color: #667eea; font-size: 0.8rem; font-weight: 500; margin-bottom: 8px; }
        .post-caption { color: #333; line-height: 1.4; margin-bottom: 12px; white-space: pre-wrap; word-wrap: break-word; }
        .post-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        .post-link { display: inline-block; background: #667eea; color: white; text-decoration: none; padding: 6px 12px; border-radius: 15px; font-size: 0.8rem; }
        .post-link:hover { background: #5a6fd8; }
        .copy-link-btn { background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 15px; font-size: 0.8rem; cursor: pointer; transition: background 0.2s; }
        .copy-link-btn:hover { background: #218838; }
        .copy-link-btn:active { background: #1e7e34; }
        .no-posts { text-align: center; padding: 30px; color: #666; font-style: italic; }
        .footer { text-align: center; padding: 20px; color: #666; border-top: 1px solid #e1e5e9; }
        @media (max-width: 768px) { .posts-grid { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } }
    """


def generate_html_header(timestamp: str) -> str:
    """Generate HTML header section."""
    cutoff_date = get_cutoff_date()
    date_range = f"{cutoff_date.strftime('%d-%m-%Y')} to {datetime.now().strftime('%d-%m-%Y')}"

    return f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Instagram Posts Report - Recent Posts ({DAYS_BACK_TO_FETCH} days)</title>
    <style>{generate_html_styles()}</style>
    <script>
        function copyToClipboard(text) {{
            // Try modern clipboard API first
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(text).then(function() {{
                    // Show success feedback
                    const event = window.event;
                    const button = event.target;
                    const originalText = button.textContent;
                    button.textContent = '✅ Copied!';
                    button.style.background = '#007bff';
                    setTimeout(function() {{
                        button.textContent = originalText;
                        button.style.background = '#28a745';
                    }}, 2000);
                }}).catch(function(err) {{
                    console.error('Clipboard API failed: ', err);
                    // Fallback to document.execCommand
                    fallbackCopyToClipboard(text, event.target);
                }});
            }} else {{
                // Fallback for older browsers
                fallbackCopyToClipboard(text, event.target);
            }}
        }}

        function fallbackCopyToClipboard(text, button) {{
            try {{
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                const successful = document.execCommand('copy');
                document.body.removeChild(textArea);

                if (successful) {{
                    // Show success feedback
                    const originalText = button.textContent;
                    button.textContent = '✅ Copied!';
                    button.style.background = '#007bff';
                    setTimeout(function() {{
                        button.textContent = originalText;
                        button.style.background = '#28a745';
                    }}, 2000);
                }} else {{
                    alert('Failed to copy link to clipboard');
                }}
            }} catch (err) {{
                console.error('Fallback copy failed: ', err);
                alert('Failed to copy link to clipboard');
            }}
        }}
    </script>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>📸 Instagram Posts Report</h1>
            <p>Recent posts from the past {DAYS_BACK_TO_FETCH} days (sorted by date)</p>
            <p>Date range: {date_range}</p>
            <p>Generated on {timestamp}</p>
        </div>"""


def generate_html_stats(posts_by_account: Dict[str, List[Dict]]) -> str:
    """Generate HTML stats section."""
    # Calculate stats excluding the special sorting key
    real_accounts = {k: v for k, v in posts_by_account.items() if k != '_all_sorted'}
    total_posts = sum(len(posts) for posts in real_accounts.values())

    return f"""        <div class='stats'>
            <div class='stat-item'>
                <div class='stat-number'>{len(INSTAGRAM_ACCOUNTS)}</div>
                <div class='stat-label'>Accounts Checked</div>
            </div>
            <div class='stat-item'>
                <div class='stat-number'>{len(real_accounts)}</div>
                <div class='stat-label'>Accounts with Posts</div>
            </div>
            <div class='stat-item'>
                <div class='stat-number'>{total_posts}</div>
                <div class='stat-label'>Total Posts Found</div>
            </div>
        </div>"""


def format_post_caption(caption: str) -> str:
    """Format post caption for HTML display."""
    return caption.replace('"', '&quot;').replace("'", '&#39;')


def clean_instagram_url(url: str) -> str:
    """Clean Instagram URL by removing tracking parameters."""
    if not url:
        return url

    # Remove common tracking parameters
    parsed = urllib.parse.urlparse(url)

    # Keep only the base path, remove query parameters and fragments
    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Remove trailing slash if present
    clean_url = clean_url.rstrip('/')

    return clean_url


def generate_post_card_html(post: Dict) -> str:
    """Generate HTML for a single post card."""
    caption = format_post_caption(post.get('caption', ''))
    date_posted = post.get('date_posted', 'Unknown date')
    account = post.get('account', 'Unknown account')
    original_url = post.get('url', '')
    clean_url = clean_instagram_url(original_url)

    # Since image fetching is disabled, we focus on text content
    return f"""                <div class='post-card'>
                    <div class='post-content'>
                        <div class='post-account'>👤 @{account}</div>
                        <div class='post-date'>📅 {date_posted}</div>
                        <div class='post-caption'>{caption}</div>
                        <div class='post-actions'>
                            <a href='{original_url}' target='_blank' class='post-link'>View on Instagram →</a>
                            <button class='copy-link-btn' onclick='copyToClipboard("{clean_url}")' title='Copy clean link for sharing'>
                                📋 Copy Link
                            </button>
                        </div>
                    </div>
                </div>"""


def generate_account_section_html(account: str, posts: List[Dict]) -> str:
    """Generate HTML for an account section."""
    section_html = f"""        <div class='account-section'>
            <div class='account-header'>
                <div class='account-name'>@{account}</div>
                <div class='post-count'>{len(posts)} posts</div>
            </div>
            <div class='posts-grid'>"""

    if posts:
        for post in posts:
            section_html += "\n" + generate_post_card_html(post)
    else:
        section_html += """                <div class='no-posts'>
                    <p>No posts found for this account</p>
                </div>"""

    section_html += """            </div>
        </div>"""

    return section_html


def generate_global_posts_section_html(posts: List[Dict]) -> str:
    """Generate HTML for all posts sorted globally by date."""
    section_html = f"""        <div class='account-section'>
            <div class='account-header'>
                <div class='account-name'>🌍 All Posts (Sorted by Date)</div>
                <div class='post-count'>{len(posts)} posts</div>
            </div>
            <div class='posts-grid'>"""

    if posts:
        for post in posts:
            section_html += "\n" + generate_post_card_html(post)
    else:
        section_html += """                <div class='no-posts'>
                    <p>No posts found</p>
                </div>"""

    section_html += """            </div>
        </div>"""

    return section_html


def generate_html_footer() -> str:
    """Generate HTML footer section."""
    return """        <div class='footer'>
            <p>Generated by Instagram Posts Fetcher</p>
        </div>
    </div>
</body>
</html>"""


def get_desktop_path() -> str:
    """Get the path to the user's desktop directory across different operating systems."""
    return os.path.join(os.path.expanduser('~'), 'Desktop')


def generate_html_report(posts_by_account: Dict[str, List[Dict]]) -> str:
    """Generate a stylized HTML report of fetched posts."""
    timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')

    filename = f"instagram_updates_{timestamp}.html"
    output_file = os.path.join(get_desktop_path(), filename)

    html_parts = [
        generate_html_header(timestamp),
        generate_html_stats(posts_by_account)
    ]

    # Use globally sorted posts if available, otherwise fall back to individual accounts
    if '_all_sorted' in posts_by_account and posts_by_account['_all_sorted']:
        # Show all posts sorted globally by date
        all_posts = posts_by_account['_all_sorted']
        html_parts.append(generate_global_posts_section_html(all_posts))
    else:
        # Fallback to individual account sections
        for account, posts in posts_by_account.items():
            if account != '_all_sorted':  # Skip the special sorting key
                html_parts.append(generate_account_section_html(account, posts))

    html_parts.append(generate_html_footer())

    # Write to file
    html_content = '\n'.join(html_parts)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")
    return output_file


def setup_browser_context(playwright_instance):
    """Set up browser and context with proper configuration."""
    browser = playwright_instance.chromium.launch(headless=False, args=BROWSER_ARGS)

    context = browser.new_context(
        locale=LOCALE,
        timezone_id=TIMEZONE,
        user_agent=USER_AGENT,
        viewport=BROWSER_VIEWPORT
    )

    return browser, context


def sort_posts_by_date(posts: List[Dict]) -> List[Dict]:
    """Sort posts by published date, newest first."""
    def get_sort_key(post):
        date_str = post.get('date_posted', '')
        if not date_str:
            return datetime.min.replace(tzinfo=MADRID_TZ)

        parsed_date = parse_post_date(date_str)
        return parsed_date if parsed_date else datetime.min.replace(tzinfo=MADRID_TZ)

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
            time.sleep(DELAY_BETWEEN_ACCOUNTS)

    # Sort all posts globally by date (newest first)
    all_posts_sorted = sort_posts_by_date(all_posts)

    # Store the globally sorted posts under a special key
    posts_by_account['_all_sorted'] = all_posts_sorted

    return posts_by_account


def open_html_file(file_path: str) -> None:
    """Open HTML file in default browser."""
    abs_path = os.path.abspath(file_path)
    logger.info(f"Opening HTML report in browser: {abs_path}...")
    os.startfile(abs_path)


def main():
    """Open Instagram for login, then fetch posts from specified accounts."""
    try:
        with sync_playwright() as p:
            browser, context = setup_browser_context(p)
            page = context.new_page()

            logger.info(f"Navigating to {INSTAGRAM_URL}...")
            page.goto(INSTAGRAM_URL, wait_until="domcontentloaded", timeout=TIMEOUT_MAIN_PAGE)

            logger.info("Please log in to Instagram and press Enter to continue...")
            input()

            # Fetch posts from all accounts
            posts_by_account = fetch_all_posts(page)

            # Display results and generate report
            display_posts_summary(posts_by_account)
            html_file = generate_html_report(posts_by_account)
            logger.info(f"HTML report saved to: {html_file}")

            # Close browser automatically
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
