"""Configuration settings for Instagram Helper."""

import os
import subprocess
from datetime import timedelta, timezone

# Time constants
SECONDS_IN_MS = 1000
DEFAULT_TIMEZONE_OFFSET = 2

# Protocol constants
FILE_PROTOCOL = "file://"
LOCALHOST_URL = "http://localhost:"

# Error constants
BROWSER_CONNECTION_ERROR = "ECONNREFUSED"

# General settings
TIMEZONE = timezone(
    timedelta(hours=int(os.getenv("TIMEZONE_OFFSET", str(DEFAULT_TIMEZONE_OFFSET))))
)

# WSL2 detection and configuration
def is_wsl2() -> bool:
    """Check if running in WSL2 environment."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except (FileNotFoundError, OSError):
        return False

def get_wsl_host_ip() -> str:
    """Get Windows host IP address from WSL2 resolv.conf."""
    try:
        result = subprocess.run(
            ["awk", "/nameserver/ {print $2; exit}", "/etc/resolv.conf"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "127.0.0.1"

# Browser settings
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_LOAD_DELAY = int(os.getenv("BROWSER_LOAD_DELAY", "5000"))  # milliseconds
BROWSER_LOAD_TIMEOUT = int(os.getenv("BROWSER_LOAD_TIMEOUT", "15000"))  # milliseconds

# WSL2-specific browser configuration
WSL2_MODE = is_wsl2() and os.getenv("WSL2_MODE", "auto").lower() != "disabled"
WSL_HOST_IP = get_wsl_host_ip() if WSL2_MODE else "127.0.0.1"

def _select_browser_path(candidates: list[str]) -> str:
    """Select the first usable browser path or command from candidates.

    Prefers existing absolute paths; otherwise returns the first non-empty value
    (to allow command names in PATH). Falls back to "chromium" if none found.
    """
    for candidate in candidates:
        if not candidate:
            continue
        try:
            # If absolute path, ensure it exists
            if os.path.isabs(candidate):
                if os.path.exists(candidate):
                    return candidate
                # Skip non-existing absolute paths
                continue
            # For command names (non-absolute), return as-is
            return candidate
        except Exception:
            # Be resilient to any unexpected errors while probing
            continue
    return "chromium"

# Browser paths for different environments
if WSL2_MODE:
    # Windows Brave paths accessible from WSL2
    _default_browser_candidates = [
        os.getenv("BROWSER_PATH"),
        "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        "/mnt/c/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe",
        "/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
        "/c/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe",
        # As a last resort, allow command name in PATH
        "brave.exe",
    ]
else:
    # Linux browser paths
    _default_browser_candidates = [
        os.getenv("BROWSER_PATH"),
        "/usr/bin/brave-browser",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        # Allow command names in PATH
        "brave-browser",
        "google-chrome-stable",
        "google-chrome",
        "chromium",
        "chromium-browser",
    ]

BROWSER_PATH = _select_browser_path(_default_browser_candidates)

# Instagram settings
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/")
INSTAGRAM_POST_LOAD_DELAY = int(
    os.getenv("INSTAGRAM_POST_LOAD_DELAY", "3000")
)  # milliseconds
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(
    os.getenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "2")
)  # posts
INSTAGRAM_POST_LOAD_TIMEOUT = int(
    os.getenv("INSTAGRAM_POST_LOAD_TIMEOUT", "20000")
)  # milliseconds
INSTAGRAM_ACCOUNT_LOAD_DELAY = int(
    os.getenv("INSTAGRAM_ACCOUNT_LOAD_DELAY", "3000")
)  # milliseconds
INSTAGRAM_RETRY_DELAY = int(os.getenv("INSTAGRAM_RETRY_DELAY", "2000"))  # milliseconds

# Instagram accounts to track
INSTAGRAM_ACCOUNTS = [
    "agendagijon",
    "allandestars",
    "asociacionelviescu",
    "asturias_en_vena",
    "asturiasacoge",
    "asturiesculturaenrede",
    "aytocastrillon",
    "aytoviedo",
    "ayuntamientocabranes",
    "ayuntamientodegozon",
    "bandinalagarrapiella",
    "bibliotecasdegijonxixon",
    "biodevas",
    "centroniemeyer",
    "centros_sociales_oviedo",
    "chigreculturallatadezinc",
    "cia.proyectopiloto",
    "cinesfoncalada",
    "clubsemperludens",
    "conectaoviedo",
    "conocerasturias",
    "conseyu_cmx",
    "crjasturias",
    "cuentosdemaleta",
    "cultura.gijon",
    "cultura.grau",
    "culturacolunga",
    "culturallanes",
    "deportesayov",
    "exprime.gijon",
    "ferialibroxixon",
    "gijon",
    "gonggalaxyclub",
    "gteatrolospintores",
    "juventudgijon",
    "juventudoviedo",
    "kbunsgijon",
    "kuivi_almacenes",
    "laboralcinemateca",
    "laboralciudadcultura",
    "lacompaniadelalba",
    "lasalvaje.oviedo",
    "meidinerzclub",
    "mierescultura",
    "museosgijonxixon",
    "museudelpuebludasturies",
    "nortes.me",
    "oviedo_secrets",
    "oviedo.turismo",
    "paramo_bar",
    "patioh_laboral",
    "prestosofest",
    "prial_asociacion",
    "traslapuertatiteres",
    "trivilorioyeimpro",
    "youropia_asociacion",
]

# Output settings
BASE_DIR = os.getenv(
    "BASE_DIR", os.path.join(os.path.expanduser("~"), "Desktop", "IG Helper")
)
OUTPUT_DIR = os.getenv("OUTPUT_DIR", BASE_DIR)
LOG_DIR = os.getenv("LOG_DIR", BASE_DIR)
