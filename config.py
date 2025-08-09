"""Configuration settings."""

import os
import platform
import subprocess
from datetime import timedelta, timezone


def find_brave_browser_path() -> str:
    """Find the Brave browser executable path, with special handling for WSL2."""
    # Check if BROWSER_PATH is set via environment variable
    env_path = os.getenv("BROWSER_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    system = platform.system().lower()
    paths_to_check = []
    default_path = "brave-browser"

    # Determine paths to check based on system
    if system == "linux" and "microsoft" in platform.release().lower():
        # WSL2 detected
        paths_to_check = [
            "/usr/bin/brave-browser",
            "/usr/bin/brave-browser-stable",
            "/snap/bin/brave-browser",
            "/opt/brave.com/brave/brave-browser",
            os.path.expanduser("~/.local/bin/brave-browser"),
            "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
            "/mnt/c/Program Files (x86)/BraveSoftware/Brave-Browser/Application/brave.exe",
        ]
        default_path = "/usr/bin/brave-browser"
    elif system == "linux":
        # Regular Linux
        paths_to_check = [
            "/usr/bin/brave-browser",
            "/usr/bin/brave-browser-stable",
            "/snap/bin/brave-browser",
            "/opt/brave.com/brave/brave-browser",
            os.path.expanduser("~/.local/bin/brave-browser"),
        ]
        default_path = "/usr/bin/brave-browser"
    elif system == "windows":
        # Windows
        paths_to_check = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        ]
        default_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
    elif system == "darwin":
        # macOS
        paths_to_check = [
            "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "/usr/bin/brave-browser",
        ]
        default_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"

    # Check all paths
    for path in paths_to_check:
        if os.path.exists(path):
            return path

    # Try 'which' command for Unix-like systems
    if system in ["linux", "darwin"]:
        try:
            result = subprocess.run(
                ["which", "brave-browser"], check=False, capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                brave_path = result.stdout.strip()
                if os.path.exists(brave_path):
                    return brave_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return default_path


# General settings
TIMEZONE = timezone(timedelta(hours=int(os.getenv("TIMEZONE_OFFSET", "2"))))

# Browser settings
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_LOAD_DELAY = int(os.getenv("BROWSER_LOAD_DELAY", "5000"))  # milliseconds
BROWSER_LOAD_TIMEOUT = int(os.getenv("BROWSER_LOAD_TIMEOUT", "15000"))  # milliseconds
BROWSER_PATH = find_brave_browser_path()

# Instagram settings
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/")
INSTAGRAM_MAX_POST_AGE = int(os.getenv("INSTAGRAM_MAX_POST_AGE", "2"))  # days
INSTAGRAM_POST_LOAD_DELAY = int(os.getenv("INSTAGRAM_POST_LOAD_DELAY", "3000"))  # milliseconds
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(os.getenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "2"))  # posts
INSTAGRAM_POST_LOAD_TIMEOUT = int(os.getenv("INSTAGRAM_POST_LOAD_TIMEOUT", "20000"))  # milliseconds
INSTAGRAM_ACCOUNT_LOAD_DELAY = int(
    os.getenv("INSTAGRAM_ACCOUNT_LOAD_DELAY", "3000")
)  # milliseconds

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
    "asociacion_ssagar",
]

# Output settings
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "IG Helper")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", BASE_DIR)
LOG_DIR = os.getenv("LOG_DIR", BASE_DIR)
