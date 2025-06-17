"""Instagram browser launcher with post fetching."""

import re
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from playwright.sync_api import Page, sync_playwright

from config import (BROWSER_ARGS, BROWSER_VIEWPORT, DAYS_BACK_TO_FETCH, DELAY_BETWEEN_ACCOUNTS, INSTAGRAM_ACCOUNTS, INSTAGRAM_URL, LOCALE, MAX_POSTS_TO_CHECK,
                    TIMEZONE, USER_AGENT)
from utils import logger

# Page navigation timeouts
TIMEOUTS = {
    'page_load': 3000,
    'post_navigation': 8000,
    'account_navigation': 12000,
    'main_page': 30000,
}

# Login verification
LOGIN_RETRY_ATTEMPTS = 3

# Element selectors
SELECTORS = {
    'login_indicators': [
        'nav[role="navigation"]',
        'a[href="/"]',
        'a[href="/explore/"]',
        'a[href="/reels/"]',
        'a[href="/direct/inbox/"]'
    ],
    'login_page_indicators': [
        'input[name="username"]',
        'input[name="password"]',
        'button[type="submit"]',
        'form[method="post"]'
    ],
    'caption': [
        'h1[dir="auto"]',
        'div[data-testid="post-caption"] span',
        'article h1',
        'span[dir="auto"]',
        'div[data-testid="post-caption"]',
        'article div[dir="auto"]',
        'article span',
        'h1',
        'p'
    ],
    'date': [
        'time[datetime]',
        'a time',
        'time',
        'span[title*="202"]',
        'a[title*="202"]',
        'time[title*="202"]'
    ],
    'image': [
        'article img[crossorigin="anonymous"]',
        'img[src*="scontent"]',
        'img[src*="instagram"]',
        'article img',
        'img[alt*="Photo"]',
        'img[alt*="Image"]',
        'img[src*="cdninstagram"]',
        'img[src*="fbcdn"]',
        'img[src*="akamai"]',
        'img[src*="cdn"]',
        'img[src*="media"]',
        'img'
    ],
    'post': [
        'a[href*="/p/"]',
        'article a[href*="/p/"]',
        'a[href*="/p/"]:not([href*="/p/explore/"])',
        'a[href*="/reel/"]',
        'a[href*="/tv/"]'
    ]
}

# Image validation
IMG_KEYWORDS = ['scontent', 'instagram', 'cdn', 'fbcdn', 'akamai', 'media']
MIN_IMG_SIZE = 100

# Error messages
EXECUTION_CONTEXT_ERROR = "Execution context was destroyed"


def get_cutoff_date() -> datetime:
  """Get the cutoff date for filtering posts (7 days ago)."""
  madrid_tz = timezone(timedelta(hours=1))  # CET/CEST
  return datetime.now(madrid_tz) - timedelta(days=DAYS_BACK_TO_FETCH)


def parse_post_date(date_str: str) -> Optional[datetime]:
  """Parse a post date string into a datetime object."""
  if not date_str:
    return None

  try:
    # Try parsing ISO format first (from datetime attribute)
    if 'T' in date_str and ('Z' in date_str or '+' in date_str):
      dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
      madrid_tz = timezone(timedelta(hours=1))
      return dt.astimezone(madrid_tz)

    # Try parsing other common formats
    formats = [
        '%Y-%m-%d %H:%M:%S %Z',
        '%Y-%m-%d %H:%M:%S',
        '%B %d, %Y',
        '%d %B %Y',
    ]

    for fmt in formats:
      try:
        return datetime.strptime(date_str, fmt)
      except ValueError:
        continue

  except Exception as e:
    logger.debug(f"Could not parse date '{date_str}': {e}")

  return None


def is_post_recent(date_str: str, cutoff_date: datetime) -> bool:
  """Check if a post date is within the recent timeframe."""
  post_date = parse_post_date(date_str)
  if not post_date:
    # If we can't parse the date, assume it might be recent and check it
    return True

  return post_date >= cutoff_date


def extract_post_date_quick(page: Page, post_url: str) -> Optional[str]:
  """Quick extraction of post date without full page processing."""
  try:
    logger.debug(f"Quick date check: {post_url}")

    # Navigate to post quickly
    page.goto(post_url, wait_until="domcontentloaded", timeout=TIMEOUTS['post_navigation'])
    time.sleep(1)  # Brief wait for content

    # Try to extract date quickly
    for selector in SELECTORS['date']:
      try:
        date_element = page.query_selector(selector)
        if not date_element:
          continue

        # Try datetime attribute first
        datetime_attr = date_element.get_attribute('datetime')
        if datetime_attr:
          return datetime_attr

        # Try title attribute
        title_attr = date_element.get_attribute('title')
        if title_attr:
          return title_attr

        # Try inner text
        inner_text = date_element.inner_text().strip()
        if inner_text and re.search(r'\d{4}', inner_text):
          return inner_text

      except Exception:
        continue

    return None

  except Exception as e:
    logger.debug(f"Quick date extraction failed: {e}")
    return None


def check_if_logged_in(page: Page) -> bool:
  """Check if user is properly logged into Instagram."""
  try:
    time.sleep(2)  # Wait for page to stabilize

    # Check for logged-in indicators
    for selector in SELECTORS['login_indicators']:
      try:
        if page.query_selector(selector):
          return True
      except Exception:
        continue

    # Check if we're on the login page
    for selector in SELECTORS['login_page_indicators']:
      try:
        if page.query_selector(selector):
          return False
      except Exception:
        continue

    return True  # Assume logged in if we can't determine

  except Exception as e:
    logger.warning(f"Error checking login status: {e}")
    if EXECUTION_CONTEXT_ERROR in str(e):
      logger.info("Page is navigating, waiting for it to stabilize...")
      time.sleep(3)
      try:
        page.wait_for_selector('body', timeout=5000)
        return True
      except:
        return False
    return False


def wait_for_page_load(page: Page, timeout: Optional[int] = None) -> None:
  """Wait for page to load with better error handling."""
  timeout = timeout or TIMEOUTS['page_load']
  try:
    page.wait_for_load_state("domcontentloaded", timeout=timeout)
    time.sleep(1)  # Small additional wait for dynamic content
  except Exception as e:
    logger.warning(f"Page load timeout, continuing anyway: {e}")
    time.sleep(1)


def extract_caption(page: Page) -> str:
  """Extract caption from Instagram post."""
  for selector in SELECTORS['caption']:
    try:
      caption_element = page.query_selector(selector)
      if caption_element:
        caption_text = caption_element.inner_text().strip()
        if caption_text and len(caption_text) > 5:
          return caption_text
    except Exception as e:
      if EXECUTION_CONTEXT_ERROR in str(e):
        logger.warning("Execution context destroyed while extracting caption")
        break
      continue
  return ''


def extract_date_posted(page: Page) -> str:
  """Extract date posted from Instagram post."""
  for selector in SELECTORS['date']:
    try:
      date_element = page.query_selector(selector)
      if not date_element:
        continue

      # Try to get datetime attribute first
      datetime_attr = date_element.get_attribute('datetime')
      if datetime_attr:
        try:
          dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
          madrid_tz = timezone(timedelta(hours=1))  # CET/CEST
          dt_madrid = dt.astimezone(madrid_tz)
          return dt_madrid.strftime('%Y-%m-%d %H:%M:%S %Z')
        except:
          pass

      # Fallback to title attribute or inner text
      title_attr = date_element.get_attribute('title')
      if title_attr:
        return title_attr

      inner_text = date_element.inner_text().strip()
      if inner_text and re.search(r'\d{4}', inner_text):
        return inner_text

    except Exception as e:
      if EXECUTION_CONTEXT_ERROR in str(e):
        logger.warning("Execution context destroyed while extracting date")
        break
      continue
  return ''


def is_valid_image(img_src: str, width: Optional[str], height: Optional[str]) -> bool:
  """Check if image is valid based on URL and dimensions."""
  if not img_src:
    return False

  # Check for basic image format
  if not (img_src.startswith('http') or img_src.startswith('data:')):
    return False

  # Accept images that contain Instagram-related keywords OR look like valid image URLs
  has_instagram_keywords = any(keyword in img_src.lower() for keyword in IMG_KEYWORDS)
  looks_like_image = any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp'])

  if not (has_instagram_keywords or looks_like_image):
    return False

  # More lenient dimension check - accept if no dimensions or reasonable size
  if width and height:
    try:
      w, h = int(width), int(height)
      # Accept images that are at least 50x50 (was 100x100)
      return w >= 50 and h >= 50
    except:
      # If we can't parse dimensions, accept the image anyway
      return True

  return True


def extract_image_url(page: Page) -> Optional[str]:
  """Extract image URL from Instagram post."""
  # Wait a bit more for images to load
  time.sleep(2)

  # Try more specific selectors first, then broader ones
  image_selectors = [
      # Most specific - main post images
      'article img[crossorigin="anonymous"]',
      '[role="img"] img',
      'div[role="img"] img',
      # CDN-specific selectors
      'img[src*="scontent"]',
      'img[src*="cdninstagram"]',
      'img[src*="fbcdn"]',
      # General post images
      'article img',
      'img[alt*="Photo"]',
      'img[alt*="Image"]',
      # Fallback selectors
      'img[src*="instagram"]',
      'img[src*="cdn"]',
      'img[src*="akamai"]',
      'img[src*="media"]',
      # Last resort
      'img'
  ]

  found_images = []

  for selector in image_selectors:
    try:
      img_elements = page.query_selector_all(selector)
      logger.debug(f"Selector '{selector}': found {len(img_elements)} images")

      for img_element in img_elements:
        try:
          img_src = img_element.get_attribute('src')
          width = img_element.get_attribute('width')
          height = img_element.get_attribute('height')

          if img_src:
            found_images.append({
              'src': img_src,
              'width': width,
              'height': height,
              'selector': selector,
              'valid': is_valid_image(img_src, width, height)
            })

        except Exception as e:
          logger.debug(f"Error extracting from image element: {e}")
          continue

    except Exception as e:
      if EXECUTION_CONTEXT_ERROR in str(e):
        logger.warning("Execution context destroyed while extracting image")
        break
      logger.debug(f"Error with selector '{selector}': {e}")
      continue

  # Log what we found for debugging
  if found_images:
    logger.debug(f"Found {len(found_images)} total images:")
    for i, img in enumerate(found_images[:5]):  # Show first 5
      logger.debug(f"  {i + 1}. {img['src'][:80]}{'...' if len(img['src']) > 80 else ''} (valid: {img['valid']}, selector: {img['selector'][:30]})")
  else:
    logger.debug("No images found with any selector")

  # Return the first valid image
  for img in found_images:
    if img['valid']:
      logger.debug(f"Using image: {img['src'][:80]}{'...' if len(img['src']) > 80 else ''}")
      return img['src']

  # If no valid images, return the first one anyway (let the browser handle it)
  if found_images:
    logger.debug(f"No valid images found, using first available: {found_images[0]['src'][:80]}{'...' if len(found_images[0]['src']) > 80 else ''}")
    return found_images[0]['src']

  return None


def create_base_post_data(account: str, post_url: str) -> Dict:
  """Create base post data structure."""
  return {
      'account': account,
      'url': post_url,
      'caption': '',
      'date_posted': '',
      'image_url': None,
      'timestamp': datetime.now().isoformat()
  }


def create_error_post_data(account: str, post_url: str, error: str) -> Dict:
  """Create post data structure for errors."""
  post_data = create_base_post_data(account, post_url)
  post_data['error'] = error
  return post_data


def extract_post_details(page: Page, post_url: str, account: str) -> Dict:
  """Extract detailed information from a single Instagram post."""
  try:
    logger.debug(f"Opening post: {post_url}")

    # Navigate to post
    try:
      page.goto(post_url, wait_until="domcontentloaded", timeout=TIMEOUTS['post_navigation'])
      wait_for_page_load(page)
    except Exception as e:
      logger.warning(f"Navigation to post failed: {e}")
      return create_error_post_data(account, post_url, f"Navigation failed: {str(e)}")

    post_data = create_base_post_data(account, post_url)

    # Extract all post details
    post_data['caption'] = extract_caption(page)
    post_data['date_posted'] = extract_date_posted(page)
    post_data['image_url'] = extract_image_url(page)

    logger.debug(f"Extracted: caption={len(post_data['caption'])}chars, date={post_data['date_posted'][:10] if post_data['date_posted'] else 'None'}")
    return post_data

  except Exception as e:
    logger.error(f"Error extracting details from {post_url}: {e}")
    return create_error_post_data(account, post_url, str(e))


def extract_post_urls(page: Page, account: str) -> List[str]:
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
    except:
      continue

  return []


def fetch_posts_from_account(page: Page, account: str) -> List[Dict]:
  """Fetch recent posts from a specific Instagram account (past 7 days only)."""
  try:
    url = f"https://www.instagram.com/{account}/"
    logger.info(f"Fetching recent posts from @{account}")

    cutoff_date = get_cutoff_date()
    logger.debug(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

    # Navigate to account
    try:
      page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUTS['account_navigation'])
      wait_for_page_load(page)
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

    for i, post_url in enumerate(post_urls):
      if posts_checked >= MAX_POSTS_TO_CHECK:
        logger.debug(f"Reached maximum post check limit for @{account}")
        break

      try:
        posts_checked += 1
        logger.debug(f"Checking post {posts_checked}/{min(len(post_urls), MAX_POSTS_TO_CHECK)}")

        # Quick date check first
        post_date_str = extract_post_date_quick(page, post_url)

        if post_date_str and not is_post_recent(post_date_str, cutoff_date):
          posts_too_old += 1
          logger.debug(f"Post too old ({post_date_str}), stopping check")
          # Since posts are usually ordered by date (newest first),
          # if one post is outside our range, all subsequent posts will be too
          break

        # Post seems recent or date unclear, process it fully
        # NOTE: We're already on the post page from extract_post_date_quick,
        # so we don't need to navigate again
        logger.debug(f"Post appears recent, extracting details...")

        # Extract details from current page (already navigated by extract_post_date_quick)
        post_data = create_base_post_data(account, post_url)
        post_data['caption'] = extract_caption(page)
        post_data['date_posted'] = post_date_str or extract_date_posted(page)
        post_data['image_url'] = extract_image_url(page)

        # Log image extraction result
        if post_data['image_url']:
          logger.debug(f"✓ Image extracted successfully")
        else:
          logger.debug(f"✗ No image found for post")

        # Double-check the date after full processing
        if post_data.get('date_posted'):
          if not is_post_recent(post_data['date_posted'], cutoff_date):
            logger.debug(f"Post confirmed too old after full processing, stopping check")
            posts_too_old += 1
            # Since posts are usually ordered by date, stop checking remaining posts
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
  total_posts = sum(len(posts) for posts in posts_by_account.values())
  cutoff_date = get_cutoff_date()

  # Calculate image statistics
  posts_with_images = 0
  posts_without_images = 0
  for posts in posts_by_account.values():
    for post in posts:
      if post.get('image_url'):
        posts_with_images += 1
      else:
        posts_without_images += 1

  logger.info("=== SUMMARY ===")
  logger.info(f"Date range: {cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')} ({DAYS_BACK_TO_FETCH} days)")
  logger.info(f"Accounts: {len(posts_by_account)}/{len(INSTAGRAM_ACCOUNTS)} with posts | Total posts: {total_posts}")
  logger.info(f"Images: {posts_with_images} with images, {posts_without_images} without images")

  if posts_by_account:
    logger.info("Posts by account:")
    for account, posts in posts_by_account.items():
      account_with_images = sum(1 for post in posts if post.get('image_url'))
      logger.info(f"  @{account}: {len(posts)} posts ({account_with_images} with images)")

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
        .post-image { width: 100%; height: 180px; background: #f8f9fa; display: flex; align-items: center; justify-content: center; color: #666; }
        .post-image img { width: 100%; height: 100%; object-fit: cover; }
        .post-content { padding: 15px; }
        .post-date { color: #667eea; font-size: 0.8rem; font-weight: 500; margin-bottom: 8px; }
        .post-caption { color: #333; line-height: 1.4; margin-bottom: 12px; white-space: pre-wrap; word-wrap: break-word; }
        .post-link { display: inline-block; background: #667eea; color: white; text-decoration: none; padding: 6px 12px; border-radius: 15px; font-size: 0.8rem; }
        .post-link:hover { background: #5a6fd8; }
        .no-posts { text-align: center; padding: 30px; color: #666; font-style: italic; }
        .footer { text-align: center; padding: 20px; color: #666; border-top: 1px solid #e1e5e9; }
        @media (max-width: 768px) { .posts-grid { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } }
    """


def generate_html_header(timestamp: str) -> str:
  """Generate HTML header section."""
  cutoff_date = get_cutoff_date()
  date_range = f"{cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}"

  return f"""<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>Instagram Posts Report - Recent Posts ({DAYS_BACK_TO_FETCH} days)</title>
    <style>{generate_html_styles()}</style>
</head>
<body>
    <div class='container'>
        <div class='header'>
            <h1>📸 Instagram Posts Report</h1>
            <p>Recent posts from the past {DAYS_BACK_TO_FETCH} days</p>
            <p>Date range: {date_range}</p>
            <p>Generated on {timestamp}</p>
        </div>"""


def generate_html_stats(posts_by_account: Dict[str, List[Dict]]) -> str:
  """Generate HTML stats section."""
  total_posts = sum(len(posts) for posts in posts_by_account.values())

  return f"""        <div class='stats'>
            <div class='stat-item'>
                <div class='stat-number'>{len(INSTAGRAM_ACCOUNTS)}</div>
                <div class='stat-label'>Accounts Checked</div>
            </div>
            <div class='stat-item'>
                <div class='stat-number'>{len(posts_by_account)}</div>
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


def generate_post_card_html(post: Dict) -> str:
  """Generate HTML for a single post card."""
  caption = format_post_caption(post.get('caption', ''))
  date_posted = post.get('date_posted', 'Unknown date')
  image_url = post.get('image_url')

  if image_url:
    image_html = f'<img src="{image_url}" alt="Post image" onerror="this.parentElement.innerHTML=\'<span>No image available</span>\'" />'
  else:
    image_html = '<span>No image available</span>'

  return f"""                <div class='post-card'>
                    <div class='post-image'>
                        {image_html}
                    </div>
                    <div class='post-content'>
                        <div class='post-date'>📅 {date_posted}</div>
                        <div class='post-caption'>{caption}</div>
                        <a href='{post['url']}' target='_blank' class='post-link'>View on Instagram →</a>
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


def generate_html_footer() -> str:
  """Generate HTML footer section."""
  return """        <div class='footer'>
            <p>Generated by Instagram Posts Fetcher</p>
        </div>
    </div>
</body>
</html>"""


def generate_html_report(posts_by_account: Dict[str, List[Dict]], output_file: str = "instagram_posts.html") -> str:
  """Generate a beautiful HTML report of fetched posts."""
  timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  html_parts = [
      generate_html_header(timestamp),
      generate_html_stats(posts_by_account)
  ]

  # Generate content for each account
  for account, posts in posts_by_account.items():
    html_parts.append(generate_account_section_html(account, posts))

  html_parts.append(generate_html_footer())

  # Write to file
  html_content = '\n'.join(html_parts)
  with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

  logger.info(f"HTML report generated: {output_file}")
  return output_file


def verify_login_with_retries(page: Page) -> bool:
  """Verify login status with retries."""
  for attempt in range(LOGIN_RETRY_ATTEMPTS):
    try:
      logger.info(f"Verifying login status (attempt {attempt + 1}/{LOGIN_RETRY_ATTEMPTS})...")
      if check_if_logged_in(page):
        return True
      else:
        logger.warning("Login not detected, please make sure you're logged in")
        if attempt < LOGIN_RETRY_ATTEMPTS - 1:
          retry = input("Press Enter to retry login verification, or 'q' to quit: ")
          if retry.lower() == 'q':
            return False
    except Exception as e:
      logger.warning(f"Login verification attempt {attempt + 1} failed: {e}")
      if attempt < LOGIN_RETRY_ATTEMPTS - 1:
        time.sleep(2)
      continue

  logger.error(f"Could not verify login status after {LOGIN_RETRY_ATTEMPTS} attempts.")
  logger.info("Please make sure you are properly logged into Instagram!")
  return False


def setup_browser_context(playwright_instance):
  """Set up browser and context with proper configuration."""
  browser = playwright_instance.chromium.launch(headless=False, args=BROWSER_ARGS)

  context = browser.new_context(
      viewport=BROWSER_VIEWPORT,
      user_agent=USER_AGENT,
      locale=LOCALE,
      timezone_id=TIMEZONE
  )

  return browser, context


def navigate_to_instagram(page: Page) -> bool:
  """Navigate to Instagram main page."""
  try:
    logger.info("Navigating to Instagram...")
    page.goto(INSTAGRAM_URL, wait_until="domcontentloaded", timeout=TIMEOUTS['main_page'])
    return True
  except Exception as e:
    logger.error(f"Failed to navigate to Instagram: {e}")
    return False


def fetch_all_posts(page: Page) -> Dict[str, List[Dict]]:
  """Fetch posts from all configured accounts."""
  posts_by_account = {}

  for account in INSTAGRAM_ACCOUNTS:
    posts = fetch_posts_from_account(page, account)
    if posts:
      posts_by_account[account] = posts

    # Delay between accounts (except last one)
    if account != INSTAGRAM_ACCOUNTS[-1]:
      time.sleep(DELAY_BETWEEN_ACCOUNTS)

  return posts_by_account


def main():
  """Open Instagram for login, then fetch posts from specified accounts."""
  try:
    logger.info("Opening Instagram main page...")

    with sync_playwright() as p:
      browser, context = setup_browser_context(p)
      page = context.new_page()

      # Navigate to Instagram
      if not navigate_to_instagram(page):
        return

      logger.info("Instagram page opened! Please log in manually.")
      logger.info("After logging in, press Enter to start fetching posts...")
      input()

      # Verify login
      if not verify_login_with_retries(page):
        logger.info("Press Enter to close the browser...")
        input()
        context.close()
        browser.close()
        return

      logger.info("Login verified! Starting to fetch posts from specified accounts...")

      # Fetch posts from all accounts
      posts_by_account = fetch_all_posts(page)

      # Display results and generate report
      display_posts_summary(posts_by_account)
      html_file = generate_html_report(posts_by_account)
      logger.info(f"HTML report saved to: {html_file}")

      logger.info("Post fetching complete! Press Enter to close the browser...")
      input()

      context.close()
      browser.close()

  except Exception as e:
    logger.error(f"An error occurred: {e}")
    raise


if __name__ == "__main__":
  main()
