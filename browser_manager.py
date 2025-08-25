"""Browser management functionality."""

from __future__ import annotations

import os
import subprocess
import time
from typing import TYPE_CHECKING

from playwright.sync_api import Browser, Playwright

from config import settings
from utils import setup_logging

if TYPE_CHECKING:
    from config import Settings

logger = setup_logging(__name__)


def _kill_existing_browser_processes() -> None:
    """Attempts to kill existing browser processes to prevent conflicts."""
    if not settings.BROWSER_PATH:
        return

    browser_name = settings.BROWSER_PATH.name.lower()

    # Handle different operating systems and WSL2 scenarios
    if "brave" in browser_name:
        try:
            # Check if we're in WSL2 (Linux shell but Windows browser path)
            is_wsl2 = (
                os.name == "posix"
                and "microsoft" in os.uname().release.lower()
                and (
                    "win" in str(settings.BROWSER_PATH).lower()
                    or ".exe" in str(settings.BROWSER_PATH).lower()
                )
            )

            if is_wsl2 or "win" in os.name.lower():
                # Windows or WSL2 with Windows browser
                try:
                    # Try using wsl.exe to run Windows commands
                    subprocess.run(
                        ["wsl.exe", "taskkill.exe", "/f", "/im", "brave.exe"],
                        capture_output=True,
                        check=False,
                        text=True,
                    )
                except FileNotFoundError:
                    # Fallback to direct Windows command if wsl.exe not available
                    subprocess.run(
                        ["taskkill.exe", "/f", "/im", "brave.exe"],
                        capture_output=True,
                        check=False,
                        text=True,
                    )
            else:
                # Native Linux/macOS
                subprocess.run(
                    ["pkill", "-f", "brave"],
                    capture_output=True,
                    check=False,
                    text=True,
                )
            logger.info("Attempted to stop existing Brave browser processes.")
        except FileNotFoundError:
            logger.debug("Process killing command not found, skipping cleanup")
        except Exception as e:
            logger.warning(f"Error while trying to kill Brave processes: {e}")


def _launch_local_browser(
    playwright: Playwright, app_settings: Settings
) -> Browser | None:
    """Launches a local browser with remote debugging enabled."""
    if not app_settings.BROWSER_PATH or not app_settings.BROWSER_PATH.exists():
        logger.debug("Browser path not configured or not found.")
        return None

    logger.info("Attempting to launch local browser...")
    _kill_existing_browser_processes()

    # Check if we're in WSL2 with Windows browser
    is_wsl2 = (
        os.name == "posix"
        and "microsoft" in os.uname().release.lower()
        and (
            "win" in str(app_settings.BROWSER_PATH).lower()
            or ".exe" in str(app_settings.BROWSER_PATH).lower()
        )
    )

    # Add platform-specific arguments
    browser_args = [
        str(app_settings.BROWSER_PATH),
        f"--remote-debugging-port={app_settings.BROWSER_DEBUG_PORT}",
        f"--user-data-dir={app_settings.BROWSER_USER_DATA_DIR}",
        f"--profile-directory={app_settings.BROWSER_PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        app_settings.BROWSER_START_URL,
    ]

    try:
        # Use different subprocess approach for WSL2 vs native
        if is_wsl2:
            # In WSL2, we need to launch the Windows browser from Windows
            try:
                # Try using wsl.exe to launch Windows browser
                wsl_args = ["wsl.exe"] + browser_args
                process = subprocess.Popen(
                    wsl_args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
            except FileNotFoundError:
                # Fallback to direct launch
                process = subprocess.Popen(
                    browser_args,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
        else:
            # Native Linux/macOS launch
            process = subprocess.Popen(
                browser_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

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
            logger.info(f"Successfully connected to browser at {connect_url}")
            return browser
        except Exception as e:
            if "ECONNREFUSED" in str(e):
                logger.error(
                    f"Connection refused to browser at {connect_url}. "
                    "Please close any existing browser instances and try again."
                )
            else:
                logger.error(f"Failed to connect to browser: {e}")

            # Try to clean up the process if connection failed
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception:
                pass
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
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--no-first-run",
                "--no-default-browser-check",
                f"--remote-debugging-port={app_settings.BROWSER_DEBUG_PORT}",
            ],
        )
    except Exception as e:
        logger.critical(f"Failed to launch Playwright Chromium: {e}")
        raise


def setup_browser(playwright: Playwright) -> Browser:
    """Sets up and returns a browser instance.

    This function follows a specific strategy to establish a browser connection:
    1. Attempts to launch a local browser instance (e.g., Brave) if configured.
    2. If local launch fails, falls back to launching a Playwright-managed
       Chromium instance.
    3. Provides clear error messages for connection issues.

    Returns:
        A Playwright `Browser` instance.

    Raises:
        ConnectionError: If no browser connection can be established.
    """
    logger.info("Setting up browser instance...")

    # Try to launch a local browser if configured
    try:
        if browser := _launch_local_browser(playwright, settings):
            logger.info("Successfully launched and connected to local browser.")
            return browser
    except Exception as e:
        logger.warning(f"Local browser launch failed: {e}")

    # Fallback to Playwright-managed Chromium
    logger.info("Falling back to Playwright-managed Chromium browser.")
    try:
        browser = _launch_playwright_chromium(playwright, settings)
        logger.info("Successfully launched Playwright-managed Chromium browser.")
        return browser
    except Exception as e:
        logger.critical(f"Failed to launch Playwright-managed Chromium: {e}")
        raise ConnectionError("Could not launch any browser.") from None
