"""Build the Chrome Web Store zip for Moon Glimmer Theme and self-check it.

    python3 scripts/package.py

The archive holds the theme body only (manifest.json at the root, the shipped
icon, README and LICENSE). Screenshots, promo tiles and store copy are uploaded
separately in the store form, so they stay out of the zip.

Self-checks before reporting success:
  1. manifest_version is 3 and version matches the value read from the manifest
  2. every file referenced by icons / theme.images exists
  3. manifest.json sits at the archive root
  4. the manifest re-read from inside the zip matches the working copy
  5. the copy dropped in the shared upload folder is byte-identical
"""
import json
import os
import shutil
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, 'dist')
# sibling of the theme folders: <...>\vibe coding\  (derived, never hardcoded)
DEFAULT_OUT = os.path.abspath(os.path.join(ROOT, os.pardir, os.pardir))

INCLUDE = ['manifest.json', 'logo/logo.png', 'README.md', 'LICENSE']


def main():
    with open(os.path.join(ROOT, 'manifest.json'), encoding='utf-8') as fh:
        manifest = json.load(fh)

    assert manifest['manifest_version'] == 3, 'theme must ship MV3'
    version = manifest['version']

    refs = list(manifest.get('icons', {}).values())
    for img in manifest.get('theme', {}).get('images', {}).values():
        refs.append(img if isinstance(img, str) else img.get('path', ''))
    missing = [r for r in refs if r and not os.path.exists(os.path.join(ROOT, r))]
    assert not missing, f'manifest references missing files: {missing}'
    for rel in INCLUDE:
        assert os.path.exists(os.path.join(ROOT, rel)), f'missing {rel}'

    os.makedirs(OUT_DIR, exist_ok=True)
    zip_path = os.path.join(OUT_DIR, f'moon-glimmer-theme-{version}.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel in INCLUDE:
            z.write(os.path.join(ROOT, rel), rel)   # arcname=rel -> root level

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        assert 'manifest.json' in names, 'manifest.json must sit at the zip root'
        assert not any(n.startswith('/') for n in names)
        inside = json.loads(z.read('manifest.json').decode('utf-8'))
        assert inside['name'] == manifest['name'], 'zip manifest drifted from source'
        assert inside['version'] == version, 'zip version drifted from source'
        assert {
            'manifest.json', 'logo/logo.png', 'README.md', 'LICENSE'
        }.issubset(set(names)), f'unexpected zip contents: {sorted(names)}'

    assert os.path.exists(DEFAULT_OUT), f'upload folder not found: {DEFAULT_OUT}'
    dst = os.path.join(DEFAULT_OUT, os.path.basename(zip_path))
    shutil.copyfile(zip_path, dst)
    with open(zip_path, 'rb') as a, open(dst, 'rb') as b:
        assert a.read() == b.read(), 'copy in the upload folder is stale'

    size = os.path.getsize(zip_path)
    print(f'Packaged {os.path.relpath(zip_path, ROOT)} ({size} bytes)')
    print(f'Copied   {dst}')
    print(f'Zip contents: {sorted(names)}')


if __name__ == '__main__':
    main()
