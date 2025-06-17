"""Instagram data fetcher module."""

import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import instaloader
import pytz

from config import DAYS_TO_LOOK_BACK, INSTAGRAM_ACCOUNTS, MAX_RETRIES, POSTS_PER_ACCOUNT, TIMEZONE
from utils import logger

# Suppress instaloader's verbose logging
logging.getLogger('instaloader').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)


class InstagramFetcher:
  def __init__(self):
    self.loader = instaloader.Instaloader(  # type: ignore
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        max_connection_attempts=1,
        request_timeout=10.0,
        quiet=True
    )
    self.madrid_tz = pytz.timezone(TIMEZONE)
    self.is_logged_in = False
    self._login()

  def _login(self):
    """Attempt to log in to Instagram using credentials from environment variables."""
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    if not username or not password:
      logger.info("No login credentials provided - will attempt to access public profiles only")
      return

    # Try to load existing session first
    session_file = f"{username}_session"
    if os.path.exists(session_file):
      try:
        logger.info(f"Loading session for {username}...")
        self.loader.load_session_from_file(username, session_file)
        self.is_logged_in = True
        logger.info("Session loaded successfully")
        return
      except Exception as e:
        logger.warning(f"Session load failed: {str(e)[:50]}...")
        if os.path.exists(session_file):
          os.remove(session_file)

    # Store original logging level before attempting login
    original_level = logging.getLogger().level

    try:
      logger.info(f"Logging in as {username}...")
      # Temporarily suppress all logging during login to avoid spam
      logging.getLogger().setLevel(logging.CRITICAL)

      self.loader.login(username, password)
      self.is_logged_in = True

      # Restore logging level
      logging.getLogger().setLevel(original_level)
      logger.info("Login successful")

      # Save session for future use
      try:
        self.loader.save_session_to_file(session_file)
      except Exception:
        pass  # Session saving is not critical

    except Exception as e:
      # Restore logging level in case of error
      logging.getLogger().setLevel(original_level)

      error_msg = str(e)
      if "window._sharedData" in error_msg:
        logger.warning("Instagram anti-bot protection detected")
      elif "BadCredentials" in error_msg:
        logger.error("Invalid username or password")
      elif "TwoFactorAuth" in error_msg:
        logger.error("Two-factor authentication required")
      else:
        logger.warning(f"Login failed: {error_msg[:50]}...")

      logger.info("Continuing without login - will try public profiles only")

  def _fetch_profile_quietly(self, account: str):
    """Fetch profile with suppressed logging to avoid spam."""
    # Temporarily suppress instaloader logging
    instaloader_logger = logging.getLogger('instaloader')
    old_level = instaloader_logger.level
    instaloader_logger.setLevel(logging.CRITICAL)

    try:
      profile = instaloader.Profile.from_username(self.loader.context, account)  # type: ignore
      return profile
    finally:
      # Always restore logging level
      instaloader_logger.setLevel(old_level)

  def get_recent_posts(self) -> Dict[str, List[Dict]]:
    """Fetch recent posts from configured Instagram accounts."""
    posts = {}
    cutoff_date = datetime.now(self.madrid_tz) - timedelta(days=DAYS_TO_LOOK_BACK)

    if self.is_logged_in:
      logger.info(f"Fetching posts from {len(INSTAGRAM_ACCOUNTS)} accounts (logged in)")
    else:
      logger.info(f"Fetching posts from {len(INSTAGRAM_ACCOUNTS)} accounts (public access only)")

    successful_accounts = 0
    skipped_accounts = []

    for i, account in enumerate(INSTAGRAM_ACCOUNTS, 1):
      logger.info(f"[{i}/{len(INSTAGRAM_ACCOUNTS)}] Checking @{account}")

      success = False
      for attempt in range(1, MAX_RETRIES + 1):
        try:
          profile = self._fetch_profile_quietly(account)
          account_posts = []

          post_count = 0
          for post in profile.get_posts():
            if post_count >= POSTS_PER_ACCOUNT:
              break

            post_date_madrid = post.date_utc.astimezone(self.madrid_tz)
            if post_date_madrid < cutoff_date:
              break

            post_data = {
                'url': f"https://www.instagram.com/p/{post.shortcode}/",
                'date': post_date_madrid.isoformat(),
                'shortcode': post.shortcode,
                'caption': post.caption if post.caption else "No caption"
            }
            account_posts.append(post_data)
            post_count += 1

          if account_posts:
            posts[account] = account_posts
            logger.info(f"  ✓ Found {len(account_posts)} recent posts")
            successful_accounts += 1
          else:
            logger.info("  - No recent posts found")
            successful_accounts += 1

          success = True
          break

        except instaloader.exceptions.ProfileNotExistsException:
          logger.warning("  ✗ Profile does not exist")
          skipped_accounts.append(f"{account} (not found)")
          break
        except instaloader.exceptions.LoginRequiredException:
          logger.info("  ✗ Private profile, login required")
          skipped_accounts.append(f"{account} (private)")
          break
        except Exception as e:
          error_msg = str(e)
          if "401" in error_msg or "403" in error_msg or "HTTP error code 401" in error_msg:
            if attempt < MAX_RETRIES:
              logger.info(f"  ⚠ Access denied, retrying... ({attempt}/{MAX_RETRIES})")
              time.sleep(3)
            else:
              logger.warning(f"  ✗ Access denied after {MAX_RETRIES} attempts")
              skipped_accounts.append(f"{account} (access denied)")
          else:
            if attempt < MAX_RETRIES:
              logger.info(f"  ⚠ Error occurred, retrying... ({attempt}/{MAX_RETRIES})")
              time.sleep(3)
            else:
              logger.warning(f"  ✗ Failed after {MAX_RETRIES} attempts: {error_msg[:30]}...")
              skipped_accounts.append(f"{account} (error)")

      # Add delay between accounts to avoid rate limiting
      if not success and i < len(INSTAGRAM_ACCOUNTS):
        time.sleep(2)
      elif success and i < len(INSTAGRAM_ACCOUNTS):
        time.sleep(1)

    # Summary
    logger.info(f"Completed: {successful_accounts} successful, {len(skipped_accounts)} skipped")
    if skipped_accounts:
      logger.info(f"Skipped accounts: {', '.join(skipped_accounts)}")

    return posts
