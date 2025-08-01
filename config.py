"""Configuration settings."""

import os
from datetime import timedelta, timezone

# General settings
TIMEZONE = timezone(timedelta(hours=int(os.getenv('TIMEZONE_OFFSET', '2'))))

# Browser settings
BROWSER_DEBUG_PORT = int(os.getenv('BROWSER_DEBUG_PORT', '9222'))
BROWSER_LOAD_DELAY = int(os.getenv('BROWSER_LOAD_DELAY', '5000'))  # milliseconds
BROWSER_LOAD_TIMEOUT = int(os.getenv('BROWSER_LOAD_TIMEOUT', '15000'))  # milliseconds
BROWSER_PATH = os.getenv('BROWSER_PATH', os.path.expandvars('C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'))

# Instagram settings
INSTAGRAM_URL = os.getenv('INSTAGRAM_URL', "https://www.instagram.com/")
INSTAGRAM_MAX_POST_AGE = int(os.getenv('INSTAGRAM_MAX_POST_AGE', '2'))  # days
INSTAGRAM_POST_LOAD_DELAY = int(os.getenv('INSTAGRAM_POST_LOAD_DELAY', '3000'))  # milliseconds
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(os.getenv('INSTAGRAM_MAX_POSTS_PER_ACCOUNT', '2'))  # posts
INSTAGRAM_POST_LOAD_TIMEOUT = int(os.getenv('INSTAGRAM_POST_LOAD_TIMEOUT', '20000'))  # milliseconds
INSTAGRAM_ACCOUNT_LOAD_DELAY = int(os.getenv('INSTAGRAM_ACCOUNT_LOAD_DELAY', '3000'))  # milliseconds

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
BASE_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'IG Helper')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', BASE_DIR)
LOG_DIR = os.getenv('LOG_DIR', BASE_DIR)
