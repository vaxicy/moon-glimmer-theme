#!/usr/bin/env python3
"""Copy the real browser capture in and sample the colours we must calibrate.

Chrome paints several new-tab elements itself (Google mark, search pill,
shortcut tiles, Customize pill). Those tones are taken from the real capture
instead of being derived from the theme palette, per
chrome-theme-screenshot-ui-color-from-real-browser.

Run from the project root:
    python3 scripts/sample-reference.py
"""

import os
import shutil
from collections import Counter

from PIL import Image

SOURCE = (r"C:\Users\16704\AppData\Local\CodeBuddyExtension\Data"
          r"\29778d92-91e1-4369-8953-0334b572f040\VSCode"
          r"\29778d92-91e1-4369-8953-0334b572f040\history"
          r"\39f900b35f456c64c11ed818b125875a"
          r"\5a7d44da732748aba197c3b3393c0f72\assets\image.82fded83af.png")
DEST = os.path.join("store-assets", "references", "browser-real.png")


def hx(rgb):
    return "#%02X%02X%02X" % tuple(rgb[:3])


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def box_report(img, name, box, skip=None, n=4):
    crop = img.crop(box).convert("RGB")
    px = [p for p in crop.getdata() if p != skip] if skip else list(crop.getdata())
    counts = Counter(px)
    common = ", ".join(f"{hx(c)}x{k}" for c, k in counts.most_common(n))
    print(f"  {name:24s} common: {common}")
    print(f"  {'':24s} darkest {hx(min(px, key=lum))}   lightest {hx(max(px, key=lum))}")


def vscan(img, x, y0, y1):
    print(f"  vertical x={x}:")
    last = None
    for y in range(y0, y1):
        c = hx(img.getpixel((x, y)))
        if c != last:
            print(f"     y={y:4d} {c}")
            last = c


def main():
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    img = Image.open(DEST).convert("RGB")
    print(f"reference: {DEST}  size {img.size}")

    print("\ntab bodies (5 tabs, centres ~116/292/467/642/817), new-tab ~915:")
    for x in (116, 292, 467, 642, 817, 915):
        print(f"  x={x:3d}: " + "  ".join(
            f"y{y}={hx(img.getpixel((x, y)))}" for y in (3, 8, 14, 20, 26, 30)))

    print("\nsearch pill borders:")
    vscan(img, 400, 266, 292)
    vscan(img, 400, 312, 334)

    print("\nregion samples:")
    box_report(img, "pill placeholder", (296, 292, 600, 310), skip=(255, 255, 255))
    box_report(img, "mic glyph", (735, 290, 762, 312), skip=(255, 255, 255))
    box_report(img, "lens glyph", (770, 288, 800, 312), skip=(255, 255, 255))
    box_report(img, "shortcut labels", (490, 380, 600, 402), skip=(255, 255, 255))
    box_report(img, "images row", (980, 104, 1076, 140), skip=(255, 255, 255))
    box_report(img, "customize pill", (965, 600, 1074, 634))
    box_report(img, "toolbar icons", (14, 36, 200, 62), skip=(215, 204, 234))
    box_report(img, "omnibox row", (126, 32, 800, 64), skip=(254, 254, 254))
    box_report(img, "pill inner", (982, 612, 1058, 626), skip=(32, 33, 36), n=6)
    box_report(img, "pill icon only", (984, 612, 998, 626), skip=(32, 33, 36), n=6)
    box_report(img, "apps grid", (1038, 106, 1068, 136), skip=(255, 255, 255))
    box_report(img, "win glyphs", (975, 8, 1075, 28), skip=(228, 216, 252))
    box_report(img, "search magnifier", (282, 290, 302, 310), skip=(255, 255, 255))


if __name__ == "__main__":
    main()
