"""Instagram browser launcher with post fetching."""

import re
import time
from datetime import datetime, timedelta
from typing import Dict, List

from playwright.sync_api import sync_playwright

from config import (BROWSER_ARGS, BROWSER_VIEWPORT, DAYS_TO_LOOK_BACK, DELAY_BETWEEN_ACCOUNTS, INSTAGRAM_ACCOUNTS, INSTAGRAM_URL, LOCALE, POSTS_PER_ACCOUNT,
                    TIMEZONE, USER_AGENT)
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

    # Extract caption using stable selectors with timeout
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
          if caption_text and len(caption_text) > 5:  # Reduced minimum length
            post_data['caption'] = caption_text
            break
      except Exception as e:
        if "Execution context was destroyed" in str(e):
          logger.warning(f"Execution context destroyed while extracting caption")
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
              from datetime import timezone
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
          logger.warning(f"Execution context destroyed while extracting date")
          break
        continue

    # Extract image URL using stable selectors
    img_selectors = [
        'article img[crossorigin="anonymous"]',
        'img[src*="scontent"]',
        'img[src*="instagram"]',
        'article img',
        'img[alt*="Photo"]',
        'img[alt*="Image"]',
        'img'
    ]

    for selector in img_selectors:
      try:
        img_element = page.query_selector(selector)
        if img_element:
          img_src = img_element.get_attribute('src')
          if img_src and ('scontent' in img_src or 'instagram' in img_src):
            post_data['image_url'] = img_src
            break
      except Exception as e:
        if "Execution context was destroyed" in str(e):
          logger.warning(f"Execution context destroyed while extracting image")
          break
        continue

    logger.info(f"Extracted data: Caption length={len(post_data['caption'])}, Date={post_data['date_posted']}")
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

    posts = []

    # Use only stable selectors for post links - no dynamic classes
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

  logger.info(f"=== POST FETCHING SUMMARY ===")
  logger.info(f"Total accounts checked: {len(INSTAGRAM_ACCOUNTS)}")
  logger.info(f"Accounts with posts: {len(posts_by_account)}")
  logger.info(f"Total posts found: {total_posts}")
  logger.info("")

  for account, posts in posts_by_account.items():
    logger.info(f"@{account}: {len(posts)} posts")

  logger.info("=" * 30)


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

      logger.info("Post fetching complete! Press Enter to close the browser...")
      input()

      context.close()
      browser.close()

  except Exception as e:
    logger.error(f"An error occurred: {e}")
    raise


if __name__ == "__main__":
  main()
