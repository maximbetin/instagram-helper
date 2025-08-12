"""Configuration settings for Instagram Helper."""

import os
from datetime import timedelta, timezone

from dotenv import load_dotenv

load_dotenv()


def is_running_in_wsl() -> bool:
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


# Time constants
SECONDS_IN_MS = 1000
DEFAULT_TIMEZONE_OFFSET = 2
TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", str(DEFAULT_TIMEZONE_OFFSET)))
TIMEZONE = timezone(timedelta(hours=TIMEZONE_OFFSET))

# Protocol constants
FILE_PROTOCOL = os.getenv("FILE_PROTOCOL", "file://")
LOCALHOST_URL = os.getenv("LOCALHOST_URL", "http://localhost")

# Browser settings
BROWSER_PATH = os.getenv("BROWSER_PATH")
BROWSER_REMOTE_HOST = os.getenv("BROWSER_REMOTE_HOST")
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_LOAD_DELAY = int(os.getenv("BROWSER_LOAD_DELAY", "5000"))
BROWSER_CONNECT_SCHEME = os.getenv("BROWSER_CONNECT_SCHEME", "http")
_attach_only_env = os.getenv("BROWSER_ATTACH_ONLY")
BROWSER_ATTACH_ONLY = (
    _attach_only_env.lower() in {"1", "true", "yes", "on"}
    if _attach_only_env
    else is_running_in_wsl()
)

# Output settings
BASE_DIR = os.getenv("BASE_DIR", "/mnt/c/Users/Maxim/Desktop/ig_helper")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", BASE_DIR)
LOG_DIR = os.getenv("LOG_DIR", BASE_DIR)
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "templates/template.html")

# Instagram settings
INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/")
INSTAGRAM_RETRY_DELAY = int(os.getenv("INSTAGRAM_RETRY_DELAY", "2000"))
INSTAGRAM_POST_LOAD_DELAY = int(os.getenv("INSTAGRAM_POST_LOAD_DELAY", "3000"))
INSTAGRAM_POST_LOAD_TIMEOUT = int(os.getenv("INSTAGRAM_POST_LOAD_TIMEOUT", "20000"))
INSTAGRAM_ACCOUNT_LOAD_DELAY = int(os.getenv("INSTAGRAM_ACCOUNT_LOAD_DELAY", "3000"))
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(os.getenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "2"))

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
