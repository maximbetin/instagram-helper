"""Configuration settings for Instagram browser."""

from playwright.sync_api import ViewportSize

# Browser settings
BROWSER_VIEWPORT: ViewportSize = {'width': 1366, 'height': 768}
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
LOCALE = 'en-US'
TIMEZONE = 'Europe/Madrid'

# Instagram settings
INSTAGRAM_URL = "https://www.instagram.com/"

# Post fetching settings
DAYS_BACK_TO_FETCH = 7  # Only fetch posts from this many days ago
MAX_POSTS_TO_CHECK = 5  # Maximum posts to check per account before giving up
DELAY_BETWEEN_ACCOUNTS = 3  # seconds

# Instagram accounts to track
INSTAGRAM_ACCOUNTS = [
    "biodevas",
    "ausevagm",
    "aytoviedo",
    "nortes.me",
    "paramo_bar",
    "crjasturias",
    "agendagijon",
    "sala_niagara",
    "rocketoviedo",
    "prestosofest",
    "meidinerzclub",
    "exprime.gijon",
    "mierescultura",
    "cultura.gijon",
    "conectaoviedo",
    "culturallanes",
    "gonggalaxyclub",
    "juventudoviedo",
    "cinesfoncalada",
    "oviedo.turismo",
    "oviedo_secrets",
    "patioh_laboral",
    "centroniemeyer",
    "culturacolunga",
    "conocerasturias",
    "kuivi_almacenes",
    "cuentosdemaleta",
    "asturias_en_vena",
    "museosgijonxixon",
    "lasalvaje.oviedo",
    "laboralcinemateca",
    "lacompaniadelalba",
    "gteatrolospintores",
    "cia.proyectopiloto",
    "youropia_asociacion",
    "traslapuertatiteres",
    "laboralciudadcultura",
    "ayuntamientocabranes",
    "bandinalagarrapiella",
    "asturiesculturaenrede",
    "chigreculturallatadezinc",
]

# Browser launch arguments
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=VizDisplayCompositor',
    '--disable-web-security',
    '--disable-features=TranslateUI',
    '--disable-ipc-flooding-protection'
]
