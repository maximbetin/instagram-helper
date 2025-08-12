"""Browser management functionality."""

import os
import subprocess
import time

from playwright.sync_api import Browser, Playwright

from config import (
    BROWSER_ATTACH_ONLY,
    BROWSER_CONNECT_SCHEME,
    BROWSER_DEBUG_PORT,
    BROWSER_LOAD_DELAY,
    BROWSER_PATH,
    BROWSER_PROFILE_DIR,
    BROWSER_REMOTE_HOST,
    BROWSER_START_URL,
    BROWSER_USER_DATA_DIR,
)
from utils import setup_logging

logger = setup_logging(__name__)


def _connect_to_browser(playwright: Playwright, url: str) -> Browser | None:
    """Try to connect to an existing browser instance over CDP."""
    try:
        browser = playwright.chromium.connect_over_cdp(url)
        logger.info(f"Successfully connected to existing browser at {url}")
        return browser
    except Exception as e:
        logger.debug(f"Could not connect to existing browser at {url}: {e}")
        return None


def _kill_existing_brave_processes() -> None:
    """Attempt to kill existing Brave processes to prevent conflicts."""
    if not BROWSER_PATH or "taskkill.exe" not in BROWSER_PATH.lower():
        return
    try:
        subprocess.run(
            ["taskkill.exe", "/f", "/im", "brave.exe"],
            capture_output=True,
            check=False,
            text=True,
        )
        logger.debug("Attempted to stop existing Brave browser processes.")
    except FileNotFoundError:
        logger.debug(
            "'taskkill.exe' not found. "
            "Skipping process cleanup. "
            "This is expected if not on WSL with Windows interop."
        )
    except Exception as e:
        logger.warning(f"An error occurred while trying to kill Brave processes: {e}")


def _launch_brave_browser(
    playwright: Playwright, url: str, port: int
) -> Browser | None:
    """Launch Brave browser with specific user data and debugging port."""
    if not (BROWSER_PATH and os.path.exists(BROWSER_PATH)):
        logger.debug(
            "Brave browser path not configured or not found. Skipping Brave launch."
        )
        return None

    logger.info("Attempting to launch Brave browser...")
    _kill_existing_brave_processes()

    browser_args = [
        BROWSER_PATH,
        f"--remote-debugging-port={port}",
        "--remote-debugging-address=0.0.0.0",
        f"--user-data-dir={BROWSER_USER_DATA_DIR}",
        f"--profile-directory={BROWSER_PROFILE_DIR}",
        BROWSER_START_URL,
    ]

    try:
        subprocess.Popen(browser_args)
        logger.debug(
            f"Waiting {BROWSER_LOAD_DELAY / 1000:.1f}s for Brave to initialize..."
        )
        time.sleep(BROWSER_LOAD_DELAY / 1000)
        # Try connecting after launch
        return _connect_to_browser(playwright, url)
    except Exception as e:
        logger.error(f"Failed to launch Brave browser: {e}")
        return None


def _launch_playwright_chromium(playwright: Playwright, port: int) -> Browser:
    """Launch a managed Playwright Chromium instance as a fallback."""
    logger.info("Falling back to Playwright-managed Chromium browser.")
    try:
        return playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--remote-debugging-port={port}",
            ],
        )
    except Exception as e:
        logger.critical(f"Failed to launch Playwright Chromium: {e}")
        raise


def setup_browser(playwright: Playwright) -> Browser:
    """Set up and return a browser instance.

    This function attempts the following strategies in order:
    1. Connect to an existing browser instance.
    2. If BROWSER_PATH is set, launch a local Brave browser with custom user data.
    3. If BROWSER_ATTACH_ONLY is true, it will not proceed to launch a browser.
    4. As a fallback, launch a new Playwright-managed Chromium instance.
    """
    target_url = (
        f"{BROWSER_CONNECT_SCHEME}://{BROWSER_REMOTE_HOST}:{BROWSER_DEBUG_PORT}"
    )
    logger.debug(f"Attempting to connect to browser at {target_url}")

    # 1. Try to connect to an existing browser
    if browser := _connect_to_browser(playwright, target_url):
        return browser

    # If attach-only is enabled, fail here
    if BROWSER_ATTACH_ONLY:
        logger.error("Failed to connect to browser, and BROWSER_ATTACH_ONLY is enabled.")
        raise ConnectionError(f"Could not connect to browser at {target_url}")

    # 2. Try to launch local Brave browser
    if browser := _launch_brave_browser(playwright, target_url, BROWSER_DEBUG_PORT):
        logger.info("Successfully launched and connected to Brave browser.")
        return browser

    # 3. Fallback to Playwright-managed Chromium
    browser = _launch_playwright_chromium(playwright, BROWSER_DEBUG_PORT)
    logger.info("Successfully launched Playwright-managed Chromium browser.")
    return browser
