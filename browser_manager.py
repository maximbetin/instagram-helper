"""Browser management functionality."""

import subprocess
import time

from playwright.sync_api import Browser, Playwright

from config import (
    BROWSER_ATTACH_ONLY,
    BROWSER_CONNECT_SCHEME,
    BROWSER_DEBUG_PORT,
    BROWSER_LOAD_DELAY,
    BROWSER_PATH,
    BROWSER_REMOTE_HOST,
    INSTAGRAM_URL,
    LOCALHOST_URL,
    SECONDS_IN_MS,
)
from utils import setup_logging

logger = setup_logging(__name__)


def setup_browser(playwright: Playwright) -> Browser:
    """Launch or attach to a Chromium-based browser over CDP.

    Supports WSL2→Windows Brave by skipping local spawn and attaching to a
    pre-started Windows Brave with --remote-debugging-port.
    """
    logger.info(f"Preparing browser connection to {INSTAGRAM_URL}...")

    try:
        # Determine target host for CDP
        target_host = BROWSER_REMOTE_HOST if BROWSER_REMOTE_HOST else "localhost"
        target_base = (
            f"{BROWSER_CONNECT_SCHEME}://{target_host}:{BROWSER_DEBUG_PORT}"
        )

        if not BROWSER_ATTACH_ONLY and target_host == "localhost":
            # Attempt to launch a local browser only when attaching to localhost
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
        else:
            logger.info(
                "Attach-only mode enabled or remote host provided; skipping local browser launch."
            )

        logger.debug(
            f"Connecting to browser via CDP at {target_base} (port {BROWSER_DEBUG_PORT})..."
        )
        return playwright.chromium.connect_over_cdp(target_base)

    except (subprocess.SubprocessError, ValueError, OSError) as e:
        logger.error(f"Failed to start or connect to browser: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error setting up browser: {e}")
        raise
