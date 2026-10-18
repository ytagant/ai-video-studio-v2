"""PIL-based documentary overlay PNG generators.

title_card / lower_third / fact_card — all render full-frame PNGs at any
WxH (1280x720 and 720x1280 supported) so ffmpeg can composite them with a
plain ``overlay=0:0`` (no position math in the filter chain).

Fonts: no single font on the box covers both Latin and Urdu glyphs, so
text is drawn word-by-word with per-word font fallback (DejaVu Sans for
Latin, Noto Sans Arabic / Naskh / Kufi for Arabic script). Urdu/Arabic
shaping: if ``arabic_reshaper`` + ``python-bidi`` are installed they are
used automatically for correct letter shaping and RTL order; otherwise
words render in logical order (documented limitation, still legible).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

GOLD = "#d4a017"

_FONT_DIRS = [
    "/usr/share/fonts/truetype/noto",
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/opentype/noto",
]

# family -> bold -> candidate filenames (first existing file wins)
_FONT_CANDIDATES = {
    "latin": {
        True: ["DejaVuSans-Bold.ttf", "NotoSansArabic-Bold.ttf"],
        False: ["DejaVuSans.ttf", "NotoSansArabic-Regular.ttf"],
    },
    "arabic": {
        True: ["NotoSansArabic-Bold.ttf", "NotoNaskhArabic-Bold.ttf",
               "NotoKufiArabic-Bold.ttf", "DejaVuSans-Bold.ttf"],
        False: ["NotoSansArabic-Regular.ttf", "NotoNaskhArabic-Regular.ttf",
                "NotoKufiArabic-Regular.ttf", "DejaVuSans.ttf"],
    },
}

_ARABIC_RANGES = [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF),
                  (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)]

_FCACHE: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}


def _find_font_file(family: str, bold: bool) -> Optional[str]:
    for name in _FONT_CANDIDATES[family][bold]:
        for d in _FONT_DIRS:
            p = Path(d) / name
            if p.exists():
                return str(p)
    for d in _FONT_DIRS:  # last resort: any plausible file
        dd = Path(d)
        if dd.exists():
            for pat in ("*.ttf", "*.otf"):
                hits = sorted(dd.glob(pat))
                if hits:
                    return str(hits[0])
    return None


def _has_arabic(text: str) -> bool:
    return any(any(lo <= ord(c) <= hi for lo, hi in _ARABIC_RANGES)
               for c in text)


def _shape(text: str) -> str:
    """Reshape Arabic-script text for PIL when the shaping libs exist."""
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def _font_for(text: str, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    family = "arabic" if _has_arabic(_shape(text)) else "latin"
    path = _find_font_file(family, bold)
    key = (path or "default", size)
    if key not in _FCACHE:
        if path:
            try:
                _FCACHE[key] = ImageFont.truetype(path, size)
            except Exception:
                _FCACHE[key] = ImageFont.load_default()
        else:
            _FCACHE[key] = ImageFont.load_default()
    return _FCACHE[key]


def _line_width(draw: ImageDraw.ImageDraw, line: str, size: int,
                bold: bool = True) -> float:
    words = _shape(line).split(" ")
    total, sp = 0.0, None
    for i, wd in enumerate(words):
        f = _font_for(wd or " ", size, bold)
        total += draw.textlength(wd, font=f)
        if i < len(words) - 1:
            if sp is None:
                sp = draw.textlength(" ", font=f)
            total += sp
    return total


def _draw_line(draw: ImageDraw.ImageDraw, x: float, y: float, line: str,
               size: int, bold: bool = True,
               fill: Tuple[int, int, int, int] = (255, 255, 255, 255),
               stroke_width: int = 0,
               stroke_fill: Tuple[int, int, int, int] = (0, 0, 0, 255)) -> float:
    """Draw one (possibly mixed-script) line; returns x past the line end."""
    words = _shape(line).split(" ")
    for i, wd in enumerate(words):
        f = _font_for(wd or " ", size, bold)
        kw = {"stroke_width": stroke_width, "stroke_fill": stroke_fill} \
            if stroke_width else {}
        draw.text((x, y), wd, font=f, fill=fill, **kw)
        x += draw.textlength(wd, font=f)
        if i < len(words) - 1:
            x += draw.textlength(" ", font=f)
    return x


def _wrap(draw: ImageDraw.ImageDraw, text: str, size: int, bold: bool,
          max_w: int) -> List[str]:
    lines, cur = [], ""
    for word in (text or "").split():
        trial = (cur + " " + word).strip()
        if _line_width(draw, trial, size, bold) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines or [""]


def _hex(color: str) -> Tuple[int, int, int]:
    c = (color or GOLD).strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    try:
        return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    except Exception:
        return (212, 160, 23)


def _vertical_gradient(w: int, h: int,
                       top: Tuple[int, int, int],
                       bottom: Tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


# ---------------------------------------------------------------- title card

def title_card(title: str, subtitle: str = "", accent_color: str = GOLD,
               W: int = 1280, H: int = 720, dest: Optional[Path] = None) -> Path:
    """Full-frame elegant title card PNG (opaque). Returns dest path."""
    dest = Path(dest) if dest else Path(f"title_card_{W}x{H}.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    accent = _hex(accent_color)

    img = _vertical_gradient(W, H, (11, 17, 34), (30, 41, 59)).convert("RGBA")
    d = ImageDraw.Draw(img)

    # accent rule across the top
    d.rectangle([0, 0, W, max(6, H // 120)], fill=accent + (255,))

    title_size = max(44, W // 12)
    sub_size = max(22, W // 30)
    max_w = W - 160
    t_lines = _wrap(d, title, title_size, True, max_w)[:3]
    s_lines = _wrap(d, subtitle, sub_size, False, max_w)[:2]

    t_adv, s_adv = int(title_size * 1.28), int(sub_size * 1.4)
    block_h = len(t_lines) * t_adv + int(title_size * 0.5) + len(s_lines) * s_adv
    y = (H - block_h) / 2

    for line in t_lines:
        tw = _line_width(d, line, title_size, True)
        _draw_line(d, (W - tw) / 2, y, line, title_size, True)
        y += t_adv

    # accent underline under the title block
    uw = min(max_w, max(_line_width(d, l, title_size, True) for l in t_lines))
    uy = y - int(title_size * 0.22)  # just below descenders, not through them
    d.rectangle([(W - uw) / 2, uy, (W + uw) / 2, uy + 5], fill=accent + (255,))
    y += int(title_size * 0.5)

    for line in s_lines:
        tw = _line_width(d, line, sub_size, False)
        _draw_line(d, (W - tw) / 2, y, line, sub_size, False,
                   fill=(203, 213, 225, 255))
        y += s_adv

    img.convert("RGB").save(dest)
    return dest


# --------------------------------------------------------------- lower third

def lower_third(text: str, accent_color: str = GOLD,
                W: int = 1280, H: int = 720,
                dest: Optional[Path] = None) -> Path:
    """Transparent full-frame PNG with a name/topic strap near the bottom,
    positioned above the subtitle safe-zone (MarginV 40 @16:9, 260 @9:16)."""
    dest = Path(dest) if dest else Path(f"lower_third_{W}x{H}.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    accent = _hex(accent_color)
    vertical = W < H

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    margin = 40 if vertical else 48
    bar_h = 150 if vertical else 110
    bottom_gap = 360 if vertical else 110   # clear of burned subtitles
    x0, x1 = margin, W - margin
    y1 = H - bottom_gap
    y0 = y1 - bar_h

    d.rounded_rectangle([x0, y0, x1, y1], radius=18, fill=(10, 18, 32, 232))
    d.rounded_rectangle([x0, y0, x0 + 10, y1], radius=5, fill=accent + (255,))

    fsize = 38 if vertical else 34
    lines = _wrap(d, text, fsize, True, (x1 - x0) - 90)[:2]
    adv = fsize + 12
    ty = y0 + (bar_h - adv * len(lines)) / 2
    for line in lines:
        _draw_line(d, x0 + 44, ty, line, fsize, True)
        ty += adv

    img.save(dest)
    return dest


# ---------------------------------------------------------------- fact card

def fact_card(text: str, accent_color: str = GOLD,
              W: int = 1280, H: int = 720,
              dest: Optional[Path] = None) -> Path:
    """Transparent full-frame PNG with a centered fact callout box."""
    dest = Path(dest) if dest else Path(f"fact_card_{W}x{H}.png")
    dest.parent.mkdir(parents=True, exist_ok=True)
    accent = _hex(accent_color)
    vertical = W < H

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    box_w = min(W - 120, 560 if vertical else 680)
    kick_size = 26 if vertical else 24
    fsize = 40 if vertical else 36
    adv = fsize + 14
    lines = _wrap(d, text, fsize, True, box_w - 80)[:4]

    pad = 36
    box_h = pad + 44 + adv * len(lines) + pad - 12
    x0 = (W - box_w) / 2
    y0 = H * (0.28 if vertical else 0.30) - box_h / 2

    # soft drop shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.rounded_rectangle([x0 + 8, y0 + 10, x0 + box_w + 8, y0 + box_h + 10],
                         radius=20, fill=(0, 0, 0, 110))
    img = Image.alpha_composite(img, sh)
    d = ImageDraw.Draw(img)

    d.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=20,
                        fill=(10, 18, 32, 238))
    # accent top border
    d.rounded_rectangle([x0, y0, x0 + box_w, y0 + 22], radius=10,
                        fill=accent + (255,))
    d.rectangle([x0, y0 + 10, x0 + box_w, y0 + 22], fill=accent + (255,))

    _draw_line(d, x0 + 40, y0 + pad, "FACT", kick_size, True,
               fill=accent + (255,))
    ty = y0 + pad + 48
    for line in lines:
        tw = _line_width(d, line, fsize, True)
        _draw_line(d, (W - tw) / 2, ty, line, fsize, True)
        ty += adv

    img.save(dest)
    return dest
