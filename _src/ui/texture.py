"""Generate and cache the tiled background texture."""

from __future__ import annotations

import base64
import tkinter as tk
from io import BytesIO

from PIL import Image, ImageDraw

from . import theme as T

_TILE_CACHE: tk.PhotoImage | None = None
_FULL_CACHE: dict[tuple[int, int], tk.PhotoImage] = {}


def _make_tile(size: int = 96) -> Image.Image:
    """Subtle EVE-like cross-hatch / panel texture tile."""
    base = tuple(int(T.BG[i : i + 2], 16) for i in (1, 3, 5))
    img = Image.new("RGB", (size, size), base)
    draw = ImageDraw.Draw(img)
    # faint diagonal hatch both ways
    line_a = (base[0] + 10, base[1] + 12, base[2] + 14)
    line_b = (base[0] + 6, base[1] + 7, base[2] + 8)
    step = 8
    for i in range(-size, size * 2, step):
        draw.line([(i, 0), (i + size, size)], fill=line_a, width=1)
        draw.line([(i, size), (i + size, 0)], fill=line_b, width=1)
    # soft grid
    grid = (base[0] + 4, base[1] + 5, base[2] + 6)
    for x in range(0, size, 24):
        draw.line([(x, 0), (x, size)], fill=grid, width=1)
    for y in range(0, size, 24):
        draw.line([(0, y), (size, y)], fill=grid, width=1)
    # micro noise dots
    for y in range(0, size, 3):
        for x in range((y * 7) % 5, size, 5):
            shade = 8 if (x + y) % 2 == 0 else 4
            draw.point((x, y), fill=(base[0] + shade, base[1] + shade, base[2] + shade))
    return img


def texture_photo(master: tk.Misc, width: int, height: int) -> tk.PhotoImage:
    """Return a PhotoImage large enough to cover width×height by tiling."""
    global _FULL_CACHE
    key = (max(width, 1), max(height, 1))
    # round to reduce cache churn
    key = ((key[0] + 63) // 64 * 64, (key[1] + 63) // 64 * 64)
    cached = _FULL_CACHE.get(key)
    if cached is not None:
        return cached

    tile = _make_tile(96)
    full = Image.new("RGB", key, (0, 0, 0))
    for y in range(0, key[1], tile.height):
        for x in range(0, key[0], tile.width):
            full.paste(tile, (x, y))
    bio = BytesIO()
    full.save(bio, format="PNG")
    photo = tk.PhotoImage(data=base64.b64encode(bio.getvalue()), master=master)
    _FULL_CACHE[key] = photo
    # keep cache small
    if len(_FULL_CACHE) > 8:
        _FULL_CACHE.clear()
        _FULL_CACHE[key] = photo
    return photo


class TexturedFrame(tk.Frame):
    """Frame with a tiled cross-hatch background canvas behind children."""

    def __init__(self, master: tk.Misc, **kwargs) -> None:
        bg = kwargs.pop("bg", T.BG)
        super().__init__(master, bg=bg, **kwargs)
        self._bg_canvas = tk.Canvas(self, highlightthickness=0, bd=0, bg=bg)
        self._bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._bg_img: tk.PhotoImage | None = None
        self._bg_id = None
        self.bind("<Configure>", self._paint_bg)

    def _paint_bg(self, event=None) -> None:
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 2 or h < 2:
            return
        self._bg_img = texture_photo(self, w, h)
        if self._bg_id is None:
            self._bg_id = self._bg_canvas.create_image(0, 0, anchor="nw", image=self._bg_img)
        else:
            self._bg_canvas.itemconfigure(self._bg_id, image=self._bg_img)
        self._bg_canvas.tag_lower(self._bg_id)
