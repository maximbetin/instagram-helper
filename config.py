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

# Browser settings - Playwright handles all browser management automatically
# These settings are kept for backward compatibility but are no longer actively used
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_PATH = os.getenv("BROWSER_PATH", "chromium")

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
