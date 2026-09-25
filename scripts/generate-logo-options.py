#!/usr/bin/env python3
"""Moon Glimmer Theme - LIGHT-background logo candidates (code-drawn, PIL).

Six 128x128 squircle icons on light lilac backgrounds, written to
store-assets/icon-candidates/, plus a preview sheet showing every candidate at
128 / 48 / 32 / 16 px (the small strip is drawn on the theme's real toolbar
colour so legibility can be judged in context).

Palette from manifest.json:
    frame_inactive rgb(240,233,251) / toolbar rgb(215,204,234)
    tab_text       rgb(66,60,83)    / ntp_link rgb(77,77,148)

Run from the project root (PIL only ever sees relative paths):
    python3 scripts/generate-logo-options.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 512          # internal design canvas (supersampled 4x)
OUT = 128        # exported icon size

# ---------------------------------------------------------------- palette --
LILAC_TOP = (250, 249, 255)   # near-white
LILAC_BOT = (227, 219, 243)   # soft lilac, kept lighter than the toolbar
NIGHT = (48, 43, 70)          # tab_text deepened
INDIGO = (77, 77, 148)        # ntp_link
VIOLET = (140, 124, 196)
SILVER = (247, 246, 254)
MOON = (252, 251, 255)
MOON_SHADE = (223, 216, 241)
WHITE = (255, 255, 255)
CLOUD_SOFT = (238, 233, 249)

CAND_DIR = os.path.join("store-assets", "icon-candidates")
LOGO_DIR = "logo"               # shipped icon folder (Chrome themes need 128 only)

# Candidate promoted to the live icon (logo/logo.png). Change this one line to
# switch direction; everything else is regenerated from scratch.
PICK = "light-04-minimal-phase.png"


# ---------------------------------------------------------------- helpers --
def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def new_canvas():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def bg_gradient(top, bot, radius_ratio=0.225):
    """Rounded-square (squircle) background filled with a soft vertical gradient."""
    strip = Image.new("RGB", (1, S))
    for y in range(S):
        strip.putpixel((0, y), tuple(int(v) for v in lerp(top, bot, y / (S - 1))))
    grad = strip.resize((S, S)).convert("RGBA")
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, S - 1, S - 1], radius=int(radius_ratio * S), fill=255)
    art = new_canvas()
    art.paste(grad, (0, 0), mask)
    return art


def _stamp(art, mask, color, alpha):
    layer = Image.new("RGBA", (S, S), color + (0,))
    layer.putalpha(mask.point(lambda v: int(v * alpha)))
    art.alpha_composite(layer)


def halo(art, cx, cy, rx, ry, color, alpha, blur):
    """Soft blurred ellipse - glow, cloud band or water shimmer."""
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    _stamp(art, m.filter(ImageFilter.GaussianBlur(blur)), color, alpha)


def disc(art, cx, cy, r, color):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    _stamp(art, m, color, 1.0)


def crescent_mask(cx, cy, r, ox, oy=0.0):
    """Big circle minus an offset circle => classic crescent."""
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    d.ellipse([cx - r + ox, cy - r + oy, cx + r + ox, cy + r + oy], fill=0)
    return m


def sparkle(art, cx, cy, r, color, waist=0.26):
    """Four-point glimmer star."""
    w = r * waist
    pts = [(cx, cy - r), (cx + w, cy - w), (cx + r, cy), (cx + w, cy + w),
           (cx, cy + r), (cx - w, cy + w), (cx - r, cy), (cx - w, cy - w)]
    layer = new_canvas()
    ImageDraw.Draw(layer).polygon(pts, fill=color + (255,))
    art.alpha_composite(layer)


def ring(art, cx, cy, rx, ry, angle, width, color, alpha):
    pad = int(max(rx, ry) * 2 + width * 6 + 40)
    m = Image.new("L", (pad, pad), 0)
    kx = (pad - 2 * rx) / 2.0
    ky = (pad - 2 * ry) / 2.0
    ImageDraw.Draw(m).ellipse([kx, ky, pad - kx, pad - ky],
                              outline=255, width=width)
    if angle:
        m = m.rotate(angle, resample=Image.BICUBIC)
    m = m.filter(ImageFilter.GaussianBlur(max(0.6, width * 0.30)))
    layer = Image.new("RGBA", (pad, pad), color + (0,))
    layer.putalpha(m.point(lambda v: int(v * alpha)))
    art.alpha_composite(layer, (int(cx - pad / 2), int(cy - pad / 2)))


# --------------------------------------------------------------- variants --
def v1_crescent_glow():
    """A - vivid indigo crescent with a soft white glimmer, two tiny stars."""
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    m = crescent_mask(S * 0.500, S * 0.500, S * 0.245, S * 0.104, -S * 0.012)
    _stamp(art, m.filter(ImageFilter.GaussianBlur(S * 0.055)), WHITE, 0.95)
    _stamp(art, m, INDIGO, 1.0)
    sparkle(art, S * 0.245, S * 0.270, S * 0.055, VIOLET)
    sparkle(art, S * 0.775, S * 0.740, S * 0.038, VIOLET)
    return art


def v2_glimmer_ripple():
    """B - indigo crescent above three shimmering water lines."""
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    m = crescent_mask(S * 0.500, S * 0.415, S * 0.245, S * 0.104, -S * 0.010)
    _stamp(art, m.filter(ImageFilter.GaussianBlur(S * 0.055)), WHITE, 0.95)
    _stamp(art, m, INDIGO, 1.0)
    for i, (w, a) in enumerate([(0.320, 0.62), (0.235, 0.48), (0.150, 0.34)]):
        halo(art, S * 0.500, S * (0.720 + 0.078 * i),
             S * w, S * 0.014, INDIGO, a, S * 0.009)
    return art


def v3_moon_clouds():
    """C - deep moon sinking behind a puffy white cloud bank."""
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    halo(art, S * 0.500, S * 0.372, S * 0.285, S * 0.285, WHITE, 0.85, S * 0.085)
    disc(art, S * 0.500, S * 0.372, S * 0.198, NIGHT)
    halo(art, S * 0.432, S * 0.318, S * 0.048, S * 0.048, (94, 86, 126), 0.55, S * 0.013)
    halo(art, S * 0.562, S * 0.404, S * 0.034, S * 0.034, (94, 86, 126), 0.45, S * 0.012)
    # cloud bank: three soft puffs then the main band
    halo(art, S * 0.300, S * 0.505, S * 0.056, S * 0.052, WHITE, 1.0, S * 0.009)
    halo(art, S * 0.665, S * 0.492, S * 0.048, S * 0.046, WHITE, 1.0, S * 0.009)
    halo(art, S * 0.500, S * 0.487, S * 0.066, S * 0.060, WHITE, 1.0, S * 0.010)
    halo(art, S * 0.480, S * 0.548, S * 0.330, S * 0.056, WHITE, 1.0, S * 0.012)
    halo(art, S * 0.615, S * 0.632, S * 0.240, S * 0.044, CLOUD_SOFT, 1.0, S * 0.011)
    sparkle(art, S * 0.790, S * 0.225, S * 0.040, VIOLET)
    sparkle(art, S * 0.215, S * 0.300, S * 0.027, VIOLET)
    return art


def v4_minimal_phase():
    """D - bold two-tone moon phase disc; the clearest shape at 16 px."""
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    halo(art, S * 0.500, S * 0.500, S * 0.340, S * 0.340, WHITE, 0.80, S * 0.080)
    r = S * 0.285
    disc(art, S * 0.500, S * 0.500, r, INDIGO)
    m = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([S * 0.500 - r, S * 0.500 - r, S * 0.500 + r, S * 0.500 + r], fill=255)
    ccx = S * 0.500 + 0.58 * r
    d.ellipse([ccx - 0.78 * r, S * 0.500 - 1.02 * r,
               ccx + 0.78 * r, S * 0.500 + 1.02 * r], fill=0)
    _stamp(art, m, VIOLET, 1.0)
    sparkle(art, S * 0.790, S * 0.245, S * 0.040, VIOLET)
    return art


def v5_lunar_orbit():
    """E - indigo moon sitting between two tilted, elliptical orbit rings."""
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    ring(art, S * 0.500, S * 0.500, S * 0.360, S * 0.300, -18,
         int(S * 0.010), INDIGO, 0.34)
    ring(art, S * 0.500, S * 0.500, S * 0.430, S * 0.360, 20,
         int(S * 0.006), VIOLET, 0.42)
    disc(art, S * 0.500, S * 0.500, S * 0.190, INDIGO)
    halo(art, S * 0.436, S * 0.432, S * 0.034, S * 0.034, MOON, 0.34, S * 0.017)
    halo(art, S * 0.285, S * 0.755, S * 0.028, S * 0.028, WHITE, 1.0, S * 0.014)
    disc(art, S * 0.285, S * 0.755, S * 0.016, VIOLET)
    return art


def v6_moonshine_rays():
    """F - indigo crescent ringed by eight short glimmer rays."""
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    m = crescent_mask(S * 0.500, S * 0.500, S * 0.205, S * 0.088, -S * 0.010)
    _stamp(art, m.filter(ImageFilter.GaussianBlur(S * 0.050)), WHITE, 0.95)
    _stamp(art, m, INDIGO, 1.0)

    rays = Image.new("L", (S, S), 0)
    rd = ImageDraw.Draw(rays)
    for i in range(8):
        ang = math.radians(i * 45 + 22.5)
        r0 = S * (0.315 if i % 2 == 0 else 0.325)
        r1 = S * (0.445 if i % 2 == 0 else 0.412)
        rd.line([S * 0.5 + math.cos(ang) * r0, S * 0.5 + math.sin(ang) * r0,
                 S * 0.5 + math.cos(ang) * r1, S * 0.5 + math.sin(ang) * r1],
                fill=255, width=int(S * 0.014))
    _stamp(art, rays.filter(ImageFilter.GaussianBlur(S * 0.007)), INDIGO, 0.50)
    return art


def v7_full_moon_halo():
    """G - full moon with two glimmer rings, light counterpart of the dark B.

    Value structure is inverted for a light tile: the moon becomes a solid
    indigo disc (craters in violet, lighter than the disc) and the halo/rings
    become white glow + faint indigo circles.
    """
    art = bg_gradient(LILAC_TOP, LILAC_BOT)
    halo(art, S * 0.500, S * 0.500, S * 0.380, S * 0.380, WHITE, 0.95, S * 0.130)
    halo(art, S * 0.500, S * 0.500, S * 0.260, S * 0.260, VIOLET, 0.22, S * 0.080)
    ring(art, S * 0.500, S * 0.500, S * 0.335, S * 0.335, 0,
         int(S * 0.009), INDIGO, 0.34)
    ring(art, S * 0.500, S * 0.500, S * 0.415, S * 0.415, 0,
         int(S * 0.005), INDIGO, 0.17)
    disc(art, S * 0.500, S * 0.500, S * 0.205, INDIGO)
    halo(art, S * 0.440, S * 0.450, S * 0.048, S * 0.048, VIOLET, 0.60, S * 0.013)
    halo(art, S * 0.550, S * 0.560, S * 0.034, S * 0.034, VIOLET, 0.48, S * 0.012)
    halo(art, S * 0.490, S * 0.605, S * 0.026, S * 0.026, VIOLET, 0.40, S * 0.011)
    halo(art, S * 0.408, S * 0.418, S * 0.026, S * 0.026, MOON, 0.30, S * 0.011)
    return art


VARIANTS = [
    ("light-01-crescent-glow.png",    "A - Crescent Glow",  v1_crescent_glow),
    ("light-02-glimmer-ripple.png",   "B - Glimmer Ripple", v2_glimmer_ripple),
    ("light-03-moon-clouds.png",      "C - Moon & Clouds",  v3_moon_clouds),
    ("light-04-minimal-phase.png",    "D - Minimal Phase",  v4_minimal_phase),
    ("light-05-lunar-orbit.png",      "E - Lunar Orbit",    v5_lunar_orbit),
    ("light-06-moonshine-rays.png",   "F - Moonshine Rays", v6_moonshine_rays),
    ("light-07-full-moon-halo.png",   "G - Full Moon Halo", v7_full_moon_halo),
]


# ---------------------------------------------------------- preview sheet --
MARGIN = 44
CELL_W = 220
GAP = 26
CHIP_H = 56
CHIP_BG = (215, 204, 234)      # the theme's real toolbar colour
SHEET_BG = (250, 250, 253)


def load_font(size, bold=False):
    name = "msyhbd.ttc" if bold else "msyh.ttc"
    for path in [os.path.join(r"C:\Windows\Fonts", name),
                 r"C:\Windows\Fonts\msyh.ttc",
                 r"C:\Windows\Fonts\arialbd.ttf",
                 r"C:\Windows\Fonts\arial.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def preview_sheet(entries, title, out_path):
    n = len(entries)
    W = MARGIN * 2 + n * CELL_W + (n - 1) * GAP
    RIGHT = W - MARGIN
    cell_h = OUT + 12 + 24 + 14 + CHIP_H
    H = MARGIN + 52 + 16 + cell_h + MARGIN

    sheet = Image.new("RGBA", (W, H), SHEET_BG + (255,))
    d = ImageDraw.Draw(sheet)
    f_title = load_font(26, bold=True)
    f_label = load_font(17)
    d.text((MARGIN, MARGIN), title, fill=NIGHT, font=f_title)
    d.line([MARGIN, MARGIN + 40, RIGHT, MARGIN + 40],
           fill=(222, 215, 240), width=2)

    top = MARGIN + 52 + 16
    sizes = [16, 32, 48]
    for i, (path, label) in enumerate(entries):
        x = MARGIN + i * (CELL_W + GAP)
        assert x + CELL_W <= RIGHT, "cell overflows the right baseline"

        icon = Image.open(path).convert("RGBA")
        sheet.alpha_composite(icon, (x, top))

        bb = d.textbbox((0, 0), label, font=f_label)
        d.text((x + (CELL_W - (bb[2] - bb[0])) // 2, top + OUT + 12),
               label, fill=NIGHT, font=f_label)

        chip_y = top + OUT + 12 + 24 + 14
        d.rounded_rectangle([x, chip_y, x + CELL_W, chip_y + CHIP_H],
                            radius=14, fill=CHIP_BG + (255,))
        strip_w = sum(sizes) + 16 * (len(sizes) - 1)
        sx = x + (CELL_W - strip_w) // 2
        for s in sizes:
            sheet.alpha_composite(icon.resize((s, s), Image.LANCZOS),
                                  (sx, chip_y + (CHIP_H - s) // 2))
            sx += s + 16

    assert top + cell_h <= H - MARGIN, "sheet content overflows the bottom margin"
    sheet.save(out_path)
    print("wrote", out_path)


# ------------------------------------------------------------------- main --
def main():
    os.makedirs(CAND_DIR, exist_ok=True)
    entries = []
    for name, label, fn in VARIANTS:
        icon = fn().resize((OUT, OUT), Image.LANCZOS)
        path = os.path.join(CAND_DIR, name)
        icon.save(path)
        entries.append((path, label))
        print("wrote", path)
        if name == PICK:
            logo_path = os.path.join(LOGO_DIR, "logo.png")
            os.makedirs(LOGO_DIR, exist_ok=True)
            icon.save(logo_path)
            print("wrote", logo_path)

    preview_sheet(entries, "Moon Glimmer - Light Logo Candidates",
                  os.path.join(CAND_DIR, "preview-all.png"))


if __name__ == "__main__":
    main()
