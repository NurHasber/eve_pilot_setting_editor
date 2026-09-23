"""
Bootstrap / install helper notes:

PyInstaller --onefile ALWAYS re-extracts its archive on every launch (bootloader design).
There is no reliable "skip if already unpacked" for onefile.

Fast launches require a permanent onedir install on disk. This launcher:
  1) Ensures %LOCALAPPDATA%\\EveSettingsCopy\\app\\ contains the current version (from payload.zip)
  2) Starts that onedir exe (subsequent runs of THAT exe are instant)

The versioned GitHub artifact is still one file: EveSettingsCopy_vX.Y.Z.exe (this launcher
with payload.zip embedded). First start / version bump extracts once into LocalAppData.
Running the installed app directly from LocalAppData\\EveSettingsCopy\\app\\ is instant.

If you keep double-clicking the GitHub onefile launcher, you still pay a small Python
bootloader cost each time — pin/use the installed app for zero unpack delay.
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

# Keep in sync with core.logic.APP_VERSION when releasing.
APP_VERSION = "1.0.4"
APP_NAME = "EVE Settings Copy"


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
    # Dev: expect payload next to this file after build_release.py
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
        # Accept either flat onedir or a single top-level folder
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


def show_status(title: str, text: str) -> tk.Tk:
    root = tk.Tk()
    root.title(title)
    root.geometry("360x120")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    tk.Label(root, text=text, font=("Segoe UI", 10), wraplength=320, justify="center").pack(
        expand=True, padx=16, pady=16
    )
    root.update()
    root.update_idletasks()
    return root


def main() -> int:
    try:
        if needs_install():
            ui = show_status(APP_NAME, f"Installing v{APP_VERSION}…\nThis happens only once per version.")
            try:
                install_payload()
            finally:
                ui.destroy()
        exe = installed_exe()
        subprocess.Popen([str(exe)], cwd=str(exe.parent), close_fds=True)
        return 0
    except Exception as exc:  # noqa: BLE001
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
