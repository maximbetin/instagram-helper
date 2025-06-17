"""Main entry point for Instagram post fetcher application."""

from dotenv import load_dotenv

from data_fetcher import InstagramFetcher
from posts_display import display_posts
from utils import logger

# Load environment variables from .env file
load_dotenv()


def main():
  """Main application entry point."""
  try:
    logger.info("Starting Instagram post fetcher...")
    fetcher = InstagramFetcher()

    logger.info("Fetching recent posts...")
    new_posts = fetcher.get_recent_posts()

    display_posts(new_posts)
    logger.info("Done!")

  except Exception as e:
    logger.error(f"An error occurred: {e}", exc_info=True)
    raise


if __name__ == "__main__":
  main()
