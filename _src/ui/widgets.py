"""Reusable EVE-styled widgets."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from . import theme as T
from .icons import make_icon
from .texture import TexturedFrame


class TechPanel(tk.Frame):
    """Dark panel with angular corner cuts; sized to content (not empty expand)."""

    def __init__(self, master: tk.Misc, title: str = "", **kwargs) -> None:
        super().__init__(master, bg=T.BG, **kwargs)
        self._title = title
        self._canvas = tk.Canvas(self, bg=T.BG, highlightthickness=0, bd=0)
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.body = tk.Frame(self, bg=T.BG_PANEL)
        self.body.pack(fill=tk.X, padx=12, pady=(20, 12))
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _event=None) -> None:
        c = self._canvas
        c.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 20 or h < 20:
            return
        cut = 8
        pts = [
            cut, 1,
            w - cut, 1,
            w - 1, cut,
            w - 1, h - cut,
            w - cut, h - 1,
            cut, h - 1,
            1, h - cut,
            1, cut,
        ]
        c.create_polygon(pts, outline=T.BORDER, fill=T.BG_PANEL, width=1)
        c.create_line(cut, 1, cut + 22, 1, fill=T.ORANGE, width=1)
        if self._title:
            c.create_text(12, 3, anchor="nw", text=self._title, fill=T.ORANGE, font=T.FONT_SECTION)


class IconButton(tk.Canvas):
    def __init__(
        self,
        master: tk.Misc,
        icon: str,
        command: Callable[[], None] | None = None,
        color: str = T.TEXT_MUTED,
        size: int = 28,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=size,
            height=size,
            bg=T.BG_BUTTON,
            highlightthickness=1,
            highlightbackground=T.BORDER,
            bd=0,
            cursor="hand2",
            **kwargs,
        )
        self._command = command
        self._photo = make_icon(self, icon, color, size=max(12, size - 12))
        self.create_image(size // 2, size // 2, image=self._photo)
        self.bind("<Button-1>", lambda e: self._command and self._command())
        self.bind("<Enter>", lambda e: self.configure(highlightbackground=T.ORANGE))
        self.bind("<Leave>", lambda e: self.configure(highlightbackground=T.BORDER))


class ActionButton(tk.Canvas):
    """Reference-like action button: soft fill, dual rim, gentle corner cuts, glow edge."""

    def __init__(
        self,
        master: tk.Misc,
        text: str,
        accent: str,
        icon: str,
        command: Callable[[], None] | None = None,
        height: int = 44,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            height=height,
            bg=T.BG,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs,
        )
        self._text = text
        self._accent = accent
        self._icon = icon
        self._command = command
        self._height = height
        self._photo: tk.PhotoImage | None = None
        self._hovered = False
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", lambda e: self._command and self._command())
        self.bind("<Enter>", self._hover_on)
        self.bind("<Leave>", self._hover_off)

    def _hover_on(self, _e=None) -> None:
        self._hovered = True
        self._redraw()

    def _hover_off(self, _e=None) -> None:
        self._hovered = False
        self._redraw()

    @staticmethod
    def _chamfer(w: int, h: int, cut: int, inset: int = 0) -> list[int]:
        i = inset
        c = cut
        return [
            c + i, i,
            w - c - i, i,
            w - 1 - i, c + i,
            w - 1 - i, h - c - i,
            w - c - i, h - 1 - i,
            c + i, h - 1 - i,
            i, h - c - i,
            i, c + i,
        ]

    def _redraw(self, _event=None) -> None:
        self.delete("all")
        w = max(self.winfo_width(), 12)
        h = self._height
        accent = self._accent
        # darker navy/amber-tinted fill matching reference
        if accent.lower() in (T.CYAN.lower(), T.CYAN_HOT.lower(), "#3aa0d9", "#55b6e8"):
            fill = "#102028" if not self._hovered else "#153040"
            glow = "#1A4A66"
        else:
            fill = "#1A1410" if not self._hovered else "#261C12"
            glow = "#5A3A18"

        # outer glow rim
        self.create_polygon(self._chamfer(w, h, 7, 0), outline=glow, fill=fill, width=3)
        # main accent rim
        self.create_polygon(
            self._chamfer(w, h, 7, 1),
            outline=accent,
            fill=fill,
            width=2 if self._hovered else 1,
        )
        # inner hairline
        self.create_polygon(self._chamfer(w, h, 7, 4), outline=accent, fill="", width=1)

        # subtle top highlight
        self.create_line(12, 3, w - 12, 3, fill=accent if self._hovered else glow)

        self._photo = make_icon(self, self._icon, accent, size=18)
        # center icon+text as a group
        text_w = len(self._text) * 7
        group_w = 18 + 10 + text_w
        cx = w // 2
        icon_x = cx - group_w // 2 + 9
        text_x = icon_x + 18
        self.create_image(icon_x, h // 2, image=self._photo)
        self.create_text(
            text_x,
            h // 2,
            anchor="w",
            text=self._text,
            fill=accent,
            font=T.FONT_ACTION,
        )


class DarkEntry(tk.Frame):
    """Readonly-looking entry that reliably shows StringVar values on Windows Tk."""

    def __init__(self, master: tk.Misc, textvariable: tk.StringVar, **kwargs) -> None:
        super().__init__(master, bg=T.BORDER, padx=1, pady=1, **kwargs)
        self._var = textvariable
        self.entry = tk.Entry(
            self,
            bg=T.BG_INPUT,
            fg=T.TEXT,
            insertbackground=T.TEXT,
            relief="flat",
            font=T.FONT_UI,
            readonlybackground=T.BG_INPUT,
            disabledbackground=T.BG_INPUT,
            disabledforeground=T.TEXT,
        )
        self.entry.pack(fill=tk.BOTH, expand=True, ipady=4, padx=6)
        self._apply()
        self._var.trace_add("write", lambda *_args: self._apply())

    def _apply(self) -> None:
        value = self._var.get()
        self.entry.configure(state="normal")
        self.entry.delete(0, tk.END)
        if value:
            self.entry.insert(0, value)
        self.entry.configure(state="readonly")


class WindowButton(tk.Canvas):
    """Equal-size title-bar control (min / max / close)."""

    def __init__(
        self,
        master: tk.Misc,
        kind: str,
        command: Callable[[], None],
        hot: bool = False,
        size: int = 28,
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            width=size,
            height=size,
            bg=T.BG_TITLE,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            **kwargs,
        )
        self._kind = kind
        self._command = command
        self._hot = hot
        self._size = size
        self._hovered = False
        self.bind("<Button-1>", lambda e: self._command())
        self.bind("<Enter>", self._on)
        self.bind("<Leave>", self._off)
        self._redraw()

    def _on(self, _e=None) -> None:
        self._hovered = True
        self._redraw()

    def _off(self, _e=None) -> None:
        self._hovered = False
        self._redraw()

    def _redraw(self) -> None:
        self.delete("all")
        s = self._size
        pad = 3
        accent = T.ORANGE if self._hot else T.BORDER
        fg = T.ORANGE if self._hot else (T.TEXT if self._hovered else T.TEXT_MUTED)
        if self._hovered and self._hot:
            accent = T.ORANGE_HOT
            fg = T.ORANGE_HOT
        # rounded-square frame
        self.create_rectangle(pad, pad, s - pad, s - pad, outline=accent, fill="#14181E", width=1)
        cx = cy = s / 2
        if self._kind == "min":
            self.create_line(cx - 5, cy, cx + 5, cy, fill=fg, width=1)
        elif self._kind == "max":
            self.create_rectangle(cx - 5, cy - 5, cx + 5, cy + 5, outline=fg, width=1)
        else:  # close
            self.create_line(cx - 4, cy - 4, cx + 4, cy + 4, fill=fg, width=1)
            self.create_line(cx + 4, cy - 4, cx - 4, cy + 4, fill=fg, width=1)


class TabBar(TexturedFrame):
    def __init__(
        self,
        master: tk.Misc,
        tabs: list[tuple[str, str]],
        on_change: Callable[[str], None],
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)
        self._on_change = on_change
        self._tabs = tabs
        self._active = tabs[0][0]
        self._buttons: dict[str, tk.Frame] = {}
        self._icons: dict[str, tk.PhotoImage] = {}
        self._labels: dict[str, tuple[tk.Label, tk.Label]] = {}

        row = tk.Frame(self, bg=T.BG)
        row.pack(fill=tk.X, padx=14, pady=(2, 0))
        # keep row transparent over texture by matching — children use solid; lift row
        row.configure(bg=T.BG)
        for key, label in tabs:
            self._make_tab(row, key, label)
        self._underline = tk.Canvas(self, height=2, bg=T.BG, highlightthickness=0, bd=0)
        self._underline.pack(fill=tk.X, padx=14, pady=(0, 2))
        self.after_idle(self._paint_underline)

    def _make_tab(self, parent: tk.Frame, key: str, label: str) -> None:
        fr = tk.Frame(parent, bg=T.BG, cursor="hand2")
        fr.pack(side=tk.LEFT, padx=(0, 18), pady=4)
        color = T.ORANGE if key == self._active else T.TEXT_MUTED
        icon = make_icon(fr, key if key in ("settings", "profiles", "about") else "about", color, 14)
        self._icons[key] = icon
        img = tk.Label(fr, image=icon, bg=T.BG)
        img.pack(side=tk.LEFT, padx=(0, 5))
        txt = tk.Label(fr, text=label, bg=T.BG, fg=color, font=T.FONT_TAB)
        txt.pack(side=tk.LEFT)
        for w in (fr, img, txt):
            w.bind("<Button-1>", lambda e, k=key: self.select(k))
        self._buttons[key] = fr
        self._labels[key] = (img, txt)

    def select(self, key: str) -> None:
        if key == self._active:
            return
        self._active = key
        for k, fr in self._buttons.items():
            color = T.ORANGE if k == key else T.TEXT_MUTED
            icon_kind = k if k in ("settings", "profiles", "about") else "about"
            self._icons[k] = make_icon(fr, icon_kind, color, 14)
            img, txt = self._labels[k]
            img.configure(image=self._icons[k])
            txt.configure(fg=color)
        self._paint_underline()
        self._on_change(key)

    def _paint_underline(self) -> None:
        self.update_idletasks()
        self._underline.delete("all")
        fr = self._buttons.get(self._active)
        if not fr:
            return
        x = fr.winfo_x()
        w = fr.winfo_width()
        self._underline.create_rectangle(x, 0, x + w, 2, outline="", fill=T.ORANGE)


class StatusBar(tk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=T.BG_TITLE, height=26, **kwargs)
        self.pack_propagate(False)
        self._status = tk.StringVar(value="Ready.")
        left = tk.Frame(self, bg=T.BG_TITLE)
        left.pack(side=tk.LEFT, padx=12)
        self._dot = tk.Canvas(left, width=8, height=8, bg=T.BG_TITLE, highlightthickness=0, bd=0)
        self._dot.pack(side=tk.LEFT, padx=(0, 8), pady=9)
        self._dot.create_oval(0, 0, 8, 8, fill=T.CYAN, outline=T.CYAN)
        tk.Label(
            left,
            textvariable=self._status,
            bg=T.BG_TITLE,
            fg=T.TEXT_MUTED,
            font=T.FONT_SMALL,
        ).pack(side=tk.LEFT)

        right = tk.Frame(self, bg=T.BG_TITLE)
        right.pack(side=tk.RIGHT, padx=12)
        self._ver = tk.Label(right, text="v1.0.0", bg=T.BG_TITLE, fg=T.TEXT_DIM, font=T.FONT_SMALL)
        self._ver.pack(side=tk.LEFT, padx=(0, 8))
        self._info_icon = make_icon(right, "info", T.TEXT_DIM, 11)
        self._shield_icon = make_icon(right, "shield", T.TEXT_DIM, 11)
        tk.Label(right, image=self._info_icon, bg=T.BG_TITLE).pack(side=tk.LEFT, padx=3)
        tk.Label(right, image=self._shield_icon, bg=T.BG_TITLE).pack(side=tk.LEFT, padx=3)

    def set_version(self, version: str) -> None:
        self._ver.configure(text=f"v{version}")

    def set_status(self, text: str, error: bool = False) -> None:
        self._status.set(text)
        color = T.ERROR if error else T.CYAN
        self._dot.delete("all")
        self._dot.create_oval(0, 0, 8, 8, fill=color, outline=color)


# re-export for type checkers / unused import silence
__all__ = [
    "TechPanel",
    "IconButton",
    "ActionButton",
    "DarkEntry",
    "WindowButton",
    "TabBar",
    "StatusBar",
    "TexturedFrame",
]
