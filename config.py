from typing import List

# Instagram accounts to track
INSTAGRAM_ACCOUNTS: List[str] = [
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
    "chigreculturallatadezinc",
]

# How far back to look for posts (in days)
DAYS_TO_LOOK_BACK: int = 3

# Fetcher configuration
MAX_RETRIES: int = 1
RETRY_DELAY: int = 5  # seconds
POSTS_PER_ACCOUNT: int = 10
ACCOUNT_DELAY: int = 5  # seconds
