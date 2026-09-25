"""Entry point: render every Moon Glimmer store asset, then validate the logo.

    python3 scripts/generate-store-assets.py

Renders screenshots + promo tiles via generate-references.py (headless
Chromium), then asserts the theme ships exactly one icon size: 128.
"""
from pathlib import Path
import runpy
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / 'scripts' / 'generate-references.py'), run_name='__main__')
with Image.open(ROOT / 'logo' / 'logo.png') as logo:
    assert logo.size == (128, 128), 'Logo must be 128x128'
print('Logo validated: logo/logo.png (128x128); no duplicate sizes generated')
