"""About tab."""

from __future__ import annotations

import tkinter as tk
import webbrowser

from core import APP_NAME, APP_VERSION

from .. import theme as T
from ..texture import TexturedFrame
from ..widgets import TechPanel

# GitHub / ChooseALicense official guidance: no open-source license = all rights reserved.
LICENSE_DOCS_URL = "https://choosealicense.com/no-permission/"
GITHUB_LICENSE_DOCS_URL = (
    "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/"
    "customizing-your-repository/licensing-a-repository"
)

LICENSE_TEXT = (
    "Copyright © HesBi. All Rights Reserved.\n"
    "No permission is granted to copy, modify, distribute, or create derivative works "
    "of this application without prior written permission from the copyright holder.\n\n"
    "This follows GitHub’s default copyright position when no open-source license is offered:\n"
    f"{LICENSE_DOCS_URL}"
)

ABOUT_INTRO = f"{APP_NAME} was vibe-coded in Cursor by pilot HesBi."
ABOUT_TAGLINE = "Flag save capsulir!"


class AboutTab(TexturedFrame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        panel = TechPanel(self, title="ABOUT")
        panel.pack(fill=tk.BOTH, expand=True, padx=14, pady=10)
        body = panel.body

        tk.Label(
            body,
            text=f"{APP_NAME} v{APP_VERSION}",
            bg=T.BG_PANEL,
            fg=T.ORANGE,
            font=T.FONT_UI_BOLD,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 8))

        tk.Label(
            body,
            text=ABOUT_INTRO,
            bg=T.BG_PANEL,
            fg=T.TEXT,
            font=T.FONT_UI,
            wraplength=540,
            justify="left",
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            body,
            text=LICENSE_TEXT,
            bg=T.BG_PANEL,
            fg=T.TEXT_MUTED,
            font=T.FONT_SMALL,
            wraplength=540,
            justify="left",
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 4))

        link = tk.Label(
            body,
            text="Open official docs (choosealicense.com / No License)",
            bg=T.BG_PANEL,
            fg=T.CYAN,
            font=T.FONT_SMALL,
            cursor="hand2",
            anchor="w",
        )
        link.pack(fill=tk.X, pady=(0, 2))
        link.bind("<Button-1>", lambda e: webbrowser.open(LICENSE_DOCS_URL))

        link2 = tk.Label(
            body,
            text="GitHub Docs: Licensing a repository",
            bg=T.BG_PANEL,
            fg=T.CYAN,
            font=T.FONT_SMALL,
            cursor="hand2",
            anchor="w",
        )
        link2.pack(fill=tk.X, pady=(0, 12))
        link2.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_LICENSE_DOCS_URL))

        tk.Label(
            body,
            text=ABOUT_TAGLINE,
            bg=T.BG_PANEL,
            fg=T.ORANGE,
            font=T.FONT_UI_BOLD,
            anchor="w",
        ).pack(fill=tk.X)
