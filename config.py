"""Configuration settings."""

import os
from datetime import timedelta, timezone

# General settings
TIMEZONE = timezone(timedelta(hours=int(os.getenv('TIMEZONE_OFFSET', '2'))))

# Browser settings
BROWSER_DEBUG_PORT = int(os.getenv('BROWSER_DEBUG_PORT', '9222'))
BROWSER_LOAD_DELAY = int(os.getenv('BROWSER_LOAD_DELAY', '5'))  # seconds
BROWSER_LOAD_TIMEOUT = int(os.getenv('BROWSER_LOAD_TIMEOUT', '10000'))  # milliseconds
BROWSER_PATH = os.getenv('BROWSER_PATH', os.path.expandvars(r"%PROGRAMFILES%\BraveSoftware\Brave-Browser\Application\brave.exe"))

# Instagram settings
INSTAGRAM_URL = os.getenv('INSTAGRAM_URL', "https://www.instagram.com/")
INSTAGRAM_MAX_POST_AGE = int(os.getenv('INSTAGRAM_MAX_POST_AGE', '3'))  # days
INSTAGRAM_POST_LOAD_DELAY = int(os.getenv('INSTAGRAM_POST_LOAD_DELAY', '3'))  # seconds
INSTAGRAM_ACCOUNT_LOAD_DELAY = int(os.getenv('INSTAGRAM_ACCOUNT_LOAD_DELAY', '3'))  # seconds
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = int(os.getenv('INSTAGRAM_MAX_POSTS_PER_ACCOUNT', '3'))  # posts

# Instagram accounts to track
INSTAGRAM_ACCOUNTS = [
    "gijon",
    "biodevas",
    "ausevagm",
    "aytoviedo",
    "nortes.me",
    "paramo_bar",
    "kbunsgijon",
    "crjasturias",
    "agendagijon",
    "conseyu_cmx",
    "sala_niagara",
    "rocketoviedo",
    "prestosofest",
    "deportesayov",
    "cultura.grau",
    "allandestars",
    "meidinerzclub",
    "exprime.gijon",
    "mierescultura",
    "cultura.gijon",
    "conectaoviedo",
    "juventudgijon",
    "culturallanes",
    "gonggalaxyclub",
    "juventudoviedo",
    "cinesfoncalada",
    "oviedo.turismo",
    "oviedo_secrets",
    "patioh_laboral",
    "centroniemeyer",
    "culturacolunga",
    "aytocastrillon",
    "ferialibroxixon",
    "conocerasturias",
    "kuivi_almacenes",
    "cuentosdemaleta",
    "asturias_en_vena",
    "museosgijonxixon",
    "lasalvaje.oviedo",
    "trivilorioyeimpro",
    "laboralcinemateca",
    "lacompaniadelalba",
    "gteatrolospintores",
    "cia.proyectopiloto",
    "youropia_asociacion",
    "traslapuertatiteres",
    "ayuntamientodegozon",
    "laboralciudadcultura",
    "ayuntamientocabranes",
    "bandinalagarrapiella",
    "asturiesculturaenrede",
    "bibliotecasdegijonxixon",
    "museudelpuebludasturies",
    "chigreculturallatadezinc",
]

# Output settings
BASE_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'IG Updates')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', BASE_DIR)
LOG_DIR = os.getenv('LOG_DIR', BASE_DIR)
