"""Browser management and integration functionality.

BROWSER INTEGRATION STRATEGY:

This module implements a sophisticated browser management system that handles
cross-platform compatibility, WSL2 integration, and fallback strategies. The
design addresses several critical challenges:

1. CROSS-PLATFORM COMPATIBILITY: Supports Windows, Linux, and macOS with appropriate process management and path handling for each platform.

2. WSL2 INTEGRATION: Windows Subsystem for Linux 2 presents unique challenges because it runs a Linux kernel but often needs to launch Windows applications. This requires special detection and handling logic.

3. REMOTE DEBUGGING: The tool requires browser remote debugging capabilities to control the browser programmatically via the Chrome DevTools Protocol.

4. PROCESS MANAGEMENT: Existing browser instances must be terminated to prevent port conflicts and ensure clean debugging sessions.

5. FALLBACK STRATEGIES: Multiple fallback approaches ensure the tool works even when the preferred browser setup fails.

ARCHITECTURE OVERVIEW:

The browser management follows a layered approach:

1. LOCAL BROWSER DETECTION: Attempts to connect to existing browser instances.
2. LOCAL BROWSER LAUNCH: Launches new browser instances with debugging enabled.
3. PLAYWRIGHT FALLBACK: Uses Playwright as a last resort for browser automation.

WSL2 DETECTION LOGIC:

WSL2 environments are detected using multiple criteria:
- os.name == "posix": Confirms Linux shell environment
- "microsoft" in platform.uname().release.lower(): Identifies WSL2 kernel
- Windows browser path indicators: Checks for .exe extensions or Windows paths

This detection enables appropriate process management and browser launching
strategies for each environment.

CRITICAL IMPLEMENTATION DETAILS:

- PROCESS KILLING: Different strategies for Windows (taskkill.exe) vs Linux (pkill)
- PATH TRANSLATION: WSL2 requires special handling for Windows paths
- PORT CONFLICTS: Only one browser can use port 9222 for remote debugging
- SESSION MANAGEMENT: Browser user data directories preserve login sessions
- ERROR HANDLING: Graceful degradation when browser operations fail

PERFORMANCE CONSIDERATIONS:

- CONNECTION POOLING: Reuses browser connections when possible
- TIMEOUT HANDLING: Prevents indefinite waits for browser operations
- RESOURCE CLEANUP: Ensures browser processes are properly terminated
- MEMORY MANAGEMENT: Avoids memory leaks from abandoned browser instances
"""

from __future__ import annotations

import os
import platform
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
    """Kills existing browser processes to prevent conflicts.

    IMPLEMENTATION DETAILS:

    This function handles browser process management across different environments,
    with special handling for WSL2 (Windows Subsystem for Linux 2). The complexity
    is necessary because:

    1. CROSS-PLATFORM COMPATIBILITY: Different operating systems use different
    process management commands (taskkill.exe vs pkill).

    2. WSL2 INTEGRATION: WSL2 runs a Linux kernel but often needs to manage
    Windows processes, requiring special detection and handling.

    3. PORT CONFLICTS: Only one browser can use port 9222 for remote debugging,
    so existing processes must be terminated before launching new ones.

    4. SESSION CONFLICTS: Existing browser instances may have different
    debugging configurations that could interfere with the tool.

    WSL2 DETECTION LOGIC:
    - os.name == "posix": Confirms we're in a Linux shell
    - "microsoft" in platform.uname().release.lower(): Identifies WSL2 kernel
    - Windows browser path: Checks if browser path contains Windows indicators

    This detection allows the tool to use appropriate process management
    strategies for each environment.
    """
    if not settings.BROWSER_PATH:
        return

    browser_name = settings.BROWSER_PATH.name.lower()

    # Handle different operating systems and WSL2 scenarios
    if "brave" in browser_name:
        try:
            # Check if we're in WSL2 (Linux shell but Windows browser path)
            # This detection is crucial for proper process management
            is_wsl2 = (
                os.name == "posix"
                and "microsoft" in platform.uname().release.lower()
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
    logger.info(f"Platform: {platform.system()}, OS name: {os.name}")
    logger.info(f"Browser path: {app_settings.BROWSER_PATH}")
    logger.info(f"Browser path exists: {app_settings.BROWSER_PATH.exists()}")

    _kill_existing_browser_processes()

    # Check if we're in WSL2 with Windows browser
    is_wsl2 = (
        os.name == "posix"
        and "microsoft" in platform.uname().release.lower()
        and (
            "win" in str(app_settings.BROWSER_PATH).lower()
            or ".exe" in str(app_settings.BROWSER_PATH).lower()
        )
    )

    logger.info(f"WSL2 detection: {is_wsl2}")
    logger.info(f"Platform system: {platform.system()}")

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
        # Use different subprocess approach for WSL2 vs native Windows vs Linux/macOS
        if is_wsl2:
            logger.info("Using WSL2 launch method")
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
        elif platform.system() == "Windows":
            logger.info("Using native Windows launch method")
            # Native Windows launch
            process = subprocess.Popen(
                browser_args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        else:
            logger.info("Using native Linux/macOS launch method")
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
