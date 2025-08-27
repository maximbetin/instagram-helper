"""Configuration settings for Instagram Helper (CDP + real profile)."""

from __future__ import annotations

import os
import platform
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar
from zoneinfo import ZoneInfo

# -------------------------- platform helpers ----------------------------------


def _is_wsl2() -> bool:
    return os.name == "posix" and "microsoft" in platform.uname().release.lower()


def _windows_userprofile_from_env() -> Path | None:
    up = os.environ.get("USERPROFILE") or os.environ.get("HOMEPATH")
    return Path(up) if up else None


def _wsl_windows_home() -> Path | None:
    # Best effort: /mnt/c/Users/<Name> based on $USERPROFILE if present
    up = _windows_userprofile_from_env()
    if up:
        drive = up.drive.rstrip(":") or "C"
        return (
            Path(f"/mnt/{drive.lower()}") / up.relative_to(up.drive + "\\").as_posix()
        )
    # Fallback: guess common shape
    user = os.environ.get("USERNAME") or os.environ.get("USER")
    return Path(f"/mnt/c/Users/{user}") if user else None


def _first_existing(paths: Iterable[Path]) -> Path | None:
    for p in paths:
        if p and p.exists():
            return p
    return None


# -------------------------- defaults discovery --------------------------------


def _discover_browser_path() -> Path | None:
    """Try Brave → Chrome → Edge."""
    if platform.system() == "Windows" or _is_wsl2():
        candidates = [
            Path(r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"),
            Path(
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
            ),
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        ]
        # If running inside WSL2, the Windows paths are still correct for launching.
        return _first_existing(candidates)
    else:
        candidates = [
            Path("/usr/bin/brave-browser"),
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/microsoft-edge"),
            Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ]
        return _first_existing(candidates)


def _default_user_data_dir(browser_path: Path | None) -> Path | None:
    """Return the profile root dir for the chosen browser."""
    if platform.system() == "Windows" or _is_wsl2():
        home = _windows_userprofile_from_env()
        if not home:
            return None
        if browser_path and "brave" in browser_path.name.lower():
            return home / r"AppData\Local\BraveSoftware\Brave-Browser\User Data"
        if browser_path and "chrome" in browser_path.name.lower():
            return home / r"AppData\Local\Google\Chrome\User Data"
        if browser_path and "msedge" in browser_path.name.lower():
            return home / r"AppData\Local\Microsoft\Edge\User Data"
        # Default to Chrome layout
        return home / r"AppData\Local\Google\Chrome\User Data"
    else:
        home = Path.home()
        if browser_path and "brave" in browser_path.name.lower():
            return home / ".config/BraveSoftware/Brave-Browser"
        if browser_path and "chrome" in browser_path.name.lower():
            return home / ".config/google-chrome"
        if browser_path and "edge" in browser_path.name.lower():
            return home / ".config/microsoft-edge"
        return home / ".config/google-chrome"


def _default_output_dir() -> Path:
    if platform.system() == "Windows":
        home = _windows_userprofile_from_env() or Path.home()
        return home / "Desktop" / "ig_helper"
    if _is_wsl2():
        home = _wsl_windows_home() or Path.home()
        return home / "Desktop" / "ig_helper"
    return Path.home() / "Desktop" / "ig_helper"


# ------------------------------- settings -------------------------------------


@dataclass(frozen=True, kw_only=True)
class Settings:
    """Central app configuration (immutable)."""

    # Project root
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent

    # Paths
    OUTPUT_DIR: Path = field(default_factory=_default_output_dir)
    LOG_DIR: Path = field(default_factory=_default_output_dir)

    # Timezone (IANA)
    TIMEZONE: ZoneInfo = field(default_factory=lambda: ZoneInfo("Europe/Madrid"))

    # Browser (real profile via CDP)
    BROWSER_PATH: Path | None = field(default_factory=_discover_browser_path)
    BROWSER_USER_DATA_DIR: Path | None = field(
        default_factory=lambda: _default_user_data_dir(_discover_browser_path())
    )
    BROWSER_PROFILE_DIR: str = "Default"  # e.g. "Default", "Profile 1"
    BROWSER_DEBUG_PORT: int = 9222
    BROWSER_REMOTE_HOST: str = "localhost"
    BROWSER_CONNECT_SCHEME: str = "http"
    BROWSER_START_URL: str = "https://www.instagram.com/"

    # Instagram scraping
    INSTAGRAM_URL: str = "https://www.instagram.com/"
    INSTAGRAM_POST_LOAD_TIMEOUT: int = 20_000  # ms
    INSTAGRAM_MAX_POSTS_PER_ACCOUNT: int = 3

    # Default accounts (edit as needed)
    INSTAGRAM_ACCOUNTS: list[str] = field(
        default_factory=lambda: [
            "agendagijon",
            "asociacionelviescu",
            "asturiasacoge",
            "asturiesculturaenrede",
            "aytocastrillon",
            "aytoviedo",
            "ayuntamientocabranes",
            "bandinalagarrapiella",
            "biodevas",
            "centroniemeyer",
            "centros_sociales_oviedo",
            "chigreculturallatadezinc",
            "cinesfoncalada",
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
            "juventudgijon",
            "juventudoviedo",
            "kbunsgijon",
            "kuivi_almacenes",
            "laboralciudadcultura",
            "lacompaniadelalba",
            "lasalvaje.oviedo",
            "mierescultura",
            "museosgijonxixon",
            "museudelpuebludasturies",
            "nortes.me",
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

    # Mutable updates on a frozen dataclass (explicit)
    def update_instagram_settings(self, max_posts: int, timeout_ms: int) -> None:
        object.__setattr__(
            self, "INSTAGRAM_MAX_POSTS_PER_ACCOUNT", max(1, int(max_posts))
        )
        object.__setattr__(
            self, "INSTAGRAM_POST_LOAD_TIMEOUT", max(1_000, int(timeout_ms))
        )

    def __post_init__(self) -> None:
        # Ensure dirs exist
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Warn if browser/profile cannot be resolved
        if self.BROWSER_PATH is None or not Path(self.BROWSER_PATH).exists():
            # Keep running; browser_manager will fall back or raise with a clear error
            pass
        if (
            self.BROWSER_USER_DATA_DIR is None
            or not Path(self.BROWSER_USER_DATA_DIR).exists()
        ):
            # Still acceptable; browser can create the dir, but login may not be present
            pass


# Singleton
settings = Settings()
