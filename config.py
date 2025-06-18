"""Configuration settings for Instagram browser."""

from datetime import timedelta, timezone

from playwright.sync_api import ViewportSize

# Constants
TIMEZONE = timezone(timedelta(hours=1))  # CET/CEST
ERROR_EXECUTION_CONTEXT = "Execution context was destroyed"

# Browser settings
BROWSER_LOCALE = 'en-US'
BROWSER_TIMEZONE = 'Europe/Madrid'
BROWSER_VIEWPORT: ViewportSize = {'width': 1366, 'height': 768}
BROWSER_USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=VizDisplayCompositor',
    '--disable-web-security',
    '--disable-features=TranslateUI',
    '--disable-ipc-flooding-protection'
]

# Timeouts
TIMEOUT_PAGE_LOAD = 3000
TIMEOUT_POST_NAVIGATION = 8000
TIMEOUT_ACCOUNT_NAVIGATION = 12000
TIMEOUT_MAIN_PAGE = 30000

# HTML selectors
HTML_SELECTORS = {
    'login_indicators': [
        'nav[role="navigation"]',
        'a[href="/"]',
        'a[href="/explore/"]',
        'a[href="/reels/"]',
        'a[href="/direct/inbox/"]'
    ],
    'login_page_indicators': [
        'input[name="username"]',
        'input[name="password"]',
        'button[type="submit"]',
        'form[method="post"]'
    ],
    'caption': [
        'h1[dir="auto"]',
        'div[data-testid="post-caption"] span',
        'article h1',
        'span[dir="auto"]',
        'div[data-testid="post-caption"]',
        'article div[dir="auto"]',
        'article span',
        'h1',
        'p'
    ],
    'date': [
        'time[datetime]',
        'a time',
        'time',
        'span[title*="202"]',
        'a[title*="202"]',
        'time[title*="202"]'
    ],
    'post': [
        'a[href*="/p/"]',
        'article a[href*="/p/"]',
        'a[href*="/p/"]:not([href*="/p/explore/"])',
        'a[href*="/reel/"]',
        'a[href*="/tv/"]'
    ]
}

# Instagram settings
INSTAGRAM_MAX_POST_AGE = 3  # days
INSTAGRAM_MAX_POSTS_PER_ACCOUNT = 3  # posts
INSTAGRAM_DELAY_BETWEEN_ACCOUNTS = 3  # seconds
INSTAGRAM_URL = "https://www.instagram.com/"

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
    "ferialibroxixon",
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
    "bibliotecasdegijonxixon",
    "museudelpuebludasturies",
    "chigreculturallatadezinc",
]
