"""Browser management functionality."""

import os

from playwright.sync_api import Browser, Playwright

from utils import setup_logging

logger = setup_logging(__name__)


def setup_browser(playwright: Playwright) -> Browser:
    """Launch a browser using Playwright.

    For WSL2, the recommended approach is to connect to an already running
    Brave browser with remote debugging enabled.
    """
    # Check if we should connect to an existing browser
    browser_debug_port = os.getenv("BROWSER_DEBUG_PORT", "9222")
    browser_path = os.getenv("BROWSER_PATH")

    # Try to connect to an existing browser first (recommended for WSL2)
    try:
        logger.info(
            f"Attempting to connect to existing browser on port {browser_debug_port}..."
        )
        browser = playwright.chromium.connect_over_cdp(
            f"http://localhost:{browser_debug_port}"
        )
        logger.info("Successfully connected to existing browser!")
        return browser
    except Exception as e:
        logger.info(f"Could not connect to existing browser: {e}")
        logger.info("Falling back to launching new browser...")

    # Try to launch from specified path if available
    if browser_path and os.path.exists(browser_path):
        logger.info(f"Launching browser from path: {browser_path}")
        try:
            # Launch the specified browser executable
            browser = playwright.chromium.launch(
                headless=False,  # Show browser window for debugging
                executable_path=browser_path,
                args=[
                    "--no-sandbox",  # Required for some Linux environments
                    "--disable-dev-shm-usage",  # Overcome limited resource problems
                    "--remote-debugging-port=9222",  # Enable remote debugging
                ],
            )
            logger.info("Browser launched successfully")
            return browser
        except Exception as e:
            logger.warning(f"Failed to launch browser from {browser_path}: {e}")
            logger.info("Falling back to Chromium...")

    # Fallback to Chromium
    logger.info("Launching Chromium browser using Playwright...")
    try:
        # Launch a new Chromium browser instance
        # Playwright handles all browser installation and management automatically
        browser = playwright.chromium.launch(
            headless=False,  # Show browser window for debugging
            args=[
                "--no-sandbox",  # Required for some Linux environments
                "--disable-dev-shm-usage",  # Overcome limited resource problems
                "--remote-debugging-port=9222",  # Enable remote debugging
            ],
        )

        logger.info("Browser launched successfully")
        return browser

    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
        raise
