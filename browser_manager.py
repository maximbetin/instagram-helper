"""Browser management: connect to a real user profile via CDP."""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import time

from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from config import Settings, settings
from utils import setup_logging

logger = setup_logging(__name__)


def _is_wsl2() -> bool:
    return os.name == "posix" and "microsoft" in platform.uname().release.lower()


def _is_port_open(host: str, port: int, timeout: float = 0.3) -> bool:
    """Best-effort check for an open TCP port (IPv4/IPv6)."""
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    for family, socktype, proto, _, addr in infos:
        try:
            with socket.socket(family, socktype, proto) as s:
                s.settimeout(timeout)
                s.connect(addr)
                return True
        except OSError:
            continue
    return False


def _cdp_url(scheme: str, host: str, port: int) -> str:
    return f"{scheme}://{host}:{port}"


def _launch_user_profile_browser(app: Settings) -> subprocess.Popen | None:
    """Launch system browser pointing at the user's profile with a debug port."""
    if not app.BROWSER_PATH or not app.BROWSER_PATH.exists():
        logger.error("BROWSER_PATH is not configured or does not exist.")
        return None

    # Warn if the profile root doesn't exist (to avoid "why am I logged out?" surprises).
    if not app.BROWSER_USER_DATA_DIR or not app.BROWSER_USER_DATA_DIR.exists():
        logger.warning(
            f"User data dir not found: {app.BROWSER_USER_DATA_DIR!s}. "
            "Browser will create a fresh profile (no saved session)."
        )

    args = [
        str(app.BROWSER_PATH),
        f"--remote-debugging-port={app.BROWSER_DEBUG_PORT}",
        f"--user-data-dir={app.BROWSER_USER_DATA_DIR}",
        f"--profile-directory={app.BROWSER_PROFILE_DIR}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ]
    if app.BROWSER_START_URL:
        args.append(app.BROWSER_START_URL)

    try:
        # In WSL2 you can generally call the Windows .exe directly if the path points to it.
        proc = subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        logger.info("Launched system browser with user profile.")
        return proc
    except FileNotFoundError:
        logger.error("Browser binary not found.")
    except Exception as e:
        logger.error(f"Failed to launch browser: {e}")
    return None


def _connect_over_cdp_with_retry(
    playwright: Playwright, url: str, attempts: int = 12, first_delay: float = 0.4
) -> Browser | None:
    delay = first_delay
    for i in range(1, attempts + 1):
        try:
            return playwright.chromium.connect_over_cdp(url)
        except Exception as e:
            if i == attempts:
                logger.error(f"CDP connect failed ({i}/{attempts}) to {url}: {e}")
                return None
            time.sleep(delay)
            delay = min(delay * 1.6, 3.0)
    return None


def setup_browser(playwright: Playwright, app: Settings | None = None) -> Browser:
    """Connect to an existing profile-enabled browser (preferred) or launch it, then connect."""
    app_settings: Settings = app or settings
    url = _cdp_url(
        app_settings.BROWSER_CONNECT_SCHEME,
        app_settings.BROWSER_REMOTE_HOST,
        app_settings.BROWSER_DEBUG_PORT,
    )

    # 1) If a browser is already listening, connect to it
    if _is_port_open(app_settings.BROWSER_REMOTE_HOST, app_settings.BROWSER_DEBUG_PORT):
        logger.info(
            f"Debug port {app_settings.BROWSER_DEBUG_PORT} is open; connecting to existing browser…"
        )
        br = _connect_over_cdp_with_retry(playwright, url)
        if br:
            try:
                v = getattr(br, "version", None)
                version_str = v() if callable(v) else str(v)
                logger.info(f"Connected to browser: {version_str}")
            except Exception:
                pass
            return br
        # If connect failed despite the port being open, fall through and try launching ourselves.

    # 2) Launch the system browser with the configured profile, then connect
    _launch_user_profile_browser(app_settings)
    br = _connect_over_cdp_with_retry(playwright, url)
    if not br:
        raise ConnectionError(
            f"Could not connect to the browser at {url}. "
            "Ensure the debug port is free, the path is correct, and the profile directory is accessible."
        )
    try:
        v = getattr(br, "version", None)
        version_str = v() if callable(v) else str(v)
        logger.info(f"Connected to browser: {version_str}")
    except Exception:
        pass
    return br


def setup_profile_context_and_page(
    playwright: Playwright, app: Settings | None = None
) -> tuple[Browser, BrowserContext, Page]:
    """Return (browser, persistent_context, page) using the user's real profile.

    With CDP+persistent profiles, Playwright exposes an existing context.
    Creating new incognito contexts is usually unsupported; reuse the first.
    """
    app_settings: Settings = app or settings
    browser = setup_browser(playwright, app_settings)

    # Contexts can appear with a small delay right after connect.
    if not browser.contexts:
        time.sleep(0.3)

    if not browser.contexts:
        raise RuntimeError(
            "No browser contexts available after CDP connect. Is the profile locked?"
        )

    context = browser.contexts[0]  # persistent profile context

    # Reuse an existing page if present; otherwise open one.
    page = context.pages[0] if context.pages else context.new_page()

    # Optional: default timeouts aligned with app settings
    if getattr(app_settings, "INSTAGRAM_POST_LOAD_TIMEOUT", None):
        page.set_default_timeout(app_settings.INSTAGRAM_POST_LOAD_TIMEOUT)

    # If we created a fresh page and you configured a start URL, open it to ensure cookies/session load.
    if app_settings.BROWSER_START_URL and (
        len(context.pages) == 1 and page.url in ("about:blank", "")
    ):
        try:
            page.goto(app_settings.BROWSER_START_URL, wait_until="domcontentloaded")
        except Exception:
            pass

    return browser, context, page
