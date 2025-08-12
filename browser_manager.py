"""Browser management functionality."""

import os
import subprocess
import time

from playwright.sync_api import Browser, Playwright

from utils import setup_logging

logger = setup_logging(__name__)


def detect_wsl_host_ip() -> str | None:
    """Return Windows host IP from inside WSL2 by reading /etc/resolv.conf.

    Uses the first nameserver entry. Returns None if not found or on error.
    """
    try:
        with open("/etc/resolv.conf", encoding="utf-8") as resolv:
            for line in resolv:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[0] == "nameserver":
                    return parts[1]
    except Exception:
        return None
    return None


def _get_bool_env(name: str, default: bool = False) -> bool:
    """Return a boolean from environment variable."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _get_int_env(name: str, default: int) -> int:
    """Return an int from environment variable with a safe fallback."""
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def setup_browser(playwright: Playwright) -> Browser:
    """Launch or attach to a Chromium-based browser over CDP.

    In WSL2, this attaches to a pre-started Windows Brave with
    --remote-debugging-port, reusing your existing session.
    """
    scheme = os.getenv("BROWSER_CONNECT_SCHEME", "http")
    port = _get_int_env("BROWSER_DEBUG_PORT", 9222)
    attach_only = _get_bool_env("BROWSER_ATTACH_ONLY", False) or _get_bool_env(
        "BROWSER_REQUIRE_EXISTING", False
    )

    # Resolve host preference order
    # 1) Explicit full CDP URL
    cdp_url = os.getenv("BROWSER_CDP_URL")
    if cdp_url:
        target_url = cdp_url
    else:
        # 2) Explicit remote host
        host: str | None = os.getenv("BROWSER_REMOTE_HOST") or os.getenv(
            "BROWSER_DEBUG_HOST"
        )
        # 3) Auto-detect Windows host inside WSL when in attach-only mode
        if not host and attach_only:
            host = detect_wsl_host_ip()
            if host:
                logger.info(
                    f"Attach-only mode: detected Windows host IP {host} from /etc/resolv.conf"
                )

        if not host:
            host = "localhost"

        target_url = f"{scheme}://{host}:{port}"

    logger.debug(f"Connecting to browser via CDP at {target_url}...")

    try:
        return playwright.chromium.connect_over_cdp(target_url)
    except Exception as connect_error:
        # If attach-only is required, do not spawn a local browser
        if attach_only:
            logger.error(
                "Failed to connect to existing browser and attach-only is enabled."
            )
            raise

        # Optional: attempt to start a local browser if a path is provided
        browser_path = os.getenv("BROWSER_PATH")
        if browser_path and os.path.exists(browser_path):
            logger.info(f"Launching browser from path: {browser_path}")
            try:
                subprocess.Popen(
                    [
                        browser_path,
                        f"--remote-debugging-port={port}",
                    ]
                )
                # Wait for the browser to initialize
                delay_ms = _get_int_env("BROWSER_LOAD_DELAY", 5000)
                logger.debug(f"Waiting {delay_ms / 1000:.2f}s for browser to load...")
                time.sleep(delay_ms / 1000)
                return playwright.chromium.connect_over_cdp(target_url)
            except Exception as launch_error:
                logger.error(f"Failed to start or connect to browser: {launch_error}")
                raise

        # Fallback: launch a Playwright-managed Chromium if attach-only is not required
        logger.error(f"Failed to connect to browser at {target_url}: {connect_error}")
        logger.info("Falling back to launching a new Chromium instance via Playwright...")
        try:
            browser = playwright.chromium.launch(
                headless=False,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    f"--remote-debugging-port={port}",
                ],
            )
            logger.info("Browser launched successfully")
            return browser
        except Exception as launch_chromium_error:
            logger.error(f"Failed to launch Chromium: {launch_chromium_error}")
            raise
