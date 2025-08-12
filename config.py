"""Configuration settings for Instagram Helper."""

import os
from datetime import timedelta, timezone

# Time constants
SECONDS_IN_MS = 1000
DEFAULT_TIMEZONE_OFFSET = 2

# General settings
TIMEZONE = timezone(
    timedelta(hours=int(os.getenv("TIMEZONE_OFFSET", str(DEFAULT_TIMEZONE_OFFSET))))
)

# Browser settings
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_LOAD_DELAY = int(os.getenv("BROWSER_LOAD_DELAY", "5000"))  # milliseconds
BROWSER_LOAD_TIMEOUT = int(os.getenv("BROWSER_LOAD_TIMEOUT", "15000"))  # milliseconds


def _is_running_in_wsl() -> bool:
    """Detect if the process is running inside WSL/WSL2.

    Checks common kernel strings that include 'Microsoft' in WSL.
    """
    try:
        for probe in ("/proc/sys/kernel/osrelease", "/proc/version"):
            if os.path.exists(probe):
                with open(probe, encoding="utf-8", errors="ignore") as f:
                    content = f.read().lower()
                    if "microsoft" in content or "wsl" in content:
                        return True
    except Exception:
        pass
    return False


# Remote/WSL2 bridging settings
# If set, connect to this host instead of localhost (e.g., Windows host IP from /etc/resolv.conf)
BROWSER_REMOTE_HOST = os.getenv("BROWSER_REMOTE_HOST")
# When true, do not spawn a local browser process; only attach to an existing one via CDP
# Default behavior: auto-enable attach-only in WSL environments to reuse Windows browser sessions
_attach_only_env = os.getenv("BROWSER_ATTACH_ONLY")
if _attach_only_env is not None:
    BROWSER_ATTACH_ONLY = _attach_only_env.lower() in {"1", "true", "yes", "on"}
else:
    BROWSER_ATTACH_ONLY = _is_running_in_wsl()

# Scheme for CDP connection (http or ws). http://<host>:<port> works for Chromium-based browsers
BROWSER_CONNECT_SCHEME = os.getenv("BROWSER_CONNECT_SCHEME", "http")

# Prefer an explicit override, otherwise try common browser locations; fall back to a generic 'chromium' in PATH
_default_browser_candidates = [
    os.getenv("BROWSER_PATH"),
    "/usr/bin/brave-browser",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
]
BROWSER_PATH = next((p for p in _default_browser_candidates if p), "chromium")

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
BASE_DIR = os.getenv("BASE_DIR", "/mnt/c/Users/Maxim/Desktop/ig_helper")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", BASE_DIR)
LOG_DIR = os.getenv("LOG_DIR", BASE_DIR)
