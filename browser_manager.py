"""Browser management functionality."""

from __future__ import annotations

import subprocess
import time
from typing import TYPE_CHECKING

from playwright.sync_api import Browser, Error, Playwright

from config import settings
from utils import setup_logging

if TYPE_CHECKING:
    from config import Settings

logger = setup_logging(__name__)


def _kill_existing_browser_processes() -> None:
    """Attempts to kill existing browser processes to prevent conflicts.

    This is a Windows-specific solution using `taskkill` and is intended
    for WSL environments to manage the host's browser processes.
    """
    if (
        not settings.BROWSER_PATH
        or "brave.exe" not in settings.BROWSER_PATH.name.lower()
    ):
        logger.debug("Skipping process kill: Not configured for Brave on Windows.")
        return

    try:
        subprocess.run(
            ["taskkill.exe", "/f", "/im", "brave.exe"],
            capture_output=True,
            check=False,
            text=True,
        )
        logger.info("Attempted to stop existing Brave browser processes.")
    except FileNotFoundError:
        logger.debug(
            "'taskkill.exe' not found. Skipping process cleanup. "
            "This is expected on non-Windows systems."
        )
    except Exception as e:
        logger.warning(f"An error occurred while trying to kill Brave processes: {e}")


def _launch_local_browser(
    playwright: Playwright, app_settings: Settings
) -> Browser | None:
    """Launches a local browser with remote debugging enabled."""
    if not app_settings.BROWSER_PATH or not app_settings.BROWSER_PATH.exists():
        logger.debug("Browser path not configured or not found. Skipping local launch.")
        return None

    logger.info("Attempting to launch local browser...")
    _kill_existing_browser_processes()

    browser_args = [
        str(app_settings.BROWSER_PATH),
        f"--remote-debugging-port={app_settings.BROWSER_DEBUG_PORT}",
        f"--user-data-dir={app_settings.BROWSER_USER_DATA_DIR}",
        f"--profile-directory={app_settings.BROWSER_PROFILE_DIR}",
        app_settings.BROWSER_START_URL,
    ]

    try:
        subprocess.Popen(browser_args)
        logger.debug(
            f"Waiting {app_settings.BROWSER_LOAD_DELAY / 1000:.1f}s for browser..."
        )
        time.sleep(app_settings.BROWSER_LOAD_DELAY / 1000)

        # Try to connect to the newly launched browser
        connect_url = (
            f"{app_settings.BROWSER_CONNECT_SCHEME}://"
            f"{app_settings.BROWSER_REMOTE_HOST}:{app_settings.BROWSER_DEBUG_PORT}"
        )

        try:
            browser = playwright.chromium.connect_over_cdp(connect_url)
            logger.info(
                f"Successfully connected to newly launched browser at {connect_url}"
            )
            return browser
        except Exception as e:
            if "ECONNREFUSED" in str(e):
                logger.error(
                    f"Connection refused to browser at {connect_url}. "
                    "Please close any existing browser instances and try again."
                )
            else:
                logger.error(f"Failed to connect to newly launched browser: {e}")
            return None

    except Exception as e:
        logger.error(f"Failed to launch local browser: {e}")
        return None


def _launch_playwright_chromium(
    playwright: Playwright, app_settings: Settings
) -> Browser:
    """Launches a managed Playwright Chromium instance as a fallback."""
    logger.info("Falling back to Playwright-managed Chromium browser.")
    try:
        return playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--remote-debugging-port={app_settings.BROWSER_DEBUG_PORT}",
            ],
        )
    except (Error, Exception) as e:
        logger.critical(f"Failed to launch Playwright Chromium: {e}")
        raise


def setup_browser(playwright: Playwright) -> Browser:
    """Sets up and returns a browser instance.

    This function follows a specific strategy to establish a browser connection:
    1. Attempts to launch a local browser instance (e.g., Brave) if configured.
    2. If local launch fails, falls back to launching a Playwright-managed Chromium instance.
    3. Provides clear error messages for connection issues.

    Returns:
        A Playwright `Browser` instance.

    Raises:
        ConnectionError: If no browser connection can be established.
    """
    logger.info("Setting up browser instance...")

    # 1. Try to launch a local browser if configured
    if browser := _launch_local_browser(playwright, settings):
        logger.info("Successfully launched and connected to local browser.")
        return browser

    # 2. Fallback to Playwright-managed Chromium
    logger.warning(
        "Could not launch a local browser. Falling back to Playwright-managed Chromium."
    )
    try:
        browser = _launch_playwright_chromium(playwright, settings)
        logger.info("Successfully launched Playwright-managed Chromium browser.")
        return browser
    except Exception:
        logger.critical("All attempts to set up a browser have failed.")
        raise ConnectionError("Could not launch any browser.") from None
