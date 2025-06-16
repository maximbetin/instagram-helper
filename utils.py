import logging
from typing import Optional


def setup_logging(name: Optional[str] = None) -> logging.Logger:
  """Configure and return a logger instance with consistent formatting."""
  logging.basicConfig(
      level=logging.INFO,
      format='[%(levelname)s] [%(asctime)s] %(message)s',
      datefmt='%H:%M:%S'
  )
  return logging.getLogger(name or __name__)


# Create a default logger instance
logger = setup_logging()
