import logging

from dotenv import load_dotenv

from data_fetcher import InstagramFetcher
from posts_display import display_posts

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] [%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
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
