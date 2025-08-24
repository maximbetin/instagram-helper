"""Configuration settings for Instagram Helper."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import timedelta, timezone
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

load_dotenv()


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
    INSTAGRAM_ACCOUNTS: list[str] = field(
        default_factory=lambda: [
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
    )
    INSTAGRAM_URL: str = "https://www.instagram.com/"
    INSTAGRAM_POST_LOAD_TIMEOUT: int = 10000
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT: int = 5

    def __post_init__(self) -> None:
        """Performs validation after the object has been initialized.

        This method checks for required environment variables and ensures that
        critical paths are correctly configured.

        Raises:
            ValueError: If a required environment variable is missing or invalid.
        """

        def _set_from_env(
            attr_name: str, env_var: str, converter: type = str, required: bool = False
        ) -> None:
            """Helper to set attribute from environment variable."""
            value = os.getenv(env_var)
            if value is not None:
                if converter is not str:
                    try:
                        value = converter(value)
                    except (ValueError, TypeError) as err:
                        if required:
                            raise ValueError(
                                f"Invalid value for {env_var}: {value}"
                            ) from err
                        return
                object.__setattr__(self, attr_name, value)
            elif required:
                raise ValueError(f"{env_var} environment variable is not set.")

        # Load browser-related settings
        _set_from_env("BROWSER_PATH", "BROWSER_PATH", Path, required=True)
        _set_from_env(
            "BROWSER_USER_DATA_DIR", "BROWSER_USER_DATA_DIR", Path, required=True
        )
        _set_from_env("BROWSER_PROFILE_DIR", "BROWSER_PROFILE_DIR")
        _set_from_env("BROWSER_DEBUG_PORT", "BROWSER_DEBUG_PORT", int)
        _set_from_env("BROWSER_START_URL", "BROWSER_START_URL")
        _set_from_env("BROWSER_LOAD_DELAY", "BROWSER_LOAD_DELAY", int)
        _set_from_env("BROWSER_CONNECT_SCHEME", "BROWSER_CONNECT_SCHEME")
        _set_from_env("BROWSER_REMOTE_HOST", "BROWSER_REMOTE_HOST")

        # Load path and template settings
        _set_from_env("OUTPUT_DIR", "OUTPUT_DIR", Path)
        _set_from_env("LOG_DIR", "LOG_DIR", Path)
        _set_from_env("TEMPLATE_PATH", "TEMPLATE_PATH")

        # Load Instagram-related settings
        _set_from_env("INSTAGRAM_URL", "INSTAGRAM_URL")
        _set_from_env(
            "INSTAGRAM_MAX_POSTS_PER_ACCOUNT", "INSTAGRAM_MAX_POSTS_PER_ACCOUNT", int
        )
        _set_from_env("INSTAGRAM_POST_LOAD_TIMEOUT", "INSTAGRAM_POST_LOAD_TIMEOUT", int)

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
