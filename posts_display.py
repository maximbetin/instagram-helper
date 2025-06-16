import logging
import re
from datetime import datetime
from typing import Dict, List, Optional

import pytz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

MADRID_TZ = pytz.timezone('Europe/Madrid')


def clean_caption(caption: Optional[str]) -> str:
  """Clean up the caption text for better readability."""
  if not caption:
    return "No caption"

  # Remove hashtags
  caption = re.sub(r'#\w+', '', caption)

  # Remove URLs
  caption = re.sub(r'https?://\S+', '', caption)

  # Remove email addresses
  caption = re.sub(r'\S+@\S+\.\S+', '', caption)

  # Remove phone numbers
  caption = re.sub(r'☎️?\s*\d[\d\s]+', '', caption)

  # Remove all emojis
  caption = re.sub(r'[\U0001F300-\U0001F9FF]', '', caption)

  # Remove multiple dots and normalize them
  caption = re.sub(r'\.{2,}', '.', caption)

  # Remove extra spaces
  caption = re.sub(r'\s+', ' ', caption)

  # Split into sentences and clean each one
  sentences = []
  for sentence in re.split(r'(?<=[.!?])\s+', caption):
    sentence = sentence.strip()
    if sentence:
      # Remove any remaining special characters
      sentence = re.sub(r'[^\w\s.,!?-]', '', sentence)
      # Remove multiple spaces again
      sentence = re.sub(r'\s+', ' ', sentence)
      # Remove standalone dots
      sentence = re.sub(r'\s*\.\s*', '.', sentence)
      # Remove trailing/leading whitespace
      sentence = sentence.strip()
      if sentence:
        sentences.append(sentence)

  # Join sentences with newlines
  return '\n'.join(sentences)


def format_post_date(date_str: str) -> str:
  """Format the post date in Madrid timezone."""
  dt = datetime.fromisoformat(date_str)
  return dt.strftime("%Y-%m-%d %H:%M Madrid")


def display_posts(posts: Dict[str, List[Dict]]) -> None:
  """Display posts in a clear, human-readable format."""
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
      print("Caption:")
      print(clean_caption(post['caption']))
      print("-" * 50)
    print()
