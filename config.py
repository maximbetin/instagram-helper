"""Configuration settings for Instagram Helper."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta, timezone
from pathlib import Path
from typing import ClassVar


def _load_instagram_accounts() -> list[str]:
    """Default Instagram accounts to scrape."""
    return [
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


@dataclass(frozen=True, kw_only=True)
class Settings:
    """Manages all application settings with hardcoded values.

    This class centralizes configuration management with predefined values
    for all settings. Using a frozen dataclass ensures that settings are
    immutable at runtime, preventing unintended modifications.

    DESIGN DECISIONS & IMPLEMENTATION QUIRKS:

    1. FROZEN DATACLASS: The class is frozen to prevent runtime modification,
       ensuring configuration consistency throughout the application lifecycle.

    2. HARDCODED VALUES: All settings are predefined and don't require
       environment variables or external configuration files.

    3. SIMPLIFIED INITIALIZATION: No complex validation or environment
       variable loading, making the configuration reliable and predictable.

    4. PYINSTALLER COMPATIBLE: No import-time dependencies that could
       cause build issues with PyInstaller.

    Attributes:
        BASE_DIR (ClassVar[Path]): The project's root directory.
        BROWSER_PATH (Path): The absolute path to the browser executable.
        BROWSER_USER_DATA_DIR (Path): Path to the browser's user data directory.
        BROWSER_PROFILE_DIR (str): The profile directory to use.
        BROWSER_DEBUG_PORT (int): The remote debugging port.
        BROWSER_START_URL (str): The URL to start the browser at.
        BROWSER_LOAD_DELAY (int): The delay in milliseconds between page loads.
        BROWSER_CONNECT_SCHEME (str): The scheme to use for remote debugging.
        BROWSER_REMOTE_HOST (str): The host for remote debugging.
        INSTAGRAM_ACCOUNTS (list[str]): Default list of Instagram accounts.
    """

    # --- Class-level Constants ---
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent

    # --- Path Configuration ---
    OUTPUT_DIR: Path = field(
        default_factory=lambda: Path("/mnt/c/Users/Maxim/Desktop/ig_helper")
    )
    LOG_DIR: Path = field(
        default_factory=lambda: Path("/mnt/c/Users/Maxim/Desktop/ig_helper")
    )
    TEMPLATE_PATH: str = "templates/template.html"

    # --- Timezone Configuration ---
    TIMEZONE: timezone = field(default_factory=lambda: timezone(timedelta(hours=2)))

    # --- Browser Configuration ---
    BROWSER_PATH: Path = field(
        default_factory=lambda: Path(
            "/mnt/c/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"
        )
    )
    BROWSER_USER_DATA_DIR: Path = field(
        default_factory=lambda: Path(
            "C:\\Users\\Maxim\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data"
        )
    )
    BROWSER_PROFILE_DIR: str = "Default"
    BROWSER_DEBUG_PORT: int = 9222
    BROWSER_START_URL: str = "https://www.instagram.com/"
    BROWSER_LOAD_DELAY: int = 5000  # In milliseconds
    BROWSER_CONNECT_SCHEME: str = "http"
    BROWSER_REMOTE_HOST: str = "localhost"

    # --- Instagram Scraper Configuration ---
    INSTAGRAM_ACCOUNTS: list[str] = field(default_factory=_load_instagram_accounts)
    INSTAGRAM_URL: str = "https://www.instagram.com/"
    INSTAGRAM_POST_LOAD_TIMEOUT: int = 20000
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT: int = 3

    def __post_init__(self) -> None:
        """Performs validation after the object has been initialized."""
        # All settings are now hardcoded - no environment variable loading needed
        pass

    def update_instagram_settings(self, max_posts: int, timeout: int) -> None:
        """Update Instagram settings dynamically.

        Args:
            max_posts: New maximum posts per account value
            timeout: New post load timeout value in milliseconds
        """
        object.__setattr__(self, "INSTAGRAM_MAX_POSTS_PER_ACCOUNT", max_posts)
        object.__setattr__(self, "INSTAGRAM_POST_LOAD_TIMEOUT", timeout)


# Create a single, immutable instance of the settings
settings = Settings()
