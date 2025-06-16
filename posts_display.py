import logging
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def format_post_date(date_str: str) -> str:
  """Format the post date in a human-readable format."""
  dt = datetime.fromisoformat(date_str)
  return dt.strftime("%Y-%m-%d %H:%M UTC")


def display_posts(posts: Dict[str, List[Dict]]) -> None:
  """Display posts in a clear, human-readable format, without shortcode."""
  if not posts:
    print("\nNo new posts found in the last 7 days.")
    return

  print("\n=== New Instagram Posts ===\n")

  for account, account_posts in posts.items():
    print(f"{account.upper()}")
    print("=" * (len(account) + 2))
    for post in account_posts:
      print(f"Date: {format_post_date(post['date'])}")
      print(f"URL:  {post['url']}")
      print("-" * 50)
    print()
