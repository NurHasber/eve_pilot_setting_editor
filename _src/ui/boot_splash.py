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
from ui.win_icon import apply_window_icon, set_app_user_model_id


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
    """Solid dark plate the size of the app; pulsing logo until handoff.

    Kept withdrawn (not destroyed) after reveal so a second Tk (MainWindow) stays healthy.
    """

    def __init__(self, min_ms: int = 1200) -> None:
        super().__init__()
        set_app_user_model_id()
        self.title("EVE Settings Copy")
        apply_window_icon(self)
        self._min_ms = min_ms
        self._t0 = time.perf_counter()
        self._done = False
        self._photos: list[tk.PhotoImage] = []
        self._frame_i = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=T.BG)

        w, h = T.WINDOW_W, T.WINDOW_H
        self._w, self._h = w, h
        self.update_idletasks()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.canvas = tk.Canvas(
            self,
            width=w,
            height=h,
            bg=T.BG,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_rectangle(0, 0, w - 1, h - 1, outline=T.BORDER, width=1)

        base = _load_logo(200)
        frames = 24
        for i in range(frames):
            t = i / frames
            pulse = 0.88 + 0.12 * math.sin(t * math.pi * 2)
            lw = max(8, int(base.width * pulse))
            lh = max(8, int(base.height * pulse))
            scaled = base.resize((lw, lh), Image.Resampling.LANCZOS)
            plate = Image.new("RGBA", (w, h), (11, 14, 17, 255))
            ox = (w - lw) // 2
            oy = (h - lh) // 2
            plate.alpha_composite(scaled, (ox, oy))
            self._photos.append(_to_photo(self, plate.convert("RGB")))

        self._img_id = self.canvas.create_image(w // 2, h // 2, image=self._photos[0])
        self.update_idletasks()
        self.update()

    def geometry_str(self) -> str:
        return f"{self._w}x{self._h}+{self.winfo_x()}+{self.winfo_y()}"

    def _tick_frame(self) -> None:
        if self._done or not self._photos:
            return
        self._frame_i = (self._frame_i + 1) % len(self._photos)
        self.canvas.itemconfigure(self._img_id, image=self._photos[self._frame_i])

    def pump_while(self, work) -> None:
        """Run callable while animating; then hold until min_ms elapsed."""
        result = None
        error: BaseException | None = None
        finished = False

        def _run() -> None:
            nonlocal result, error, finished
            try:
                result = work()
            except BaseException as exc:  # noqa: BLE001
                error = exc
            finally:
                finished = True

        # Drive work on the next idle slice so the splash paints first.
        self.after(1, _run)
        while not finished and not self._done:
            self._tick_frame()
            try:
                self.update()
            except tk.TclError:
                break
            time.sleep(0.02)

        if error is not None:
            raise error

        while not self._done:
            elapsed_ms = (time.perf_counter() - self._t0) * 1000
            if elapsed_ms >= self._min_ms:
                break
            self._tick_frame()
            try:
                self.update()
            except tk.TclError:
                break
            time.sleep(0.04)

        return result

    def hide_keep_alive(self) -> None:
        """Hide without destroy — required when MainWindow is a second Tk."""
        self._done = True
        try:
            self.withdraw()
            self.attributes("-topmost", False)
        except tk.TclError:
            pass
