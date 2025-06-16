import time
from datetime import datetime, timedelta
from typing import Dict, List

import pytz
from instaloader import Instaloader, Profile  # type: ignore

from config import ACCOUNT_DELAY, DAYS_TO_LOOK_BACK, INSTAGRAM_ACCOUNTS, MAX_RETRIES, POSTS_PER_ACCOUNT, RETRY_DELAY
from utils import logger


class InstagramFetcher:
  def __init__(self):
    self.loader = Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False,
        max_connection_attempts=MAX_RETRIES
    )
    self.madrid_tz = pytz.timezone('Europe/Madrid')
    logger.info("Initialized Instagram fetcher (no login required for public accounts)")

  def get_recent_posts(self) -> Dict[str, List[Dict[str, str]]]:
    posts: Dict[str, List[Dict[str, str]]] = {}
    cutoff_date = datetime.now(self.madrid_tz) - timedelta(days=DAYS_TO_LOOK_BACK)

    for account in INSTAGRAM_ACCOUNTS:
      account_posts = self._fetch_account_posts(account, cutoff_date)
      if account_posts:
        posts[account] = account_posts

    return posts

  def _fetch_account_posts(self, account: str, cutoff_date: datetime) -> List[Dict[str, str]]:
    """Fetch posts for a single account with retry logic."""
    for attempt in range(1, MAX_RETRIES + 1):
      try:
        profile = Profile.from_username(self.loader.context, account)
        account_posts: List[Dict[str, str]] = []

        for idx, post in enumerate(profile.get_posts()):
          if idx >= POSTS_PER_ACCOUNT:
            break

          post_date_madrid = post.date_utc.astimezone(self.madrid_tz)
          if post_date_madrid < cutoff_date:
            break

          post_data = {
              'url': f"https://www.instagram.com/p/{post.shortcode}/",
              'date': post_date_madrid.isoformat(),
              'shortcode': post.shortcode,
              'caption': post.caption or "No caption"
          }
          account_posts.append(post_data)

        return account_posts

      except Exception as e:
        logger.error(f"Error fetching posts for {account} (attempt {attempt}): {e}")
        if attempt < MAX_RETRIES:
          logger.info(f"Retrying in {RETRY_DELAY} seconds...")
          time.sleep(RETRY_DELAY)
        else:
          logger.error(f"Failed to fetch posts for {account} after {MAX_RETRIES} attempts.")

      time.sleep(ACCOUNT_DELAY)

    return []
