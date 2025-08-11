"""Browser management functionality."""

import subprocess
import time

from playwright.sync_api import Browser, Playwright

from config import BROWSER_DEBUG_PORT, BROWSER_LOAD_DELAY, BROWSER_PATH, INSTAGRAM_URL
from utils import setup_logging

logger = setup_logging(__name__)


def setup_browser(playwright: Playwright) -> Browser:
    """Launch and connect to the browser instance."""
    logger.info(f"Starting browser at {INSTAGRAM_URL}...")

    try:
        subprocess.Popen(
            [
                BROWSER_PATH,
                f"--remote-debugging-port={BROWSER_DEBUG_PORT}",
                INSTAGRAM_URL,
            ]
        )

        logger.debug(f"Waiting {BROWSER_LOAD_DELAY / 1000}s for browser to load...")
        time.sleep(BROWSER_LOAD_DELAY / 1000)

        logger.debug(f"Connecting to browser at port {BROWSER_DEBUG_PORT}...")
        return playwright.chromium.connect_over_cdp(
            f"http://localhost:{BROWSER_DEBUG_PORT}"
        )

    except subprocess.SubprocessError as e:
        logger.error(f"Failed to start browser: {e}")
        raise
    except (ValueError, OSError) as e:
        logger.error(f"System error connecting to browser: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to browser: {e}")
        raise
