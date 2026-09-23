"""Business logic for EVE settings copy / backup."""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

APP_NAME = "EVE Settings Copy"
APP_VERSION = "1.0.5"
CONFIG_NAME = "config.json"
STATUS_RESET_MS = 4000

USER_RE = re.compile(r"^core_user_(\d+)\.dat$", re.IGNORECASE)
CHAR_RE = re.compile(r"^core_char_(\d+)\.dat$", re.IGNORECASE)


def app_data_dir() -> Path:
    """Persistent app folder under %LOCALAPPDATA%\\EveSettingsCopy (config, backups)."""
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local.is_dir():
        local = Path.home() / "AppData" / "Local"
    path = local / "EveSettingsCopy"
    path.mkdir(parents=True, exist_ok=True)
    return path


def app_dir() -> Path:
    """Directory for config.json / Backups. Frozen builds use LocalAppData."""
    if getattr(sys, "frozen", False):
        return app_data_dir()
    return Path(__file__).resolve().parent.parent


def asset_path(*parts: str) -> Path:
    """Resolve an asset path for source, onedir, and onefile (_MEIPASS) builds."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            bundled = Path(meipass).joinpath(*parts)
            if bundled.exists():
                return bundled
        beside_exe = Path(sys.executable).resolve().parent.joinpath(*parts)
        if beside_exe.exists():
            return beside_exe
    return Path(__file__).resolve().parent.parent.joinpath(*parts)


def config_path() -> Path:
    return app_dir() / CONFIG_NAME


def load_config() -> dict:
    path = config_path()
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_config(data: dict) -> None:
    path = config_path()
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_settings_default() -> Path | None:
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if not local.is_dir():
        local = Path.home() / "AppData" / "Local"

    primary = local / "CCP" / "EVE" / "d_eve_tq_tranquility" / "settings_Default"
    if primary.is_dir():
        return primary

    eve_root = local / "CCP" / "EVE"
    if eve_root.is_dir():
        for match in sorted(eve_root.rglob("settings_Default")):
            if match.is_dir():
                return match
        for folder in sorted(eve_root.rglob("settings_*")):
            if folder.is_dir() and any(folder.glob("core_*.dat")):
                return folder
    return None


def list_profile_files(settings_dir: Path, kind: str) -> list[str]:
    pattern = USER_RE if kind == "user" else CHAR_RE
    names: list[str] = []
    for entry in settings_dir.iterdir():
        if entry.is_file() and pattern.match(entry.name):
            names.append(entry.name)
    return sorted(names)


def copy_masters_to_all(
    settings_dir: Path,
    master_user: str,
    master_char: str,
) -> tuple[int, int]:
    """Copy master files onto all other matching profiles. Returns (user_count, char_count)."""
    copied_user = 0
    copied_char = 0

    if master_user:
        if not USER_RE.match(master_user):
            raise ValueError(f"{master_user} is not a valid core_user file.")
        src = settings_dir / master_user
        if not src.is_file():
            raise FileNotFoundError(f"Master user file not found: {master_user}")
        for name in list_profile_files(settings_dir, "user"):
            if name.lower() == master_user.lower():
                continue
            shutil.copy2(src, settings_dir / name)
            copied_user += 1

    if master_char:
        if not CHAR_RE.match(master_char):
            raise ValueError(f"{master_char} is not a valid core_char file.")
        src = settings_dir / master_char
        if not src.is_file():
            raise FileNotFoundError(f"Master char file not found: {master_char}")
        for name in list_profile_files(settings_dir, "char"):
            if name.lower() == master_char.lower():
                continue
            shutil.copy2(src, settings_dir / name)
            copied_char += 1

    return copied_user, copied_char


def backup_masters(
    settings_dir: Path,
    master_user: str,
    master_char: str,
) -> Path:
    """Copy selected masters into a unique Backup folder. Returns backup dir path."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_root = app_dir() / "Backups"
    backup_dir = backup_root / f"backup_{stamp}"
    suffix = 1
    while backup_dir.exists():
        backup_dir = backup_root / f"backup_{stamp}_{suffix}"
        suffix += 1

    backup_dir.mkdir(parents=True, exist_ok=False)
    saved: list[str] = []
    for name in (master_user, master_char):
        if not name:
            continue
        src = settings_dir / name
        if not src.is_file():
            raise FileNotFoundError(f"File not found: {name}")
        shutil.copy2(src, backup_dir / name)
        saved.append(name)

    (backup_dir / "backup_info.txt").write_text(
        f"Backup created: {stamp}\n"
        f"Settings folder: {settings_dir}\n"
        f"Files:\n" + "\n".join(f"  - {n}" for n in saved) + "\n",
        encoding="utf-8",
    )
    return backup_dir
