# Assets

Four English deliverables, all rendered from one headless-Chromium source
(`scripts/generate-references.py`):

| File | Size | Content |
|------|------|---------|
| `screenshots/en/screenshot-1-browser.png` | 1280x800 | Full-window mockup of the themed browser |
| `screenshots/en/screenshot-2-introduction.png` | 1280x800 | Theme intro with the 2x2 colour cards |
| `promo/440x280.png` | 440x280 | Brand tile |
| `promo/1400x560.png` | 1400x560 | Marquee with a scaled window preview |

## Calibration

The window mockup is authored in the pixel space of the real capture that sits in
`references/browser-real.png` (1080x645), so every coordinate in the composer can
be read straight off the capture. `screenshot-1` maps that space onto 1280x800
with a single `scale(1.185185, 1.240310)` transform; the other three sheets are
authored at their final size.

Theme-controlled surfaces (frame, tab strip, toolbar, bookmark bar, active tab,
omnibox, new tab page, text, links) are read from `manifest.json` at render time.
The page backdrop behind `screenshot-2` and the marquee is `mix(toolbar,
tab_text, 16%) = #BFB5D2`. That deeper lilac is derived from the theme (so the
sheets still feel native) but sits clearly below both light cards and clearly
above the dark ones; tests showed `frame` or `ntp_background` based backdrops
merging into the `Moonlight Lilac` / `Soft Lilac` cards. The composer asserts the
backdrop never equals a swatch colour, and every text tone on it was checked for
contrast: `#423C53` on `#BFB5D2` is 5.4:1.

Elements Chrome paints itself are literals sampled from the real capture, because
this is a light palette and Chrome decides these tones:

| Element | Value | Note |
|---|---|---|
| Google mark on the new tab page | `#B3B3B3` | `ntp_logo_alternate` makes Chrome paint the wordmark in a single neutral tone derived from the new-tab background; it is not the four-colour brand logo |
| Tab bodies | `#D7CCEA` | In this theme the tab bodies read as the toolbar tone, against a `#E6DFF1` strip |
| Window-control corner of the tab strip | `#E4D8FC` | Chrome paints the strip behind the window buttons with the theme's `button_background`, not with the frame colour |
| Window glyphs | `#232127` | Dark glyphs on the light frame |
| Address bar outline | `#707F99` | Chrome's own outline on the lilac toolbar |
| New tab page background | `#FFFFFF` | The capture renders white here; `ntp_background` is `#F8F8F9` |
| `Images` link + apps grid | `#444746` | Chrome's standard light-surface tone |
| Search glyphs, shortcut labels, placeholder | `#5F6368` / `#66676C` | Chrome's light-surface neutrals; the Lens glyph keeps its brand colours |
| Shortcut tiles | `#F1F3F4`, add-shortcut glyph `#202124` | The round tiles are rendered by the page, not the theme |
| `Customize Chrome` pill | `#202124` / `#8AB4F8` | Rendered by the page, not the theme |

All mockup copy is English. The two shortcut labels are trimmed to `YouTube` and
`Web Store` so they fit the real 78px tile width without ellipsis.

## Logo

`logo/logo.png` is the single 128px icon a Chrome theme ships, exported from the
chosen concept in `store-assets/icon-candidates/` (`light-04-minimal-phase.png`):
a two-tone moon phase disc — violet lit limb against an indigo shadow — with one
small glimmer, on a soft lilac squircle. It lives in its own `logo/` folder so it
is easy to find when uploading, and `manifest.json` references only that file.

## Regenerating

    python3 scripts/generate-logo-options.py     # candidate sheet + logo/logo.png
    python3 scripts/generate-store-assets.py     # screenshots + promo tiles
    python3 scripts/sample-reference.py          # re-print the calibration samples

The composer renders all four assets in one pass; change the styling in the
script and re-run instead of editing a PNG.
