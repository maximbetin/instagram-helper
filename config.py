"""Configuration settings for Instagram Helper."""

import os
from datetime import timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Path Configuration ---
# Use pathlib for robust and platform-independent path management.
# BASE_DIR is the project's root directory.
BASE_DIR = Path(__file__).resolve().parent

# Default output, log, and template directories.
# These can be overridden by environment variables.
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR))
LOG_DIR = Path(os.getenv("LOG_DIR", BASE_DIR))
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "templates/template.html")


# --- Timezone Configuration ---
# Set the local timezone for date calculations.
# Defaults to UTC+2, but can be configured via TIMEZONE_OFFSET.
TIMEZONE_OFFSET = int(os.getenv("TIMEZONE_OFFSET", "2"))
TIMEZONE = timezone(timedelta(hours=TIMEZONE_OFFSET))


# --- Browser Configuration ---
# Settings for launching and connecting to the browser.
# BROWSER_PATH should be the full path to the browser executable.
# Set BROWSER_ATTACH_ONLY to "true" to prevent launching a new browser.
BROWSER_PATH = os.getenv("BROWSER_PATH")
BROWSER_USER_DATA_DIR = os.getenv("BROWSER_USER_DATA_DIR")
BROWSER_PROFILE_DIR = os.getenv("BROWSER_PROFILE_DIR", "Default")
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_START_URL = "https://www.instagram.com/"
BROWSER_LOAD_DELAY = int(os.getenv("BROWSER_LOAD_DELAY", "5000"))  # In milliseconds
BROWSER_ATTACH_ONLY = os.getenv("BROWSER_ATTACH_ONLY", "false").lower() == "true"
BROWSER_CONNECT_SCHEME = os.getenv("BROWSER_CONNECT_SCHEME", "http")
BROWSER_REMOTE_HOST = os.getenv("BROWSER_REMOTE_HOST", "localhost")


# --- Instagram Scraper Configuration ---
# Accounts to scrape and settings for controlling scraping behavior.
# Delays are in milliseconds.
INSTAGRAM_ACCOUNTS: list[str] = [
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
INSTAGRAM_URL = "https://www.instagram.com/"
INSTAGRAM_POST_LOAD_TIMEOUT = int(os.getenv("INSTAGRAM_POST_LOAD_TIMEOUT", "10000"))
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(
    os.getenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "5")
)
FILE_PROTOCOL = "file:///"
