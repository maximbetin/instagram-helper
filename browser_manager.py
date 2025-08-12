"""Browser management functionality."""

from playwright.sync_api import Browser, Playwright

from utils import setup_logging

logger = setup_logging(__name__)


def setup_browser(playwright: Playwright) -> Browser:
    """Launch a Chromium browser using Playwright's built-in browser management.

    Playwright automatically handles browser installation and launching.
    """
    logger.info("Launching Chromium browser using Playwright...")

    try:
        # Launch a new Chromium browser instance
        # Playwright handles all browser installation and management automatically
        browser = playwright.chromium.launch(
            headless=False,  # Show browser window for debugging
            args=[
                "--no-sandbox",  # Required for some Linux environments
                "--disable-dev-shm-usage",  # Overcome limited resource problems
            ]
        )

        logger.info("Browser launched successfully")
        return browser

    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        raise
