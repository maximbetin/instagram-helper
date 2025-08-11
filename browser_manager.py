"""Browser management functionality."""

import subprocess
import time

from playwright.sync_api import Browser, Playwright

from config import (
    BROWSER_DEBUG_PORT,
    BROWSER_LOAD_DELAY,
    BROWSER_PATH,
    INSTAGRAM_URL,
    LOCALHOST_URL,
    SECONDS_IN_MS,
)
from utils import setup_logging

logger = setup_logging(__name__)


def setup_browser(playwright: Playwright) -> Browser:
    """Launch and connect to the browser instance."""
    logger.info(f"Starting browser at {INSTAGRAM_URL}...")

    try:
        # Attempt to launch the configured browser; rely on environment override for portability
        subprocess.Popen(
            [
                BROWSER_PATH,
                f"--remote-debugging-port={BROWSER_DEBUG_PORT}",
                INSTAGRAM_URL,
            ]
        )

        logger.debug(
            f"Waiting {BROWSER_LOAD_DELAY / SECONDS_IN_MS}s for browser to load..."
        )
        time.sleep(BROWSER_LOAD_DELAY / SECONDS_IN_MS)

        logger.debug(f"Connecting to browser at port {BROWSER_DEBUG_PORT}...")
        return playwright.chromium.connect_over_cdp(
            f"{LOCALHOST_URL}{BROWSER_DEBUG_PORT}"
        )

    except (subprocess.SubprocessError, ValueError, OSError) as e:
        logger.error(f"Failed to start or connect to browser: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error setting up browser: {e}")
        raise
