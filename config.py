"""Configuration settings for Instagram browser."""

from datetime import timedelta, timezone

from playwright.sync_api import ViewportSize

# Constants
INSTAGRAM_URL = "https://www.instagram.com/"
EXECUTION_CONTEXT_ERROR = "Execution context was destroyed"
MADRID_TZ = timezone(timedelta(hours=1))  # CET/CEST

# Browser settings
BROWSER_VIEWPORT: ViewportSize = {'width': 1366, 'height': 768}
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)
LOCALE = 'en-US'
TIMEZONE = 'Europe/Madrid'
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',
    '--disable-features=VizDisplayCompositor',
    '--disable-web-security',
    '--disable-features=TranslateUI',
    '--disable-ipc-flooding-protection'
]

# HTML selectors
# Element selectors
SELECTORS = {
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

# Post fetching settings
DELAY_BETWEEN_ACCOUNTS = 3  # seconds
DAYS_BACK_TO_FETCH = 3  # Only fetch posts from this many days ago
MAX_POSTS_TO_CHECK = 3  # Maximum posts to check per account before giving up

# Timeouts (milliseconds)
TIMEOUT_PAGE_LOAD = 5000
TIMEOUT_POST_NAVIGATION = 8000
TIMEOUT_ACCOUNT_NAVIGATION = 12000
TIMEOUT_MAIN_PAGE = 30000

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
    "gonggalaxyclub",
    "juventudoviedo",
    "cinesfoncalada",
    "oviedo.turismo",
    "oviedo_secrets",
    "patioh_laboral",
    "centroniemeyer",
    "conocerasturias",
    "kuivi_almacenes",
    "asturias_en_vena",
    "museosgijonxixon",
    "lasalvaje.oviedo",
    "laboralcinemateca",
    "youropia_asociacion",
    "laboralciudadcultura",
    "asturiesculturaenrede",
    "chigreculturallatadezinc"
]
