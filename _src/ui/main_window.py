"""Main frameless EVE-styled application window."""

from __future__ import annotations

import ctypes
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from core import (
    APP_NAME,
    APP_VERSION,
    CHAR_RE,
    STATUS_RESET_MS,
    USER_RE,
    asset_path,
    backup_masters,
    copy_masters_to_all,
    find_settings_default,
    load_config,
    save_config,
)
from ui import theme as T
from ui.tabs.about import AboutTab
from ui.tabs.settings_copy import SettingsCopyTab
from ui.texture import TexturedFrame, texture_photo
from ui.widgets import StatusBar, TabBar, WindowButton
from ui.win_icon import apply_window_icon, set_app_user_model_id


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        set_app_user_model_id()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.minsize(560, 380)
        self.configure(bg=T.BG)
        # Icon before overrideredirect for a reliable taskbar glyph.
        apply_window_icon(self)
        self.overrideredirect(True)
        self._offset = (0, 0)
        self._status_reset_job: str | None = None
        self._is_max = False

        # Always start centered — never let Windows restore the last close position.
        self._force_center()
        self.withdraw()

        self.settings_dir = find_settings_default()
        self.config = load_config()
        self.master_user = tk.StringVar(value=self.config.get("master_user", ""))
        self.master_char = tk.StringVar(value=self.config.get("master_char", ""))
        self.path_var = tk.StringVar(
            value=str(self.settings_dir) if self.settings_dir else "NOT FOUND"
        )

        self._logo_img: tk.PhotoImage | None = None
        self._root_bg: tk.PhotoImage | None = None

        self._install_root_texture()
        self._build_chrome()
        self._build_body()
        self._validate_remembered_masters()
        # Re-apply after widgets exist (readonly Entry can miss the initial StringVar value).
        self.master_user.set(self.master_user.get())
        self.master_char.set(self.master_char.get())
        self._force_center()
        self.bind("<Map>", self._on_map)

        if not self.settings_dir:
            self.set_status(
                "Settings folder not found. Expected under "
                "%LOCALAPPDATA%\\CCP\\EVE\\d_eve_tq_tranquility\\settings_Default",
                error=True,
            )

        self.deiconify()
        self._force_center()
        self.attributes("-topmost", True)
        self._ensure_taskbar_button(reposition=True)
        self._force_center()
        self.after(200, lambda: self.attributes("-topmost", False))
        self.focus_force()
        self.after(80, lambda: apply_window_icon(self))

    def _install_root_texture(self) -> None:
        self._bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=T.BG)
        self._bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.bind("<Configure>", self._paint_root_bg)

    def _paint_root_bg(self, _event=None) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        self._root_bg = texture_photo(self, w, h)
        self._bg_canvas.delete("tex")
        self._bg_canvas.create_image(0, 0, anchor="nw", image=self._root_bg, tags="tex")
        self._bg_canvas.tag_lower("tex")

    def _ensure_taskbar_button(self, reposition: bool = False) -> None:
        """overrideredirect hides the taskbar entry — force WS_EX_APPWINDOW."""
        try:
            self.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = (style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            apply_window_icon(self)
            # Sync flash — async after() used to race and restore last position.
            self.withdraw()
            self.update_idletasks()
            self.deiconify()
            if reposition:
                self._force_center()
            apply_window_icon(self)
        except Exception:
            pass

    def _on_map(self, _event=None) -> None:
        if not self.overrideredirect():
            self.overrideredirect(True)
            self.after(30, self._ensure_taskbar_button)

    def _build_chrome(self) -> None:
        title = tk.Frame(self, bg=T.BG_TITLE, height=34)
        title.pack(fill=tk.X)
        title.pack_propagate(False)

        left = tk.Frame(title, bg=T.BG_TITLE)
        left.pack(side=tk.LEFT, padx=10, pady=3)
        logo_path = asset_path("assets", "icons", "logo_eagle_28.png")
        if not logo_path.is_file():
            logo_path = asset_path("assets", "icons", "logo_eagle.png")
        if logo_path.is_file():
            try:
                self._logo_img = tk.PhotoImage(file=str(logo_path))
                tk.Label(left, image=self._logo_img, bg=T.BG_TITLE).pack(side=tk.LEFT, padx=(0, 8))
            except tk.TclError:
                pass
        tk.Label(
            left,
            text=f"{APP_NAME} v{APP_VERSION}",
            bg=T.BG_TITLE,
            fg=T.TEXT,
            font=T.FONT_TITLE,
        ).pack(side=tk.LEFT)

        right = tk.Frame(title, bg=T.BG_TITLE)
        right.pack(side=tk.RIGHT, padx=8, pady=3)
        WindowButton(right, "min", self._minimize, size=26).pack(side=tk.LEFT, padx=3)
        WindowButton(right, "max", self._toggle_max, size=26).pack(side=tk.LEFT, padx=3)
        WindowButton(right, "close", self.destroy, hot=True, size=26).pack(side=tk.LEFT, padx=3)

        for w in (title, left):
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._on_move)
            w.bind("<Double-Button-1>", lambda e: self._toggle_max())

        tk.Frame(self, bg=T.BORDER, height=1).pack(fill=tk.X)

    def _minimize(self) -> None:
        self.overrideredirect(False)
        self.iconify()

    def _start_move(self, event) -> None:
        self._offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _on_move(self, event) -> None:
        if self._is_max:
            return
        x = event.x_root - self._offset[0]
        y = event.y_root - self._offset[1]
        self.geometry(f"+{x}+{y}")

    def _toggle_max(self) -> None:
        self._is_max = not self._is_max
        if self._is_max:
            self._restore_geom = self.geometry()
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            self.geometry(f"{sw}x{sh}+0+0")
        else:
            self.geometry(getattr(self, "_restore_geom", f"{T.WINDOW_W}x{T.WINDOW_H}"))

    def _force_center(self) -> None:
        """Screen-center with fixed size (ignore Windows last-close position)."""
        w, h = T.WINDOW_W, T.WINDOW_H
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.update_idletasks()

    def _center(self) -> None:
        self._force_center()

    def _build_body(self) -> None:
        self.tab_bar = TabBar(
            self,
            tabs=[
                ("settings", "Settings Copy"),
                ("about", "About"),
            ],
            on_change=self._on_tab,
        )
        self.tab_bar.pack(fill=tk.X)

        self.content = TexturedFrame(self)
        self.content.pack(fill=tk.BOTH, expand=True)

        self.pages: dict[str, tk.Frame] = {}
        self.pages["settings"] = SettingsCopyTab(
            self.content,
            path_var=self.path_var,
            user_var=self.master_user,
            char_var=self.master_char,
            on_open_path=self.open_settings_folder,
            on_pick_user=lambda: self.pick_master("user"),
            on_pick_char=lambda: self.pick_master("char"),
            on_copy=self.copy_to_all,
            on_backup=self.backup_masters_action,
        )
        self.pages["about"] = AboutTab(self.content)
        for page in self.pages.values():
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages["settings"].tkraise()

        self.status_bar = StatusBar(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.set_version(APP_VERSION)
        self.configure(highlightthickness=1, highlightbackground=T.BORDER)

    def _on_tab(self, key: str) -> None:
        page = self.pages.get(key)
        if page:
            page.tkraise()

    def _validate_remembered_masters(self) -> None:
        if not self.settings_dir:
            return
        changed = False
        for attr, kind, var in (
            ("master_user", "user", self.master_user),
            ("master_char", "char", self.master_char),
        ):
            name = var.get().strip()
            if not name:
                continue
            pattern = USER_RE if kind == "user" else CHAR_RE
            if not pattern.match(name) or not (self.settings_dir / name).is_file():
                var.set("")
                self.config.pop(attr, None)
                changed = True
        if changed:
            save_config(self.config)

    def persist_masters(self) -> None:
        self.config["master_user"] = self.master_user.get().strip()
        self.config["master_char"] = self.master_char.get().strip()
        save_config(self.config)

    def set_status(self, text: str, error: bool = False, auto_reset: bool = False) -> None:
        if self._status_reset_job is not None:
            self.after_cancel(self._status_reset_job)
            self._status_reset_job = None
        self.status_bar.set_status(text, error=error)
        if auto_reset:
            self._status_reset_job = self.after(STATUS_RESET_MS, self._reset_status)

    def _reset_status(self) -> None:
        self._status_reset_job = None
        self.status_bar.set_status("Ready.")

    def open_settings_folder(self) -> None:
        if self.settings_dir and self.settings_dir.is_dir():
            os.startfile(self.settings_dir)  # noqa: S606
        else:
            messagebox.showerror(APP_NAME, "Settings folder was not found.")

    def pick_master(self, kind: str) -> None:
        if not self.settings_dir or not self.settings_dir.is_dir():
            messagebox.showerror(APP_NAME, "Settings folder was not found.")
            return
        pattern = USER_RE if kind == "user" else CHAR_RE
        if kind == "user":
            title = "Select master core_user file"
            filetypes = [("EVE account settings", "core_user_*.dat"), ("All files", "*.*")]
        else:
            title = "Select master core_char file"
            filetypes = [("EVE character settings", "core_char_*.dat"), ("All files", "*.*")]
        path = filedialog.askopenfilename(
            title=title,
            initialdir=str(self.settings_dir),
            filetypes=filetypes,
        )
        if not path:
            return
        chosen = Path(path)
        if chosen.parent.resolve() != self.settings_dir.resolve():
            messagebox.showerror(APP_NAME, "Please select a file inside the detected settings folder.")
            return
        if not pattern.match(chosen.name):
            messagebox.showerror(
                APP_NAME,
                f"{chosen.name} is not a valid {'account' if kind == 'user' else 'character'} settings file.",
            )
            return
        if kind == "user":
            self.master_user.set(chosen.name)
        else:
            self.master_char.set(chosen.name)
        self.persist_masters()
        self.set_status(f"Master {kind} set to {chosen.name}.")

    def _require_settings(self) -> Path | None:
        if not self.settings_dir or not self.settings_dir.is_dir():
            self.set_status("Settings folder not found.", error=True)
            messagebox.showerror(APP_NAME, "Settings folder was not found.")
            return None
        return self.settings_dir

    def copy_to_all(self) -> None:
        settings = self._require_settings()
        if settings is None:
            return
        master_user = self.master_user.get().strip()
        master_char = self.master_char.get().strip()
        if not master_user and not master_char:
            messagebox.showwarning(
                APP_NAME, "Select at least one master file (core_user and/or core_char)."
            )
            return
        try:
            copied_user, copied_char = copy_masters_to_all(settings, master_user, master_char)
        except (OSError, ValueError) as exc:
            self.set_status(f"Copy failed: {exc}", error=True)
            messagebox.showerror(APP_NAME, str(exc))
            return
        parts = []
        if master_user:
            parts.append(f"{copied_user} user file(s)")
        if master_char:
            parts.append(f"{copied_char} char file(s)")
        self.set_status(
            f"All settings copied successfully ({', '.join(parts)}).",
            auto_reset=True,
        )

    def backup_masters_action(self) -> None:
        settings = self._require_settings()
        if settings is None:
            return
        master_user = self.master_user.get().strip()
        master_char = self.master_char.get().strip()
        if not master_user and not master_char:
            messagebox.showwarning(APP_NAME, "Select at least one master file to back up.")
            return
        try:
            backup_dir = backup_masters(settings, master_user, master_char)
        except OSError as exc:
            self.set_status(f"Backup failed: {exc}", error=True)
            messagebox.showerror(APP_NAME, str(exc))
            return
        count = sum(1 for n in (master_user, master_char) if n)
        self.set_status(
            f"Backup created: {backup_dir.name} ({count} file(s)).",
            auto_reset=True,
        )
