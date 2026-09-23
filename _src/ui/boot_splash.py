"""App-sized boot splash — same footprint as MainWindow for a reveal handoff."""

from __future__ import annotations

import base64
import math
import time
import tkinter as tk
from io import BytesIO

from PIL import Image

from core import asset_path
from ui import theme as T
from ui.win_icon import apply_window_icon


def _load_logo(max_size: int = 220) -> Image.Image:
    path = asset_path("assets", "icons", "logo_eagle.png")
    img = Image.open(path).convert("RGBA")
    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return img


def _to_photo(master: tk.Misc, img: Image.Image) -> tk.PhotoImage:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return tk.PhotoImage(master=master, data=base64.b64encode(buf.getvalue()))


class BootSplash(tk.Toplevel):
    """Dark plate matching MainWindow size; stays on top until close_splash()."""

    def __init__(self, master: tk.Misc, min_ms: int = 1400) -> None:
        super().__init__(master)
        self.title("EVE Settings Copy")
        apply_window_icon(self)
        self._min_ms = min_ms
        self._t0 = time.perf_counter()
        self._closed = False
        self._photos: list[tk.PhotoImage] = []
        self._frame_i = 0

        # Do NOT assign self._w / self._h — those are Tk's internal window path names.
        self._plate_w = T.WINDOW_W
        self._plate_h = T.WINDOW_H

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=T.BG)
        try:
            self.transient(master)
        except tk.TclError:
            pass

        self.update_idletasks()
        x = (self.winfo_screenwidth() - self._plate_w) // 2
        y = (self.winfo_screenheight() - self._plate_h) // 2
        self.geometry(f"{self._plate_w}x{self._plate_h}+{x}+{y}")

        self.canvas = tk.Canvas(
            self,
            width=self._plate_w,
            height=self._plate_h,
            bg=T.BG,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_rectangle(
            0, 0, self._plate_w - 1, self._plate_h - 1, outline=T.BORDER, width=1
        )

        base = _load_logo(200)
        frames = 24
        for i in range(frames):
            t = i / frames
            pulse = 0.88 + 0.12 * math.sin(t * math.pi * 2)
            lw = max(8, int(base.width * pulse))
            lh = max(8, int(base.height * pulse))
            scaled = base.resize((lw, lh), Image.Resampling.LANCZOS)
            plate = Image.new("RGBA", (self._plate_w, self._plate_h), (11, 14, 17, 255))
            ox = (self._plate_w - lw) // 2
            oy = (self._plate_h - lh) // 2
            plate.alpha_composite(scaled, (ox, oy))
            self._photos.append(_to_photo(self, plate.convert("RGB")))

        self._img_id = self.canvas.create_image(
            self._plate_w // 2, self._plate_h // 2, image=self._photos[0]
        )
        self.lift()
        self.update_idletasks()
        self.update()

    def geometry_str(self) -> str:
        return (
            f"{self._plate_w}x{self._plate_h}+{self.winfo_x()}+{self.winfo_y()}"
        )

    def _tick_frame(self) -> None:
        if self._closed or not self._photos:
            return
        self._frame_i = (self._frame_i + 1) % len(self._photos)
        self.canvas.itemconfigure(self._img_id, image=self._photos[self._frame_i])

    def hold_until_ready(self) -> None:
        """Animate until min display time; call after the main UI is mapped underneath."""
        while not self._closed:
            elapsed_ms = (time.perf_counter() - self._t0) * 1000
            if elapsed_ms >= self._min_ms:
                break
            self._tick_frame()
            try:
                self.update()
            except tk.TclError:
                break
            time.sleep(0.04)

    def close_splash(self) -> None:
        self._closed = True
        try:
            self.destroy()
        except tk.TclError:
            pass
