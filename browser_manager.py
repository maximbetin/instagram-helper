"""Browser management functionality."""

import subprocess
import time
from typing import TYPE_CHECKING

from playwright.sync_api import Browser

from config import BROWSER_DEBUG_PORT, BROWSER_LOAD_DELAY, BROWSER_PATH, INSTAGRAM_URL
from utils import setup_logging

if TYPE_CHECKING:
    from playwright.sync_api import Playwright

logger = setup_logging(__name__)


def setup_browser(playwright: "Playwright") -> Browser:
    """Launch and connect to the browser instance."""
    logger.info(f"Starting the browser at page {INSTAGRAM_URL}...")
    subprocess.Popen([BROWSER_PATH, f"--remote-debugging-port={BROWSER_DEBUG_PORT}", INSTAGRAM_URL])
    logger.debug(f"Waiting {BROWSER_LOAD_DELAY} seconds for the browser to load...")
    time.sleep(BROWSER_LOAD_DELAY)
    logger.debug(f"Connecting to the browser at port {BROWSER_DEBUG_PORT}...")
    return playwright.chromium.connect_over_cdp(f"http://localhost:{BROWSER_DEBUG_PORT}")
