from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from .. import theme as T
from ..texture import TexturedFrame
from ..widgets import ActionButton, DarkEntry, IconButton, TechPanel


class SettingsCopyTab(TexturedFrame):
    def __init__(
        self,
        master: tk.Misc,
        path_var: tk.StringVar,
        user_var: tk.StringVar,
        char_var: tk.StringVar,
        on_open_path: Callable[[], None],
        on_pick_user: Callable[[], None],
        on_pick_char: Callable[[], None],
        on_copy: Callable[[], None],
        on_backup: Callable[[], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        panel = TechPanel(self, title="CONFIGURATION")
        panel.pack(fill=tk.X, padx=14, pady=(6, 8))
        body = panel.body

        tk.Label(body, text="Source Path", bg=T.BG_PANEL, fg=T.TEXT_MUTED, font=T.FONT_SMALL).pack(
            anchor="w", pady=(0, 2)
        )
        path_row = tk.Frame(body, bg=T.BG_PANEL)
        path_row.pack(fill=tk.X, pady=(0, 8))
        DarkEntry(path_row, path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        IconButton(path_row, icon="folder", command=on_open_path, color=T.TEXT_MUTED, size=28).pack(
            side=tk.RIGHT
        )

        self._master_row(body, "Core User (Master)", user_var, on_pick_user)
        self._master_row(body, "Core Char (Master)", char_var, on_pick_char)

        actions = tk.Frame(self, bg=T.BG)
        actions.pack(fill=tk.X, padx=14, pady=(2, 4))
        ActionButton(
            actions,
            text="Copy to all others",
            accent=T.CYAN,
            icon="copy",
            command=on_copy,
            height=44,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 7))
        ActionButton(
            actions,
            text="Backup masters",
            accent=T.ORANGE,
            icon="backup",
            command=on_backup,
            height=44,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(7, 0))

        hint = (
            "Copy overwrites every other core_user_*.dat / core_char_*.dat "
            "in the settings folder with your master files (filenames kept)."
        )
        tk.Label(
            self,
            text=hint,
            bg=T.BG,
            fg=T.TEXT_DIM,
            font=T.FONT_SMALL,
            wraplength=600,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(2, 2))

    def _master_row(
        self,
        parent: tk.Misc,
        label: str,
        var: tk.StringVar,
        on_pick: Callable[[], None],
    ) -> None:
        row = tk.Frame(parent, bg=T.BG_PANEL)
        row.pack(fill=tk.X, pady=4)
        tk.Label(
            row,
            text=label,
            bg=T.BG_PANEL,
            fg=T.TEXT_MUTED,
            font=T.FONT_UI,
            width=17,
            anchor="w",
        ).pack(side=tk.LEFT)
        DarkEntry(row, var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        btn = tk.Canvas(
            row,
            width=28,
            height=28,
            bg=T.BG_BUTTON,
            highlightthickness=1,
            highlightbackground=T.BORDER,
            bd=0,
            cursor="hand2",
        )
        btn.pack(side=tk.RIGHT)
        btn.create_text(14, 14, text="···", fill=T.TEXT_MUTED, font=("Segoe UI", 11, "bold"))
        btn.bind("<Button-1>", lambda e: on_pick())
        btn.bind("<Enter>", lambda e: btn.configure(highlightbackground=T.ORANGE))
        btn.bind("<Leave>", lambda e: btn.configure(highlightbackground=T.BORDER))
