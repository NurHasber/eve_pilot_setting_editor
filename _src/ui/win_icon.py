"""Windows taskbar / window icon helpers."""

from __future__ import annotations

import ctypes
import sys
import tkinter as tk
from pathlib import Path

from core import asset_path

APP_USER_MODEL_ID = "HesBi.EveSettingsCopy"


def set_app_user_model_id(app_id: str = APP_USER_MODEL_ID) -> None:
    """Required so Windows groups the process and picks our .ico instead of python/tk."""
    if sys.platform != "win32":
        return
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def ico_path() -> Path | None:
    path = asset_path("assets", "icons", "app.ico")
    return path if path.is_file() else None


def apply_window_icon(window: tk.Misc) -> None:
    """Apply .ico via Tk APIs and WM_SETICON (needed for frameless / taskbar)."""
    path = ico_path()
    if path is None:
        return

    try:
        window.iconbitmap(default=str(path))
    except tk.TclError:
        try:
            window.iconbitmap(str(path))
        except tk.TclError:
            pass

    # Keep a PhotoImage ref on the window so GC does not drop iconphoto.
    try:
        png = asset_path("assets", "icons", "logo_eagle_28.png")
        if not png.is_file():
            png = asset_path("assets", "icons", "logo_eagle.png")
        if png.is_file():
            img = tk.PhotoImage(file=str(png), master=window)
            window._esc_icon_photo = img  # type: ignore[attr-defined]
            window.iconphoto(True, img)
    except tk.TclError:
        pass

    if sys.platform != "win32":
        return
    try:
        window.update_idletasks()
        hwnd = window.winfo_id()
        # Tk wraps the real Win32 HWND; GetParent often yields the outer frame.
        parent = ctypes.windll.user32.GetParent(hwnd)
        if parent:
            hwnd = parent

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010
        LR_DEFAULTSIZE = 0x0040
        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1

        hicon = ctypes.windll.user32.LoadImageW(
            None,
            str(path),
            IMAGE_ICON,
            0,
            0,
            LR_LOADFROMFILE | LR_DEFAULTSIZE,
        )
        if hicon:
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon)
            # Also try the raw Tk hwnd
            raw = window.winfo_id()
            if raw and raw != hwnd:
                ctypes.windll.user32.SendMessageW(raw, WM_SETICON, ICON_BIG, hicon)
                ctypes.windll.user32.SendMessageW(raw, WM_SETICON, ICON_SMALL, hicon)
    except Exception:
        pass
