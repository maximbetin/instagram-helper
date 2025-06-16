import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import instaloader
import pytz

from config import DAYS_TO_LOOK_BACK, INSTAGRAM_ACCOUNTS, LAST_RUN_FILE, POSTS_HISTORY_FILE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
RETRY_DELAY = 10
POSTS_PER_ACCOUNT = 5
ACCOUNT_DELAY = 10


class InstagramFetcher:
  def __init__(self):
    self.loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        max_connection_attempts=MAX_RETRIES
    )
    self.posts_history = self._load_posts_history()
    self.last_run = self._load_last_run()
    self.madrid_tz = pytz.timezone('Europe/Madrid')
    self._login()

  def _login(self):
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    if not username or not password:
      logger.warning("INSTAGRAM_USERNAME and/or INSTAGRAM_PASSWORD not set in environment or .env file.")
      return
    try:
      self.loader.login(username, password)
      logger.info(f"Logged in as {username}")
    except Exception as e:
      logger.error(f"Could not log in as {username}: {e}")

  def _load_posts_history(self) -> Dict[str, List[Dict]]:
    """Load the history of previously seen posts."""
    if POSTS_HISTORY_FILE.exists():
      try:
        with open(POSTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
          return json.load(f)
      except Exception as e:
        logger.error(f"Error reading posts history file: {e}")
        return {}
    return {}

  def _save_posts_history(self):
    """Save the current posts history to file."""
    try:
      with open(POSTS_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(self.posts_history, f, indent=2, ensure_ascii=False)
    except Exception as e:
      logger.error(f"Error saving posts history file: {e}")

  def _load_last_run(self) -> Optional[datetime]:
    """Load the timestamp of the last successful run."""
    if LAST_RUN_FILE.exists():
      try:
        with open(LAST_RUN_FILE, 'r', encoding='utf-8') as f:
          timestamp = float(f.read().strip())
          return datetime.fromtimestamp(timestamp, tz=timezone.utc)
      except Exception as e:
        logger.error(f"Error reading last run file: {e}")
    return None

  def _save_last_run(self):
    """Save the current run timestamp."""
    try:
      with open(LAST_RUN_FILE, 'w', encoding='utf-8') as f:
        f.write(str(datetime.now(timezone.utc).timestamp()))
    except Exception as e:
      logger.error(f"Error saving last run file: {e}")

  def get_recent_posts(self) -> Dict[str, List[Dict]]:
    """Fetch recent posts from configured Instagram accounts."""
    new_posts = {}
    cutoff_date = datetime.now(self.madrid_tz) - timedelta(days=DAYS_TO_LOOK_BACK)

    for account in INSTAGRAM_ACCOUNTS:
      for attempt in range(1, MAX_RETRIES + 1):
        try:
          profile = instaloader.Profile.from_username(self.loader.context, account)
          account_posts = []
          for idx, post in enumerate(profile.get_posts()):
            if idx >= POSTS_PER_ACCOUNT:
              break
            # Convert post date to Madrid timezone
            post_date_madrid = post.date_utc.astimezone(self.madrid_tz)
            if post_date_madrid < cutoff_date:
              break
            post_data = {
                'url': f"https://www.instagram.com/p/{post.shortcode}/",
                'date': post_date_madrid.isoformat(),
                'shortcode': post.shortcode,
                'caption': post.caption if post.caption else "No caption"
            }
            if account not in self.posts_history or \
                    post_data['shortcode'] not in [p['shortcode'] for p in self.posts_history[account]]:
              account_posts.append(post_data)
              if account not in self.posts_history:
                self.posts_history[account] = []
              self.posts_history[account].append(post_data)
          if account_posts:
            new_posts[account] = account_posts
          break  # Success, break out of retry loop
        except Exception as e:
          logger.error(f"Error fetching posts for {account} (attempt {attempt}): {e}")
          if attempt < MAX_RETRIES:
            logger.info(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
          else:
            logger.error(f"Failed to fetch posts for {account} after {MAX_RETRIES} attempts.")
        time.sleep(ACCOUNT_DELAY)

    self._save_posts_history()
    self._save_last_run()

    return new_posts
