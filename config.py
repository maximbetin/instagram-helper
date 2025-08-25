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
    """Manages all application settings, loading them from environment variables.

    This class centralizes configuration management, providing default values
    and validation for required settings. Using a frozen dataclass ensures that
    settings are immutable at runtime, preventing unintended modifications.

    DESIGN DECISIONS & IMPLEMENTATION QUIRKS:

    1. FROZEN DATACLASS: The class is frozen to prevent runtime modification,
       ensuring configuration consistency throughout the application lifecycle.

    2. POST_INIT VALIDATION: Complex validation logic is deferred until after
       all fields are initialized, allowing for cross-field validation and
       environment-specific fallbacks.

    3. TESTING ENVIRONMENT DETECTION: The configuration automatically detects
       testing environments (CI=true or PYTEST_CURRENT_TEST) and provides
       dummy values for required browser paths. This prevents import-time
       errors when running tests without a full browser setup.

    4. OBJECT.__SETATTR__ USAGE: Since the dataclass is frozen, we use
       object.__setattr__ to update values during initialization. This maintains
       type safety while allowing necessary post-initialization modifications.

    5. GRACEFUL DEGRADATION: Non-critical settings use fallback values when
       environment variables are missing or invalid, ensuring the application
       can start even with incomplete configuration.

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
    OUTPUT_DIR: Path = field(default_factory=lambda: Settings.BASE_DIR)
    LOG_DIR: Path = field(default_factory=lambda: Settings.BASE_DIR)
    TEMPLATE_PATH: str = "templates/template.html"

    # --- Timezone Configuration ---
    TIMEZONE: timezone = field(default_factory=lambda: timezone(timedelta(hours=2)))

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

    # --- Property getters for lazy loading ---
    @property
    def BROWSER_PATH_LOADED(self) -> Path:
        """Get BROWSER_PATH, loading from environment if needed."""
        self._ensure_settings_loaded()
        if self.BROWSER_PATH is None:
            raise ValueError("BROWSER_PATH environment variable is required")
        return self.BROWSER_PATH

    @property
    def BROWSER_USER_DATA_DIR_LOADED(self) -> Path:
        """Get BROWSER_USER_DATA_DIR, loading from environment if needed."""
        self._ensure_settings_loaded()
        if self.BROWSER_USER_DATA_DIR is None:
            raise ValueError("BROWSER_USER_DATA_DIR environment variable is required")
        return self.BROWSER_USER_DATA_DIR

    @property
    def OUTPUT_DIR_LOADED(self) -> Path:
        """Get OUTPUT_DIR, loading from environment if needed."""
        self._ensure_settings_loaded()
        return self.OUTPUT_DIR

    @property
    def LOG_DIR_LOADED(self) -> Path:
        """Get LOG_DIR, loading from environment if needed."""
        self._ensure_settings_loaded()
        return self.LOG_DIR

    @property
    def TEMPLATE_PATH_LOADED(self) -> str:
        """Get TEMPLATE_PATH, loading from environment if needed."""
        self._ensure_settings_loaded()
        return self.TEMPLATE_PATH

    @property
    def TIMEZONE_LOADED(self) -> timezone:
        """Get TIMEZONE, loading from environment if needed."""
        self._ensure_settings_loaded()
        return self.TIMEZONE

    def __post_init__(self) -> None:
        """Performs validation after the object has been initialized."""
        # Don't load environment variables during import - do it lazily when needed
        # This prevents PyInstaller build issues and allows the module to be imported
        # without requiring environment variables to be set
        pass

    def _ensure_settings_loaded(self) -> None:
        """Ensure essential settings are loaded from environment variables.

        This method is called lazily when essential settings are accessed, preventing
        import-time errors during PyInstaller builds.
        """
        # Only load once
        if hasattr(self, "_settings_loaded"):
            return

        # Load only essential settings that are required for operation
        self._load_browser_settings()
        self._load_path_settings()

        # Mark as loaded
        object.__setattr__(self, "_settings_loaded", True)

    def _load_browser_settings(self) -> None:
        """Load browser-related settings from environment.

        IMPLEMENTATION NOTE: This method includes special handling for testing environments.
        When running tests (CI=true or PYTEST_CURRENT_TEST), the configuration provides
        dummy values for required browser paths instead of raising errors. This prevents
        import-time failures when tests don't have access to actual browser installations.

        The testing environment detection is crucial because:
        1. Tests may run in CI environments without browsers
        2. Import-time validation errors would prevent test collection
        3. Dummy values allow tests to run while maintaining validation in production
        """
        # Check if we're in a testing environment
        # This prevents import-time errors when running tests without browser setup
        is_testing = (
            os.getenv("PYTEST_CURRENT_TEST") is not None or os.getenv("CI") == "true"
        )

        if browser_path := os.getenv("BROWSER_PATH"):
            object.__setattr__(self, "BROWSER_PATH", Path(browser_path))
        elif is_testing:
            # Use dummy values for testing
            object.__setattr__(self, "BROWSER_PATH", Path("/dummy/browser/path"))
        else:
            raise ValueError("BROWSER_PATH environment variable is required")

        if browser_user_data := os.getenv("BROWSER_USER_DATA_DIR"):
            object.__setattr__(self, "BROWSER_USER_DATA_DIR", Path(browser_user_data))
        elif is_testing:
            # Use dummy values for testing
            object.__setattr__(self, "BROWSER_USER_DATA_DIR", Path("/dummy/user/data"))
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

        if timezone_offset := os.getenv("TIMEZONE_OFFSET"):
            try:
                hours = int(timezone_offset)
                object.__setattr__(self, "TIMEZONE", timezone(timedelta(hours=hours)))
            except ValueError:
                pass

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
