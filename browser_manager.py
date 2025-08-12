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
    INSTAGRAM_URL,
)
from utils import setup_logging

logger = setup_logging(__name__)


# Helper functions no longer needed - all constants come from config.py


def setup_browser(playwright: Playwright) -> Browser:
    """Launch or connect to a Chromium-based browser via Chrome DevTools Protocol.
    
    This function:
    1. Tries to connect to an existing browser on localhost:9222
    2. If no browser found, launches Brave with WSL2-optimized settings starting on Instagram
    3. Falls back to Playwright Chromium as last resort
    """
    port = BROWSER_DEBUG_PORT
    attach_only = BROWSER_ATTACH_ONLY
    host = BROWSER_REMOTE_HOST
    scheme = BROWSER_CONNECT_SCHEME
    
    target_url = f"{scheme}://{host}:{port}"
    logger.debug(f"Connecting to browser via CDP at {target_url}...")

    # Try to connect to existing browser
    try:
        return playwright.chromium.connect_over_cdp(target_url)
    except Exception as connect_error:
        logger.debug(f"Failed to connect to existing browser: {connect_error}")
        
        # If attach-only is enabled, don't launch a new browser
        if attach_only:
            logger.error("Failed to connect to existing browser and attach-only is enabled.")
            raise

        # Try to launch Brave with WSL2-optimized settings
        if BROWSER_PATH and os.path.exists(BROWSER_PATH):
            logger.info("Launching Brave browser with WSL2-optimized settings")
            try:
                # Kill existing browser processes to avoid conflicts
                try:
                    subprocess.run(["taskkill.exe", "/f", "/im", "brave.exe"], 
                                 capture_output=True, check=False)
                    logger.debug("Stopped existing Brave processes")
                except Exception:
                    pass  # taskkill might not be available

                # Configure browser launch arguments using config constants
                
                browser_args = [
                    BROWSER_PATH,
                    f"--remote-debugging-port={port}",
                    "--remote-debugging-address=0.0.0.0",
                    f"--user-data-dir={BROWSER_USER_DATA_DIR}",
                    f"--profile-directory={BROWSER_PROFILE_DIR}",
                    BROWSER_START_URL,
                ]
                
                # Launch browser and wait for it to initialize
                subprocess.Popen(browser_args)
                logger.debug(f"Waiting {BROWSER_LOAD_DELAY / 1000:.1f}s for browser to initialize...")
                time.sleep(BROWSER_LOAD_DELAY / 1000)
                
                return playwright.chromium.connect_over_cdp(target_url)
                
            except Exception as launch_error:
                logger.error(f"Failed to launch Brave browser: {launch_error}")
                # Continue to fallback below

        # Fallback: launch Playwright-managed Chromium
        logger.info("Falling back to Playwright-managed Chromium browser")
        try:
            browser = playwright.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox", 
                    "--disable-dev-shm-usage",
                    f"--remote-debugging-port={port}",
                ],
            )
            logger.info("Chromium browser launched successfully")
            return browser
        except Exception as chromium_error:
            logger.error(f"Failed to launch Chromium browser: {chromium_error}")
            raise