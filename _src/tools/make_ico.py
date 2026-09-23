"""Build a valid multi-size Windows .ico (PNG-compressed entries)."""

from __future__ import annotations

import struct
from io import BytesIO
from pathlib import Path

from PIL import Image

SRC = Path(__file__).resolve().parents[1] / "assets" / "icons" / "logo_eagle.png"
OUT = Path(__file__).resolve().parents[1] / "assets" / "icons" / "app.ico"
BG = (11, 14, 17, 255)
SIZES = (16, 24, 32, 48, 64, 128, 256)


def _framed(src: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), BG)
    scaled = src.resize((size, size), Image.Resampling.LANCZOS)
    canvas.alpha_composite(scaled)
    return canvas


def _png_bytes(img: Image.Image) -> bytes:
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def write_ico(path: Path, images: list[Image.Image]) -> None:
    pngs = [_png_bytes(im) for im in images]
    count = len(pngs)
    offset = 6 + 16 * count
    header = struct.pack("<HHH", 0, 1, count)
    entries = bytearray()
    blobs = bytearray()
    for im, data in zip(images, pngs):
        w, h = im.size
        entry = struct.pack(
            "<BBBBHHII",
            0 if w >= 256 else w,
            0 if h >= 256 else h,
            0,  # color count
            0,  # reserved
            1,  # planes
            32,  # bit count
            len(data),
            offset + len(blobs),
        )
        entries.extend(entry)
        blobs.extend(data)
    path.write_bytes(header + entries + blobs)


def main() -> None:
    src = Image.open(SRC).convert("RGBA")
    images = [_framed(src, s) for s in SIZES]
    write_ico(OUT, images)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes, {len(SIZES)} sizes)")


if __name__ == "__main__":
    main()
