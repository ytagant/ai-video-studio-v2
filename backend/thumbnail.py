"""Clickbait thumbnail generator: grabs a frame ~30% into the finished video,
scales/crops to 1280x720 (or 720x1280), then overlays a subtle gradient,
an accent bar and a big bold title.

make_thumbnail(video_path, title, accent_color, dest, aspect="16:9") -> Path
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from graphics import _draw_line, _hex, _line_width, _wrap

GOLD = "#d4a017"


def _duration(path: Path) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            check=True, capture_output=True, text=True)
        return max(0.5, float(r.stdout.strip()))
    except Exception:
        return 5.0


def make_thumbnail(video_path: Path, title: str, accent_color: str = GOLD,
                   dest: Path = Path("thumbnail.jpg"),
                   aspect: str = "16:9") -> Path:
    video_path, dest = Path(video_path), Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    accent = _hex(accent_color)
    vertical = aspect == "9:16"
    TW, TH = (720, 1280) if vertical else (1280, 720)

    # --- frame at ~30% duration ---
    t = _duration(video_path) * 0.30
    base = dest.with_name(dest.stem + "_base.jpg")
    subprocess.run(
        ["ffmpeg", "-y", "-ss", f"{t:.2f}", "-i", str(video_path),
         "-frames:v", "1",
         "-vf", (f"scale={TW}:{TH}:force_original_aspect_ratio=increase,"
                 f"crop={TW}:{TH}"),
         "-q:v", "4", str(base)],
        check=True, capture_output=True, text=True)

    img = Image.open(base).convert("RGBA")
    W, H = img.size

    # --- subtle bottom gradient for text legibility ---
    grad_h = int(H * 0.52)
    grad = Image.new("L", (1, grad_h))
    for y in range(grad_h):
        grad.putpixel((0, y), int(60 + (200 - 60) * (y / max(1, grad_h - 1))))
    grad = grad.resize((W, grad_h))
    black = Image.new("RGBA", (W, grad_h), (0, 0, 0, 255))
    img.paste(black, (0, H - grad_h), grad)

    d = ImageDraw.Draw(img)
    fsize = 64 if vertical else 72
    max_w = W - 170
    lines = _wrap(d, title or "Untitled", fsize, True, max_w)
    # shrink until it fits 3 lines
    while len(_wrap(d, title or "Untitled", fsize, True, max_w)) > 3 and fsize > 40:
        fsize -= 4
    lines = _wrap(d, title or "Untitled", fsize, True, max_w)[:3]

    adv = fsize + 14
    block_h = adv * len(lines)
    tx = 92
    ty = H - grad_h + (grad_h - block_h) / 2 + 10

    # accent bar left of the title block
    d.rounded_rectangle([tx - 34, ty - 6, tx - 34 + 12, ty + block_h + 6],
                        radius=6, fill=accent + (255,))

    for line in lines:
        _draw_line(d, tx, ty, line, fsize, True,
                   stroke_width=3, stroke_fill=(0, 0, 0, 255))
        ty += adv

    img.convert("RGB").save(dest, quality=88)
    try:
        base.unlink()
    except OSError:
        pass
    return dest
