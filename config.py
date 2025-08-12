"""Configuration settings for Instagram Helper."""

import os
from datetime import timedelta, timezone

from dotenv import load_dotenv

load_dotenv()


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
BROWSER_REMOTE_HOST = os.getenv("BROWSER_REMOTE_HOST", "localhost")
BROWSER_DEBUG_PORT = int(os.getenv("BROWSER_DEBUG_PORT", "9222"))
BROWSER_LOAD_DELAY = int(os.getenv("BROWSER_LOAD_DELAY", "5000"))
BROWSER_CONNECT_SCHEME = os.getenv("BROWSER_CONNECT_SCHEME", "http")
BROWSER_ATTACH_ONLY = os.getenv("BROWSER_ATTACH_ONLY", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
BROWSER_USER_DATA_DIR = os.getenv(
    "BROWSER_USER_DATA_DIR",
    r"C:\Users\Maxim\AppData\Local\BraveSoftware\Brave-Browser\User Data",
)
BROWSER_PROFILE_DIR = os.getenv("BROWSER_PROFILE_DIR", "Default")
BROWSER_START_URL = os.getenv(
    "BROWSER_START_URL", os.getenv("INSTAGRAM_URL", "https://www.instagram.com/")
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
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(os.getenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "3"))

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
