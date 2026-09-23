"""EVE Settings Copy — entry point."""

from __future__ import annotations

import sys
import tkinter as tk
import traceback
from pathlib import Path
from tkinter import messagebox

# Allow running as `python app.py` from _src/
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core import APP_NAME, app_dir  # noqa: E402


def _pyi_splash_update(text: str) -> None:
    try:
        import pyi_splash  # type: ignore

        pyi_splash.update_text(text)
    except Exception:
        pass


def _close_pyi_splash() -> None:
    """Close the PyInstaller onefile unpack splash if present."""
    try:
        import pyi_splash  # type: ignore

        pyi_splash.close()
    except Exception:
        pass


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
        _pyi_splash_update("Loading…")

        # Import UI while the unpack splash is still visible.
        from ui.boot_splash import BootSplash
        from ui.main_window import MainWindow

        _close_pyi_splash()

        # Transparent logo pulse, then the real window.
        BootSplash(duration_ms=1400).run()

        app = MainWindow()
        app.update_idletasks()
        app.lift()
        app.attributes("-topmost", True)
        app.after(250, lambda: app.attributes("-topmost", False))
        app.focus_force()
        app.mainloop()
    except Exception as exc:  # noqa: BLE001
        _close_pyi_splash()
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
