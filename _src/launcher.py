"""
Bootstrap launcher (versioned GitHub .exe).

PyInstaller onefile always unpacks before Python starts — that blank wait cannot be
removed for a fat onefile. We show a splash image during unpack (--splash), then
start the permanent onedir app under %LOCALAPPDATA%. Daily launches should use the
Desktop shortcut (instant).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
import zipfile
from pathlib import Path
from tkinter import messagebox

APP_VERSION = "1.0.8"
APP_NAME = "EVE Settings Copy"


def _splash_text(text: str) -> None:
    try:
        import pyi_splash  # type: ignore

        pyi_splash.update_text(text)
    except Exception:
        pass


def _close_pyi_splash(text: str | None = None) -> None:
    try:
        import pyi_splash  # type: ignore

        if text:
            try:
                pyi_splash.update_text(text)
            except Exception:
                pass
        pyi_splash.close()
    except Exception:
        pass


def install_root() -> Path:
    local = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local / "EveSettingsCopy"


def app_install_dir() -> Path:
    return install_root() / "app"


def installed_exe() -> Path:
    return app_install_dir() / "EveSettingsCopy.exe"


def version_marker() -> Path:
    return app_install_dir() / "version.txt"


def payload_zip() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "payload.zip"
    return Path(__file__).resolve().parent / "payload.zip"


def needs_install() -> bool:
    exe = installed_exe()
    marker = version_marker()
    if not exe.is_file() or not marker.is_file():
        return True
    try:
        return marker.read_text(encoding="utf-8").strip() != APP_VERSION
    except OSError:
        return True


def install_payload() -> None:
    zpath = payload_zip()
    if not zpath.is_file():
        raise FileNotFoundError(f"Missing payload: {zpath}")

    target = app_install_dir()
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(zpath, "r") as zf:
            zf.extractall(tmp_path)
        children = [p for p in tmp_path.iterdir()]
        source = children[0] if len(children) == 1 and children[0].is_dir() else tmp_path
        for item in source.iterdir():
            dest = target / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    if not installed_exe().is_file():
        raise FileNotFoundError("Install failed: EveSettingsCopy.exe not found in payload")
    version_marker().write_text(APP_VERSION + "\n", encoding="utf-8")


def main() -> int:
    try:
        try:
            from single_instance import activate_existing_window, already_running

            if already_running() and activate_existing_window():
                _close_pyi_splash()
                return 0
        except Exception:
            pass

        if needs_install():
            _splash_text("Installing…")
            install_payload()

        _splash_text("Starting…")
        from shortcuts import ensure_app_shortcuts

        ensure_app_shortcuts(installed_exe())

        # Hand off: close bootloader splash; installed app shows app-sized BootSplash.
        _close_pyi_splash()
        subprocess.Popen(
            [str(installed_exe())],
            cwd=str(installed_exe().parent),
            close_fds=True,
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        _close_pyi_splash()
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(APP_NAME, f"Failed to start:\n{exc}")
            root.destroy()
        except Exception:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
