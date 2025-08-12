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
        BROWSER_ATTACH_ONLY (bool): If true, attach to an existing browser.
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
    BROWSER_ATTACH_ONLY: bool = False
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
        ]
    )
    INSTAGRAM_URL: str = "https://www.instagram.com/"
    INSTAGRAM_POST_LOAD_TIMEOUT: int = 10000
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT: int = 5
    FILE_PROTOCOL: str = "file:///"

    def __post_init__(self) -> None:
        """Performs validation after the object has been initialized.

        This method checks for required environment variables and ensures that
        critical paths are correctly configured.

        Raises:
            ValueError: If a required environment variable is missing or invalid.
        """
        # Load string-based paths from environment variables
        browser_path_str = os.getenv("BROWSER_PATH")
        user_data_dir_str = os.getenv("BROWSER_USER_DATA_DIR")

        # Dynamically override defaults from environment variables
        # This is necessary because frozen dataclasses don't allow direct mutation.
        object.__setattr__(
            self, "BROWSER_PATH", Path(browser_path_str) if browser_path_str else None
        )
        object.__setattr__(
            self,
            "BROWSER_USER_DATA_DIR",
            Path(user_data_dir_str) if user_data_dir_str else None,
        )
        object.__setattr__(
            self,
            "BROWSER_PROFILE_DIR",
            os.getenv("BROWSER_PROFILE_DIR", self.BROWSER_PROFILE_DIR),
        )
        object.__setattr__(
            self,
            "BROWSER_DEBUG_PORT",
            int(os.getenv("BROWSER_DEBUG_PORT", str(self.BROWSER_DEBUG_PORT))),
        )
        object.__setattr__(
            self,
            "BROWSER_ATTACH_ONLY",
            os.getenv("BROWSER_ATTACH_ONLY", "false").lower() == "true",
        )

        # We need to re-set the output and log directories here because their
        # defaults depend on environment variables that should be loaded first.
        object.__setattr__(
            self, "OUTPUT_DIR", Path(os.getenv("OUTPUT_DIR", self.BASE_DIR))
        )
        object.__setattr__(self, "LOG_DIR", Path(os.getenv("LOG_DIR", self.BASE_DIR)))

        # Validate that required paths are set
        if self.BROWSER_PATH is None:
            raise ValueError("BROWSER_PATH environment variable is not set.")
        if self.BROWSER_USER_DATA_DIR is None:
            raise ValueError("BROWSER_USER_DATA_DIR environment variable is not set.")


# Create a single, immutable instance of the settings
settings = Settings()
