"""Instagram browser launcher with post fetching."""

import re
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from playwright.sync_api import sync_playwright

from config import BROWSER_ARGS, BROWSER_VIEWPORT, DELAY_BETWEEN_ACCOUNTS, INSTAGRAM_ACCOUNTS, INSTAGRAM_URL, LOCALE, POSTS_PER_ACCOUNT, TIMEZONE, USER_AGENT
from utils import logger


def check_if_logged_in(page) -> bool:
  """Check if user is properly logged into Instagram."""
  try:
    # Wait a moment for page to stabilize
    time.sleep(2)

    # Look for elements that indicate we're logged in
    logged_in_indicators = [
        'nav[role="navigation"]',
        'a[href="/"]',
        'a[href="/explore/"]',
        'a[href="/reels/"]',
        'a[href="/direct/inbox/"]'
    ]

    for selector in logged_in_indicators:
      try:
        if page.query_selector(selector):
          return True
      except Exception:
        continue

    # Also check if we're on the login page
    login_indicators = [
        'input[name="username"]',
        'input[name="password"]',
        'button[type="submit"]',
        'form[method="post"]'
    ]

    for selector in login_indicators:
      try:
        if page.query_selector(selector):
          return False
      except Exception:
        continue

    return True  # Assume logged in if we can't determine

  except Exception as e:
    logger.warning(f"Error checking login status: {e}")
    # If we get an execution context error, wait and try again
    if "Execution context was destroyed" in str(e):
      logger.info("Page is navigating, waiting for it to stabilize...")
      time.sleep(3)
      try:
        # Try a simple check
        page.wait_for_selector('body', timeout=5000)
        return True  # Assume logged in if page loads
      except:
        return False
    return False


def wait_for_page_load(page, timeout: int = 3000):
  """Wait for page to load with better error handling."""
  try:
    # Wait for DOM to be ready instead of network idle
    page.wait_for_load_state("domcontentloaded", timeout=timeout)
    # Small additional wait for dynamic content
    time.sleep(1)
  except Exception as e:
    logger.warning(f"Page load timeout, continuing anyway: {e}")
    # Wait a bit more for content to load
    time.sleep(1)


def extract_post_details(page, post_url: str, account: str) -> Dict:
  """Extract detailed information from a single Instagram post."""
  try:
    logger.info(f"Opening post: {post_url}")

    # Navigate to post with better error handling and shorter timeout
    try:
      page.goto(post_url, wait_until="domcontentloaded", timeout=8000)
      # Wait for DOM to be ready
      wait_for_page_load(page, 3000)
    except Exception as e:
      logger.warning(f"Navigation to post failed: {e}")
      return {
          'account': account,
          'url': post_url,
          'caption': '',
          'date_posted': '',
          'image_url': None,
          'timestamp': datetime.now().isoformat(),
          'error': f"Navigation failed: {str(e)}"
      }

    post_data = {
        'account': account,
        'url': post_url,
        'caption': '',
        'date_posted': '',
        'image_url': None,
        'timestamp': datetime.now().isoformat()
    }

    # Extract caption using stable selectors
    caption_selectors = [
        'h1[dir="auto"]',
        'div[data-testid="post-caption"] span',
        'article h1',
        'span[dir="auto"]',
        'div[data-testid="post-caption"]',
        'article div[dir="auto"]',
        'article span',
        'h1',
        'p'
    ]

    for selector in caption_selectors:
      try:
        caption_element = page.query_selector(selector)
        if caption_element:
          caption_text = caption_element.inner_text().strip()
          if caption_text and len(caption_text) > 5:
            post_data['caption'] = caption_text
            break
      except Exception as e:
        if "Execution context was destroyed" in str(e):
          logger.warning("Execution context destroyed while extracting caption")
          break
        continue

    # Extract date posted using stable selectors
    date_selectors = [
        'time[datetime]',
        'a time',
        'time',
        'span[title*="202"]',
        'a[title*="202"]',
        'time[title*="202"]'
    ]

    for selector in date_selectors:
      try:
        date_element = page.query_selector(selector)
        if date_element:
          # Try to get datetime attribute first
          datetime_attr = date_element.get_attribute('datetime')
          if datetime_attr:
            try:
              # Parse ISO datetime and convert to Europe/Madrid time
              dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
              # Convert to Europe/Madrid timezone
              madrid_tz = timezone(timedelta(hours=1))  # CET/CEST
              dt_madrid = dt.astimezone(madrid_tz)
              post_data['date_posted'] = dt_madrid.strftime('%Y-%m-%d %H:%M:%S %Z')
              break
            except:
              pass

          # Fallback to title attribute or inner text
          title_attr = date_element.get_attribute('title')
          if title_attr:
            post_data['date_posted'] = title_attr
            break

          inner_text = date_element.inner_text().strip()
          if inner_text and re.search(r'\d{4}', inner_text):  # Contains year
            post_data['date_posted'] = inner_text
            break
      except Exception as e:
        if "Execution context was destroyed" in str(e):
          logger.warning("Execution context destroyed while extracting date")
          break
        continue

    # Extract image URL using more comprehensive selectors
    img_selectors = [
        'article img[crossorigin="anonymous"]',
        'img[src*="scontent"]',
        'img[src*="instagram"]',
        'article img',
        'img[alt*="Photo"]',
        'img[alt*="Image"]',
        'img[src*="cdninstagram"]',
        'img[src*="fbcdn"]',
        'img[src*="akamai"]',
        'img[src*="instagram"]',
        'img[src*="cdn"]',
        'img[src*="media"]',
        'img'
    ]

    for selector in img_selectors:
      try:
        img_elements = page.query_selector_all(selector)
        for img_element in img_elements:
          img_src = img_element.get_attribute('src')
          if img_src and any(keyword in img_src.lower() for keyword in ['scontent', 'instagram', 'cdn', 'fbcdn', 'akamai', 'media']):
            # Skip very small images (likely icons)
            width = img_element.get_attribute('width')
            height = img_element.get_attribute('height')
            if width and height:
              try:
                if int(width) > 100 and int(height) > 100:
                  post_data['image_url'] = img_src
                  break
              except:
                post_data['image_url'] = img_src
                break
            else:
              post_data['image_url'] = img_src
              break
        if post_data['image_url']:
          break
      except Exception as e:
        if "Execution context was destroyed" in str(e):
          logger.warning("Execution context destroyed while extracting image")
          break
        continue

    logger.info(
        f"Extracted data: Caption length={len(post_data['caption'])}, Date={post_data['date_posted']}, Image={'Yes' if post_data['image_url'] else 'No'}")
    return post_data

  except Exception as e:
    logger.error(f"Error extracting details from {post_url}: {e}")
    return {
        'account': account,
        'url': post_url,
        'caption': '',
        'date_posted': '',
        'image_url': None,
        'timestamp': datetime.now().isoformat(),
        'error': str(e)
    }


def fetch_posts_from_account(page, account: str) -> List[Dict]:
  """Fetch recent posts from a specific Instagram account."""
  try:
    url = f"https://www.instagram.com/{account}/"
    logger.info(f"Fetching posts from @{account}...")

    # Navigate to account with better error handling
    try:
      page.goto(url, wait_until="domcontentloaded", timeout=12000)
      wait_for_page_load(page, 3000)
    except Exception as e:
      logger.error(f"Failed to navigate to @{account}: {e}")
      return []

    # Check if we're still on the account page
    current_url = page.url
    if account not in current_url:
      logger.warning(f"Redirected away from @{account} to {current_url}")
      return []

    # Check if logged in
    if not check_if_logged_in(page):
      logger.error("Not properly logged in to Instagram")
      return []

    # Use only stable selectors for post links
    post_selectors = [
        'a[href*="/p/"]',
        'article a[href*="/p/"]',
        'a[href*="/p/"]:not([href*="/p/explore/"])',  # Exclude explore links
        'a[href*="/reel/"]',  # Also include reels
        'a[href*="/tv/"]'     # And IGTV
    ]

    post_links = []
    for selector in post_selectors:
      try:
        links = page.query_selector_all(selector)
        if links:
          post_links = links
          logger.info(f"Found {len(links)} posts using selector: {selector}")
          break
      except:
        continue

    if not post_links:
      logger.warning(f"No post links found for @{account}")
      return []

    # Extract URLs first to avoid execution context issues
    post_urls = []
    for i, link in enumerate(post_links[:POSTS_PER_ACCOUNT]):
      try:
        post_url = link.get_attribute('href')
        if post_url and ('/p/' in post_url or '/reel/' in post_url or '/tv/' in post_url):
          full_url = f"https://www.instagram.com{post_url}" if post_url.startswith('/') else post_url
          post_urls.append(full_url)
      except Exception as e:
        logger.warning(f"Error extracting URL from post {i + 1}: {e}")
        continue

    logger.info(f"Extracted {len(post_urls)} post URLs to process")

    # Now process each URL individually
    posts = []
    for i, post_url in enumerate(post_urls):
      try:
        logger.info(f"Processing post {i + 1}/{len(post_urls)}: {post_url}")

        # Extract detailed post information
        post_data = extract_post_details(page, post_url, account)
        posts.append(post_data)

        # Small delay between posts
        time.sleep(1)

      except Exception as e:
        logger.warning(f"Error processing post {i + 1} from @{account}: {e}")
        continue

    logger.info(f"Successfully processed {len(posts)} posts from @{account}")
    return posts

  except Exception as e:
    logger.error(f"Error fetching posts from @{account}: {e}")
    return []


def display_posts_summary(posts_by_account: Dict[str, List[Dict]]):
  """Display a summary of fetched posts."""
  total_posts = sum(len(posts) for posts in posts_by_account.values())

  logger.info("=== POST FETCHING SUMMARY ===")
  logger.info(f"Total accounts checked: {len(INSTAGRAM_ACCOUNTS)}")
  logger.info(f"Accounts with posts: {len(posts_by_account)}")
  logger.info(f"Total posts found: {total_posts}")
  logger.info("")

  for account, posts in posts_by_account.items():
    logger.info(f"@{account}: {len(posts)} posts")

  logger.info("=" * 30)


def generate_html_report(posts_by_account: Dict[str, List[Dict]], output_file: str = "instagram_posts.html"):
  """Generate a beautiful HTML report of fetched posts."""

  # Start building HTML content
  lines = []

  # Add HTML header
  lines.append("<!DOCTYPE html>")
  lines.append("<html lang='en'>")
  lines.append("<head>")
  lines.append("    <meta charset='UTF-8'>")
  lines.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
  lines.append("    <title>Instagram Posts Report</title>")
  lines.append("    <style>")
  lines.append("        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }")
  lines.append("        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }")
  lines.append("        .header { background: #667eea; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }")
  lines.append("        .header h1 { margin: 0; font-size: 2.5rem; }")
  lines.append("        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 25px; }")
  lines.append("        .stat-item { text-align: center; background: #f8f9fa; padding: 20px; border-radius: 8px; }")
  lines.append("        .stat-number { font-size: 2rem; font-weight: bold; color: #667eea; }")
  lines.append("        .stat-label { color: #666; font-size: 0.9rem; text-transform: uppercase; }")
  lines.append("        .account-section { margin: 20px; border: 1px solid #e1e5e9; border-radius: 8px; overflow: hidden; }")
  lines.append(
    "        .account-header { background: #667eea; color: white; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; }")
  lines.append("        .account-name { font-size: 1.3rem; font-weight: bold; }")
  lines.append("        .post-count { background: rgba(255,255,255,0.2); padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; }")
  lines.append("        .posts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; padding: 20px; }")
  lines.append("        .post-card { border: 1px solid #e1e5e9; border-radius: 8px; overflow: hidden; transition: transform 0.2s; }")
  lines.append("        .post-card:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }")
  lines.append(
    "        .post-image { width: 100%; height: 180px; background: #f8f9fa; display: flex; align-items: center; justify-content: center; color: #666; }")
  lines.append("        .post-image img { width: 100%; height: 100%; object-fit: cover; }")
  lines.append("        .post-content { padding: 15px; }")
  lines.append("        .post-date { color: #667eea; font-size: 0.8rem; font-weight: 500; margin-bottom: 8px; }")
  lines.append("        .post-caption { color: #333; line-height: 1.4; margin-bottom: 12px; white-space: pre-wrap; word-wrap: break-word; }")
  lines.append(
    "        .post-link { display: inline-block; background: #667eea; color: white; text-decoration: none; padding: 6px 12px; border-radius: 15px; font-size: 0.8rem; }")
  lines.append("        .post-link:hover { background: #5a6fd8; }")
  lines.append("        .no-posts { text-align: center; padding: 30px; color: #666; font-style: italic; }")
  lines.append("        .footer { text-align: center; padding: 20px; color: #666; border-top: 1px solid #e1e5e9; }")
  lines.append("        @media (max-width: 768px) { .posts-grid { grid-template-columns: 1fr; } .header h1 { font-size: 2rem; } }")
  lines.append("    </style>")
  lines.append("</head>")
  lines.append("<body>")
  lines.append("    <div class='container'>")
  lines.append("        <div class='header'>")
  lines.append("            <h1>📸 Instagram Posts Report</h1>")
  lines.append(f"            <p>Fetched on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
  lines.append("        </div>")

  # Add stats
  lines.append("        <div class='stats'>")
  lines.append(
    f"            <div class='stat-item'><div class='stat-number'>{len(INSTAGRAM_ACCOUNTS)}</div><div class='stat-label'>Accounts Checked</div></div>")
  lines.append(
    f"            <div class='stat-item'><div class='stat-number'>{len(posts_by_account)}</div><div class='stat-label'>Accounts with Posts</div></div>")
  lines.append(
    f"            <div class='stat-item'><div class='stat-number'>{sum(len(posts) for posts in posts_by_account.values())}</div><div class='stat-label'>Total Posts Found</div></div>")
  lines.append("        </div>")

  # Generate content for each account
  for account, posts in posts_by_account.items():
    lines.append(f"        <div class='account-section'>")
    lines.append(f"            <div class='account-header'>")
    lines.append(f"                <div class='account-name'>@{account}</div>")
    lines.append(f"                <div class='post-count'>{len(posts)} posts</div>")
    lines.append("            </div>")
    lines.append("            <div class='posts-grid'>")

    if posts:
      for post in posts:
        # Clean caption
        caption = post.get('caption', '').replace('"', '&quot;').replace("'", '&#39;')

        # Format date
        date_posted = post.get('date_posted', 'Unknown date')

        # Handle image
        image_url = post.get('image_url')
        if image_url:
          image_html = f"<img src='{image_url}' alt='Post image' onerror='this.parentElement.innerHTML=\"<span>No image available</span>\"' />"
        else:
          image_html = "<span>No image available</span>"

        lines.append("                <div class='post-card'>")
        lines.append("                    <div class='post-image'>")
        lines.append(f"                        {image_html}")
        lines.append("                    </div>")
        lines.append("                    <div class='post-content'>")
        lines.append(f"                        <div class='post-date'>📅 {date_posted}</div>")
        lines.append(f"                        <div class='post-caption'>{caption}</div>")
        lines.append(f"                        <a href='{post['url']}' target='_blank' class='post-link'>View on Instagram →</a>")
        lines.append("                    </div>")
        lines.append("                </div>")
    else:
      lines.append("                <div class='no-posts'>")
      lines.append("                    <p>No posts found for this account</p>")
      lines.append("                </div>")

    lines.append("            </div>")
    lines.append("        </div>")

  # Add footer
  lines.append("        <div class='footer'>")
  lines.append("            <p>Generated by Instagram Posts Fetcher</p>")
  lines.append("        </div>")
  lines.append("    </div>")
  lines.append("</body>")
  lines.append("</html>")

  # Write to file
  html_content = '\n'.join(lines)
  with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

  logger.info(f"HTML report generated: {output_file}")
  return output_file


def main():
  """Open Instagram for login, then fetch posts from specified accounts."""
  try:
    logger.info("Opening Instagram main page...")

    with sync_playwright() as p:
      browser = p.chromium.launch(
          headless=False,  # Show browser
          args=BROWSER_ARGS
      )

      # Set up browser context
      context = browser.new_context(
          viewport=BROWSER_VIEWPORT,
          user_agent=USER_AGENT,
          locale=LOCALE,
          timezone_id=TIMEZONE
      )

      page = context.new_page()

      # Navigate to Instagram main page
      logger.info("Navigating to Instagram...")
      page.goto(INSTAGRAM_URL, wait_until="domcontentloaded", timeout=30000)

      logger.info("Instagram page opened! Please log in manually.")
      logger.info("After logging in, press Enter to start fetching posts...")

      # Wait for user to log in and press Enter
      input()

      # Verify login status with retries
      login_verified = False
      for attempt in range(3):
        try:
          logger.info(f"Verifying login status (attempt {attempt + 1}/3)...")
          if check_if_logged_in(page):
            login_verified = True
            break
          else:
            logger.warning("Login not detected, please make sure you're logged in")
            if attempt < 2:  # Don't ask on last attempt
              retry = input("Press Enter to retry login verification, or 'q' to quit: ")
              if retry.lower() == 'q':
                logger.info("Closing browser...")
                context.close()
                browser.close()
                return
        except Exception as e:
          logger.warning(f"Login verification attempt {attempt + 1} failed: {e}")
          if attempt < 2:
            time.sleep(2)
          continue

      if not login_verified:
        logger.error("Could not verify login status after 3 attempts.")
        logger.info("Please make sure you are properly logged into Instagram!")
        logger.info("Press Enter to close the browser...")
        input()
        context.close()
        browser.close()
        return

      logger.info("Login verified! Starting to fetch posts from specified accounts...")

      # Fetch posts from each account
      posts_by_account = {}

      for account in INSTAGRAM_ACCOUNTS:
        posts = fetch_posts_from_account(page, account)
        if posts:
          posts_by_account[account] = posts

        # Delay between accounts to avoid rate limiting
        if account != INSTAGRAM_ACCOUNTS[-1]:  # Don't delay after last account
          time.sleep(DELAY_BETWEEN_ACCOUNTS)

      # Display summary
      display_posts_summary(posts_by_account)

      # Generate HTML report
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
