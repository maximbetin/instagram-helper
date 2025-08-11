"""Browser management functionality."""

import subprocess
import time
import requests

from playwright.sync_api import Browser, Playwright

from config import (
    BROWSER_DEBUG_PORT,
    BROWSER_LOAD_DELAY,
    BROWSER_PATH,
    INSTAGRAM_URL,
    LOCALHOST_URL,
    SECONDS_IN_MS,
    WSL2_MODE,
    WSL_HOST_IP,
)
from utils import setup_logging

logger = setup_logging(__name__)


def launch_windows_brave() -> None:
    """Launch Windows Brave with remote debugging enabled for WSL2 access."""
    logger.info("Launching Windows Brave with remote debugging...")
    
    try:
        # Launch Brave with remote debugging on all interfaces
        subprocess.Popen([
            BROWSER_PATH,
            f"--remote-debugging-port={BROWSER_DEBUG_PORT}",
            "--remote-debugging-address=0.0.0.0",
            INSTAGRAM_URL,
        ])
        
        logger.info(f"Brave launched with debugging port {BROWSER_DEBUG_PORT}")
        logger.info("Note: This exposes the debugging port on your Windows host network")
        
    except (subprocess.SubprocessError, OSError) as e:
        logger.error(f"Failed to launch Windows Brave: {e}")
        logger.error("Please ensure Brave is installed and the path is correct")
        raise


def connect_to_existing_browser(playwright: Playwright) -> Browser:
    """Connect to an existing browser instance via CDP."""
    logger.info(f"Connecting to existing browser at {WSL_HOST_IP}:{BROWSER_DEBUG_PORT}...")
    
    try:
        # Try to discover the WebSocket endpoint
        debug_url = f"http://{WSL_HOST_IP}:{BROWSER_DEBUG_PORT}/json/version"
        logger.debug(f"Checking debug endpoint: {debug_url}")
        
        response = requests.get(debug_url, timeout=10)
        response.raise_for_status()
        
        ws_info = response.json()
        ws_url = ws_info["webSocketDebuggerUrl"]
        
        # Replace the host IP in the WebSocket URL if needed
        if WSL2_MODE:
            if "127.0.0.1" in ws_url:
                ws_url = ws_url.replace("127.0.0.1", WSL_HOST_IP)
            if "localhost" in ws_url:
                ws_url = ws_url.replace("localhost", WSL_HOST_IP)
        
        logger.debug(f"Connecting via WebSocket: {ws_url}")
        return playwright.chromium.connect_over_cdp(ws_url)
        
    except requests.RequestException as e:
        logger.error(f"Failed to connect to browser debug endpoint: {e}")
        if WSL2_MODE:
            logger.error("Make sure Brave is running with --remote-debugging-port=9222 --remote-debugging-address=0.0.0.0")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to browser: {e}")
        raise


def setup_browser(playwright: Playwright) -> Browser:
    """Launch and connect to the browser instance."""
    logger.info(f"Starting browser at {INSTAGRAM_URL}...")

    if WSL2_MODE:
        logger.info("WSL2 mode detected - connecting to Windows Brave")
        
        # First try to connect to existing instance
        try:
            return connect_to_existing_browser(playwright)
        except Exception as e:
            logger.warning(f"Could not connect to existing browser: {e}")
            logger.info("Attempting to launch new Windows Brave instance...")
            
            # Launch new instance if connection failed
            launch_windows_brave()
            
            logger.debug(f"Waiting {BROWSER_LOAD_DELAY / SECONDS_IN_MS}s for browser to load...")
            time.sleep(BROWSER_LOAD_DELAY / SECONDS_IN_MS)
            
            # Try to connect again
            return connect_to_existing_browser(playwright)
    else:
        # Original Linux behavior
        logger.info("Linux mode - launching local browser")
        
        try:
            subprocess.Popen([
                BROWSER_PATH,
                f"--remote-debugging-port={BROWSER_DEBUG_PORT}",
                INSTAGRAM_URL,
            ])

            logger.debug(f"Waiting {BROWSER_LOAD_DELAY / SECONDS_IN_MS}s for browser to load...")
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
