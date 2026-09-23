"""Procedural thin-line icons via Pillow → Tk PhotoImage."""

from __future__ import annotations

import base64
import tkinter as tk
from io import BytesIO

from PIL import Image, ImageDraw


def make_icon(master: tk.Misc, kind: str, color: str, size: int = 18) -> tk.PhotoImage:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad = 2
    x0, y0, x1, y1 = pad, pad, size - pad - 1, size - pad - 1
    stroke = max(1, size // 12)

    def line(*pts: float) -> None:
        draw.line(list(pts), fill=color, width=stroke, joint="curve")

    def rect(a, b, c, d) -> None:
        draw.rectangle([a, b, c, d], outline=color, width=stroke)

    if kind == "settings":
        rect(x0 + 2, y0, x1 - 1, y1)
        line(x0 + 5, y0 + 4, x1 - 4, y0 + 4)
        line(x0 + 5, y0 + 8, x1 - 4, y0 + 8)
        line(x0 + 3, y1 - 3, x1 - 2, y0 + 3)
    elif kind == "profiles":
        cx = (x0 + x1) / 2
        r = size * 0.18
        draw.ellipse([cx - r, y0 + 1, cx + r, y0 + 1 + 2 * r], outline=color, width=stroke)
        draw.arc(
            [x0 + 1, y0 + size * 0.45, x1 - 1, y1 + 4],
            start=200,
            end=340,
            fill=color,
            width=stroke,
        )
    elif kind in ("about", "info"):
        draw.ellipse([x0, y0, x1, y1], outline=color, width=stroke)
        mx = (x0 + x1) / 2
        draw.ellipse([mx - 1, y0 + 3, mx + 1, y0 + 5], fill=color)
        line(mx, y0 + 7, mx, y1 - 3)
    elif kind == "folder":
        line(x0, y0 + 4, x0 + 5, y0 + 4, x0 + 7, y0 + 1, x1 - 1, y0 + 1)
        rect(x0, y0 + 4, x1, y1)
    elif kind == "copy":
        rect(x0 + 3, y0, x1, y1 - 3)
        rect(x0, y0 + 3, x1 - 3, y1)
    elif kind == "backup":
        rect(x0, y0 + 3, x1, y1)
        line(x0, y0 + 3, (x0 + x1) / 2, y0, x1, y0 + 3)
        line(x0 + 3, (y0 + y1) / 2 + 1, x1 - 3, (y0 + y1) / 2 + 1)
        draw.ellipse([x1 - 6, y1 - 6, x1 - 3, y1 - 3], fill=color)
    elif kind == "shield":
        mx = (x0 + x1) / 2
        line(
            mx,
            y0,
            x1,
            y0 + 3,
            x1 - 1,
            y0 + size * 0.55,
            mx,
            y1,
            x0 + 1,
            y0 + size * 0.55,
            x0,
            y0 + 3,
            mx,
            y0,
        )
    else:
        rect(x0, y0, x1, y1)

    bio = BytesIO()
    img.save(bio, format="PNG")
    return tk.PhotoImage(data=base64.b64encode(bio.getvalue()), master=master)
