"""EVE Settings Copy — entry point (installed onedir app)."""

from __future__ import annotations

import sys
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import messagebox

_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core import APP_NAME, app_dir  # noqa: E402


def _log_crash(exc: BaseException) -> Path:
    log_path = app_dir() / "EveSettingsCopy_error.log"
    text = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    try:
        log_path.write_text(text, encoding="utf-8")
    except OSError:
        pass
    return log_path


def main() -> None:
    try:
        # Transparent pulse only — no static PyInstaller splash image.
        from ui.boot_splash import BootSplash
        from ui.main_window import MainWindow

        BootSplash(duration_ms=1400).run()

        app = MainWindow()
        app.update_idletasks()
        app.lift()
        app.attributes("-topmost", True)
        app.after(250, lambda: app.attributes("-topmost", False))
        app.focus_force()
        app.mainloop()
    except Exception as exc:  # noqa: BLE001
        log_path = _log_crash(exc)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                APP_NAME,
                f"Failed to start:\n{exc}\n\nDetails saved to:\n{log_path}",
            )
            root.destroy()
        except Exception:
            pass
        raise


if __name__ == "__main__":
    main()
