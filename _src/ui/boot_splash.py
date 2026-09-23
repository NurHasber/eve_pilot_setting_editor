"""Transparent boot animation (no static splash image beforehand)."""

from __future__ import annotations

import base64
import math
import tkinter as tk
from io import BytesIO

from PIL import Image

from core import asset_path
from ui.win_icon import apply_window_icon, set_app_user_model_id

CHROMA = "#010203"  # removed by transparentcolor — no visible "black card"


def _load_logo(max_size: int = 220) -> Image.Image:
    path = asset_path("assets", "icons", "logo_eagle.png")
    img = Image.open(path).convert("RGBA")
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return img


def _to_photo(master: tk.Misc, img: Image.Image) -> tk.PhotoImage:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return tk.PhotoImage(master=master, data=base64.b64encode(buf.getvalue()))


class BootSplash(tk.Tk):
    """Frameless chromakey splash — only the pulsing eagle, no background plate."""

    def __init__(self, duration_ms: int = 1400) -> None:
        super().__init__()
        set_app_user_model_id()
        self.title("EVE Settings Copy")
        apply_window_icon(self)
        self._duration_ms = duration_ms
        self._done = False
        self._photos: list[tk.PhotoImage] = []
        self._frame_i = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=CHROMA)
        try:
            self.attributes("-transparentcolor", CHROMA)
        except tk.TclError:
            pass

        size = 280
        self.geometry(f"{size}x{size}")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - size) // 2
        y = (self.winfo_screenheight() - size) // 2
        self.geometry(f"+{x}+{y}")

        self.canvas = tk.Canvas(
            self,
            width=size,
            height=size,
            bg=CHROMA,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        base = _load_logo(200)
        # Start already mid-motion (no static “posed” logo frame).
        frames = 20
        for i in range(frames):
            t = (i + 1) / frames  # skip t=0 static
            pulse = 0.86 + 0.14 * math.sin(t * math.pi * 2)  # continuous pulse
            # fade in quickly, hold, fade out at the end
            if t < 0.15:
                alpha = t / 0.15
            elif t > 0.85:
                alpha = max(0.0, (1.0 - t) / 0.15)
            else:
                alpha = 1.0
            w = max(8, int(base.width * pulse))
            h = max(8, int(base.height * pulse))
            scaled = base.resize((w, h), Image.Resampling.LANCZOS)
            r, g, b, a = scaled.split()
            a = a.point(lambda p, al=alpha: int(p * al))
            scaled = Image.merge("RGBA", (r, g, b, a))
            canvas = Image.new("RGBA", (size, size), (1, 2, 3, 255))
            ox = (size - w) // 2
            oy = (size - h) // 2
            canvas.alpha_composite(scaled, (ox, oy))
            self._photos.append(_to_photo(self, canvas.convert("RGB")))

        self._img_id = self.canvas.create_image(
            size // 2, size // 2, image=self._photos[0]
        )
        self.after(16, self._tick)
        self.after(duration_ms, self._finish)

    def _tick(self) -> None:
        if self._done:
            return
        self._frame_i = min(self._frame_i + 1, len(self._photos) - 1)
        self.canvas.itemconfigure(self._img_id, image=self._photos[self._frame_i])
        if self._frame_i < len(self._photos) - 1:
            self.after(50, self._tick)

    def _finish(self) -> None:
        self._done = True
        self.quit()

    def run(self) -> None:
        self.mainloop()
        try:
            self.destroy()
        except tk.TclError:
            pass
