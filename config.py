"""Configuration settings for Instagram Helper."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timedelta, timezone
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

load_dotenv()


def _load_instagram_accounts() -> list[str]:
    """Load Instagram accounts from a separate file or use defaults."""
    accounts_file = Path(__file__).parent / "instagram_accounts.txt"

    if accounts_file.exists():
        try:
            with open(accounts_file, encoding="utf-8") as f:
                accounts = [
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                ]
            return accounts
        except Exception:
            pass

    # Fallback to default accounts
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
    """Manages all application settings, loading them from environment variables.

    This class centralizes configuration management, providing default values
    and validation for required settings. Using a frozen dataclass ensures that
    settings are immutable at runtime, preventing unintended modifications.

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
        default_factory=lambda: Path(os.getenv("OUTPUT_DIR", Settings.BASE_DIR))
    )
    LOG_DIR: Path = field(
        default_factory=lambda: Path(os.getenv("LOG_DIR", Settings.BASE_DIR))
    )
    TEMPLATE_PATH: str = "templates/template.html"

    # --- Timezone Configuration ---
    TIMEZONE: timezone = field(
        default_factory=lambda: timezone(
            timedelta(hours=int(os.getenv("TIMEZONE_OFFSET", "2")))
        )
    )

    # --- Browser Configuration ---
    BROWSER_PATH: Path | None = field(default=None)
    BROWSER_USER_DATA_DIR: Path | None = field(default=None)
    BROWSER_PROFILE_DIR: str = "Default"
    BROWSER_DEBUG_PORT: int = 9222
    BROWSER_START_URL: str = "https://www.instagram.com/"
    BROWSER_LOAD_DELAY: int = 5000  # In milliseconds
    BROWSER_CONNECT_SCHEME: str = "http"
    BROWSER_REMOTE_HOST: str = "localhost"

    # --- Instagram Scraper Configuration ---
    INSTAGRAM_ACCOUNTS: list[str] = field(default_factory=_load_instagram_accounts)
    INSTAGRAM_URL: str = "https://www.instagram.com/"
    INSTAGRAM_POST_LOAD_TIMEOUT: int = 10000
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT: int = 5

    def __post_init__(self) -> None:
        """Performs validation after the object has been initialized."""
        # Load browser-related settings
        self._load_browser_settings()

        # Load path and template settings
        self._load_path_settings()

        # Load Instagram-related settings
        self._load_instagram_settings()

    def _load_browser_settings(self) -> None:
        """Load browser-related settings from environment."""
        if browser_path := os.getenv("BROWSER_PATH"):
            object.__setattr__(self, "BROWSER_PATH", Path(browser_path))
        else:
            raise ValueError("BROWSER_PATH environment variable is required")

        if browser_user_data := os.getenv("BROWSER_USER_DATA_DIR"):
            object.__setattr__(self, "BROWSER_USER_DATA_DIR", Path(browser_user_data))
        else:
            raise ValueError("BROWSER_USER_DATA_DIR environment variable is required")

        if profile_dir := os.getenv("BROWSER_PROFILE_DIR"):
            object.__setattr__(self, "BROWSER_PROFILE_DIR", profile_dir)

        if debug_port := os.getenv("BROWSER_DEBUG_PORT"):
            try:
                object.__setattr__(self, "BROWSER_DEBUG_PORT", int(debug_port))
            except ValueError:
                pass

        if start_url := os.getenv("BROWSER_START_URL"):
            object.__setattr__(self, "BROWSER_START_URL", start_url)

        if load_delay := os.getenv("BROWSER_LOAD_DELAY"):
            try:
                object.__setattr__(self, "BROWSER_LOAD_DELAY", int(load_delay))
            except ValueError:
                pass

        if connect_scheme := os.getenv("BROWSER_CONNECT_SCHEME"):
            object.__setattr__(self, "BROWSER_CONNECT_SCHEME", connect_scheme)

        if remote_host := os.getenv("BROWSER_REMOTE_HOST"):
            object.__setattr__(self, "BROWSER_REMOTE_HOST", remote_host)

    def _load_path_settings(self) -> None:
        """Load path and template settings from environment."""
        if output_dir := os.getenv("OUTPUT_DIR"):
            object.__setattr__(self, "OUTPUT_DIR", Path(output_dir))

        if log_dir := os.getenv("LOG_DIR"):
            object.__setattr__(self, "LOG_DIR", Path(log_dir))

        if template_path := os.getenv("TEMPLATE_PATH"):
            object.__setattr__(self, "TEMPLATE_PATH", template_path)

    def _load_instagram_settings(self) -> None:
        """Load Instagram-related settings from environment."""
        if instagram_url := os.getenv("INSTAGRAM_URL"):
            object.__setattr__(self, "INSTAGRAM_URL", instagram_url)

        if max_posts := os.getenv("INSTAGRAM_MAX_POSTS_PER_ACCOUNT"):
            try:
                object.__setattr__(
                    self, "INSTAGRAM_MAX_POSTS_PER_ACCOUNT", int(max_posts)
                )
            except ValueError:
                pass

        if timeout := os.getenv("INSTAGRAM_POST_LOAD_TIMEOUT"):
            try:
                object.__setattr__(self, "INSTAGRAM_POST_LOAD_TIMEOUT", int(timeout))
            except ValueError:
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
