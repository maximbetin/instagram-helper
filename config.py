"""Configuration settings for Instagram browser."""

from playwright.sync_api import ViewportSize

# Browser settings
BROWSER_VIEWPORT: ViewportSize = {'width': 1366, 'height': 768}
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
LOCALE = 'en-US'
TIMEZONE = 'Europe/Madrid'

# Instagram URL
INSTAGRAM_URL = "https://www.instagram.com/"

# Instagram accounts to fetch posts from
INSTAGRAM_ACCOUNTS = [
    "aytoviedo"
]

# Post fetching settings
DAYS_TO_LOOK_BACK = 7
POSTS_PER_ACCOUNT = 5
DELAY_BETWEEN_ACCOUNTS = 3  # seconds

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
