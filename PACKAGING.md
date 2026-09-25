# Packaging

The store package is just the theme body: `manifest.json`, `logo/logo.png`,
`README.md` and `LICENSE`, with `manifest.json` at the archive root. Screenshots,
promo tiles and store copy are uploaded separately in the Chrome Web Store form
and are deliberately left out of the zip.

```
python3 scripts/package.py
```

Writes `dist/moon-glimmer-theme-<version>.zip` and copies the same bytes to
`..\..\moon-glimmer-theme-<version>.zip` (the shared upload folder) so the file
is ready to drag into the store form.

The script self-checks before it reports success:

1. `manifest_version` is 3 and `version` equals the value read from the manifest.
2. every path referenced by `icons` (and `theme.images`, if present) exists.
3. `manifest.json` sits at the zip root, not inside a folder.
4. the manifest is re-read from the zip and compared with the working copy.
5. the copy in the upload folder is byte-identical to the zip.

Keep `version` at `1.0.0` for the first store upload; only bump it once the
previous version is published. Run `python3 scripts/generate-store-assets.py`
before packaging when the palette or the logo changed, so the store artwork
matches the shipped theme.
