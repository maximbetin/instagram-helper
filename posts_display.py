"""Posts display and formatting module."""

import re
import unicodedata
from datetime import datetime
from typing import Dict, List

import pytz

from config import TIMEZONE


def _remove_emojis_and_hashtags(text: str) -> str:
  """Remove emojis and hashtags from text."""
  # Remove emojis (unicode ranges)
  text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
  # Remove hashtags (but keep mentions and URLs)
  text = re.sub(r'#\w+', '', text)
  return text


def _normalize_and_clean_text(text: str) -> str:
  """Normalize unicode characters and remove non-text elements."""
  # Normalize unicode characters to their standard form
  text = unicodedata.normalize('NFKC', text)
  # Remove any remaining non-text, non-basic punctuation (keep . , ! ? ; : ( ) - and newlines)
  text = re.sub(r'[^\w\s.,!?;:()\-@/\n]', '', text)
  # Remove extra spaces
  text = re.sub(r' +', ' ', text)
  return text


def _clean_lines(text: str) -> str:
  """Clean individual lines and remove non-informative content."""
  lines = text.split('\n')
  cleaned_lines = []

  for line in lines:
    line = line.strip()
    # Remove lines that are only dots, commas, dashes, or empty
    if re.fullmatch(r'[.,:;\-–—]*', line):
      continue
    # Remove lines that are just a few repeated punctuation marks
    if re.fullmatch(r'[.,:;\-–— ]{1,5}', line):
      continue
    # Remove lines that are just a single character
    if len(line) <= 1 and not line.isalnum():
      continue
    cleaned_lines.append(line)

  # Remove consecutive blank lines
  cleaned = '\n'.join([l for i, l in enumerate(cleaned_lines) if l or (i > 0 and cleaned_lines[i - 1])])
  # Remove leading/trailing blank lines
  return cleaned.strip()


def clean_caption(caption: str) -> str:
  """Clean Instagram caption by removing emojis, hashtags, and non-informative content."""
  if not caption:
    return ""

  caption = _remove_emojis_and_hashtags(caption)
  caption = _normalize_and_clean_text(caption)
  caption = _clean_lines(caption)

  return caption


def format_post_date(date_str: str) -> str:
  """Format post date string to readable format."""
  dt = datetime.fromisoformat(date_str)
  return dt.strftime("%Y-%m-%d %H:%M")


def display_posts(posts: Dict[str, List[Dict]]) -> None:
  """Display posts in a formatted manner."""
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
