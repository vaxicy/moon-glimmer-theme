"""Compose every Moon Glimmer store asset from one HTML/CSS source.

The window is authored in the pixel space of the real capture that ships in
store-assets/references/browser-real.png (1080x645) and mapped onto the store
size with a single transform, so every coordinate below can be read straight
off the capture.

  screenshot-1  1280x800  window scaled by (1280/1080, 800/645)
  screenshot-2  1280x800  intro sheet with the 2x2 colour cards
  promo         440x280 / 1400x560

Theme-controlled colours come from manifest.json (single source of truth).
Chrome-owned UI tones are calibrated against the real capture and listed in
store-assets/ASSET-NOTES.md.
"""
from pathlib import Path
import base64
import json
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'store-assets' / 'references'
OUT.mkdir(parents=True, exist_ok=True)
C = json.loads((ROOT / 'manifest.json').read_text('utf-8-sig'))['theme']['colors']

# capture space -> store space
CAP_W, CAP_H = 1080, 645
SX, SY = 1280 / CAP_W, 800 / CAP_H


def color(k):
    return '#%02X%02X%02X' % tuple(C[k])


def mix(a, b, t):
    ca, cb = C[a], C[b]
    return '#%02X%02X%02X' % tuple(
        int(round(ca[i] + (cb[i] - ca[i]) * t)) for i in range(3))


# ---------------------------------------------------------------------------
# Tones Chrome paints itself, sampled from the real capture (see ASSET-NOTES).
# ---------------------------------------------------------------------------
TAB_BODY = '#D7CCEA'         # tab bodies read as the toolbar tone in this theme
WCTRL_BG = '#E4D8FC'         # window-control corner of the tab strip
WCTRL_FG = '#232127'         # minimise / maximise / close glyphs
OMNI_BORDER = '#707F99'      # address bar outline on the lilac toolbar
NTP_BG = '#FFFFFF'           # new tab page reads white in the capture
LOGO_TINT = '#B3B3B3'        # ntp_logo_alternate paints a single neutral tone
PAGE_UI = '#444746'          # "Images" link + apps grid
LABEL_GREY = '#5F6368'       # search glyphs, shortcut labels, placeholder
PILL_BG = '#FFFFFF'
PILL_BORDER = '#E9E9EA'
TILE_BG = '#F1F3F4'          # shortcut tiles + add-shortcut tile
ADD_FG = '#202124'
CPILL_BG = '#202124'         # Customize Chrome pill
CPILL_FG = '#8AB4F8'
G_BLUE, G_RED, G_YELLOW, G_GREEN = '#4285F4', '#EA4335', '#FBBC05', '#34A853'

# palette cards: the four tones that actually carry the design
PALETTE = [
    ('Moonlight Lilac', 'frame', 'Window frame & tab strip', 'tab_text'),
    ('Soft Lilac', 'toolbar', 'Toolbar, bookmarks & active tab', 'tab_text'),
    ('Deep Violet', 'tab_text', 'Primary text & titles', 'ntp_background'),
    ('Midnight Indigo', 'ntp_link', 'Accent, links & active tab mark', 'ntp_background'),
]
BACKDROP = mix('toolbar', 'tab_text', 0.16)

assert all(color(k) != BACKDROP for _n, k, _r, _f in PALETTE), \
    'page backdrop must not equal a swatch colour'

VARS = f""":root{{
  --frame:{color('frame')};
  --bar:{color('toolbar')};
  --ntp:{NTP_BG};
  --ob:{color('omnibox_background')};
  --tabtx:{color('tab_text')};
  --tabtx2:{color('tab_background_text')};
  --bmtext:{color('bookmark_text')};
  --icon:{color('toolbar_button_icon')};
  --link:{color('ntp_link')};
  --ntptext:{color('ntp_text')};
  --tabbody:{TAB_BODY};
  --wctrl:{WCTRL_BG};
  --wctrlf:{WCTRL_FG};
  --omnib:{OMNI_BORDER};
  --logoc:{LOGO_TINT};
  --pageui:{PAGE_UI};
  --grey:{LABEL_GREY};
  --pillb:{PILL_BORDER};
  --tile:{TILE_BG};
  --addfg:{ADD_FG};
  --cpill:{CPILL_BG};
  --cpillf:{CPILL_FG};
  --backdrop:{BACKDROP};
}}"""

CSS = VARS + """
*{box-sizing:border-box}
body{margin:0;overflow:hidden;font-family:Arial,'Helvetica Neue',sans-serif;background:var(--backdrop);color:var(--ntptext)}
.stage{width:1280px;height:800px;overflow:hidden;position:relative;background:var(--ntp)}
.window{width:1080px;height:645px;background:var(--ntp);position:relative;overflow:hidden;
       display:flex;flex-direction:column;transform-origin:top left}
svg{display:block}

/* ---- tab strip ---- */
.tabstrip{height:31px;background:var(--frame);display:flex;align-items:flex-end;padding-left:39px;position:relative}
.chev{position:absolute;left:14px;top:11px}
.tab{width:156px;height:27px;border-radius:9px 9px 0 0;margin-right:20px;padding:0 10px 0 27px;
     display:flex;align-items:center;font-size:11.5px;color:var(--tabtx2);position:relative}
.tab.off{background:linear-gradient(var(--tabbody) 0 78%, var(--frame) 78% 100%)}
.tab.on{background:var(--tabbody);color:var(--tabtx)}
.tab i{position:absolute;left:10px;top:8px;width:12px;height:12px;line-height:0}
.tab .t{flex:1 1 auto;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tab .x{flex:0 0 auto;margin-left:5px}
.newtab{width:20px;height:20px;margin:0 0 4px 3px;display:flex;align-items:center;justify-content:center}
.wtools{position:absolute;right:0;top:0;width:107px;height:31px;background:var(--wctrl);
        display:flex;align-items:center;justify-content:flex-end;gap:25px;padding-right:14px}

/* ---- toolbar ---- */
.toolbar{height:33px;background:var(--bar);display:flex;align-items:center;gap:15px;padding:0 14px}
.nav{display:flex;gap:15px;align-items:center}
.omni{width:674px;height:27px;border:2px solid var(--omnib);border-radius:14px;background:var(--ob);
      display:flex;align-items:center;padding:0 8px 0 12px;gap:8px;font-size:12.5px;color:var(--ntptext)}
.omni .ph{flex:1;white-space:nowrap;overflow:hidden}
.tools{margin-left:auto;display:flex;gap:16px;align-items:center}
.avatar{width:19px;height:19px;border-radius:50%;background:var(--bar);
        border:1.5px solid var(--icon);display:flex;align-items:center;justify-content:center}

/* ---- bookmark bar ---- */
.bookmarks{height:30px;background:var(--bar);display:flex;align-items:center;gap:18px;padding:0 14px;
           font-size:11.5px;color:var(--bmtext)}
.bookmarks .sep{width:1px;height:14px;background:rgba(66,60,83,.22)}
.bm{display:flex;align-items:center;gap:6px;white-space:nowrap}

/* ---- new tab page ---- */
.ntp{flex:1;position:relative;background:var(--ntp)}
.gtop{position:absolute;top:17px;right:18px;display:flex;align-items:center;gap:17px;font-size:12.5px;color:var(--pageui)}
.glogo{position:absolute;top:99px;left:0;right:0;text-align:center;font-family:'Google Sans','Product Sans',Arial,sans-serif;
       font-size:66px;font-weight:500;letter-spacing:-2.8px;color:var(--logoc);line-height:1}
.nsearch{position:absolute;top:187px;left:50%;margin-left:-268px;width:536px;height:38px;border-radius:19px;
         background:var(--pillb);border:1px solid var(--pillb);box-shadow:0 1px 6px rgba(32,33,36,.16);
         display:flex;align-items:center;gap:18px;padding:0 16px 0 21px}
.nsearch .ph{flex:1;font-size:14px;color:#66676C;white-space:nowrap;overflow:hidden}
.shortcuts{position:absolute;top:247px;left:0;right:0;display:flex;justify-content:center;gap:47px}
.shortcut{width:78px;text-align:center;font-size:12.5px;color:var(--grey)}
.shortcut .circle{width:33px;height:33px;border-radius:50%;background:var(--tile);margin:0 auto 13px;
                  display:flex;align-items:center;justify-content:center}
.shortcut .lbl{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.customize{position:absolute;right:7px;bottom:13px;height:28px;border-radius:14px;background:var(--cpill);
           color:var(--cpillf);display:flex;align-items:center;gap:6px;padding:0 13px;font-size:11.5px}

/* ---- promo: 440x280 brand tile ---- */
.tile{width:440px;height:280px;background:var(--tabtx);position:relative;overflow:hidden;text-align:center;color:#F8F8F9}
.tile .glow{position:absolute;left:50%;top:-70px;width:360px;height:250px;margin-left:-180px;border-radius:50%;
            background:radial-gradient(closest-side,rgba(215,204,234,.34),rgba(215,204,234,0))}
.tile img{width:76px;height:76px;display:block;margin:26px auto 0;position:relative}
.tile h1{font-family:Georgia,serif;font-weight:normal;font-size:35px;margin:13px 0 0;position:relative}
.tile .kicker{font-size:12px;letter-spacing:5px;margin-top:7px;color:#C9BFE6;position:relative}
.tile p{font-size:13.5px;margin:15px 0 0;color:#C9BFE6;position:relative}
.tile:after{content:'';position:absolute;left:0;right:0;bottom:0;height:14px;background:var(--bar)}

/* ---- promo: 1400x560 marquee ---- */
.marquee{width:1400px;height:560px;background:var(--backdrop);position:relative;overflow:hidden;
         text-align:center;border-top:8px solid var(--link)}
.marquee h1{font-family:Georgia,serif;font-weight:normal;font-size:47px;margin:28px 0 0;color:var(--tabtx)}
.marquee p{font-size:17px;margin:10px 0 0;color:var(--tabtx)}
.marquee .frame{position:absolute;top:138px;left:300px;width:800px;height:374px;overflow:hidden;
                border:2px solid var(--link);border-radius:16px;
                box-shadow:0 0 0 1px rgba(66,60,83,.08),0 16px 44px rgba(66,60,83,.28)}
.marquee .frame .window{transform:scale(.740741)}

/* ---- screenshot 2: intro + palette cards ---- */
.intro{width:1280px;height:800px;background:var(--backdrop);padding:66px 74px}
.intro .kicker{font-size:12px;letter-spacing:4px;color:var(--tabtx)}
.intro h1{font-family:Georgia,serif;font-weight:normal;font-size:54px;margin:16px 0 0;color:var(--tabtx)}
.intro .lead{font-size:21px;margin:14px 0 0;color:var(--tabtx)}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:40px}
.card{height:212px;border-radius:18px;padding:32px;display:flex;flex-direction:column;justify-content:flex-end;
      box-shadow:0 2px 10px rgba(66,60,83,.10)}
.card strong{font-size:28px}
.card span{font-size:16.5px;margin-top:10px}
.intro .chips{font-size:16px;margin-top:30px;color:var(--tabtx)}
"""


# ------------------------------------------------------------------ glyphs --
def g_mark(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<circle cx="10" cy="10" r="6.4" fill="none" stroke="{fill}" stroke-width="2.2"/>'
            f'<path d="M15 15l5.6 5.6" stroke="{fill}" stroke-width="2.2" stroke-linecap="round"/></svg>')


def chevron(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<path d="M6 10l6 6 6-6" stroke="{fill}" stroke-width="2.4" fill="none" stroke-linecap="round"/></svg>')


def plus(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<path d="M12 5v14M5 12h14" stroke="{fill}" stroke-width="2.3" stroke-linecap="round"/></svg>')


def close_x(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<path d="M5 5l14 14M19 5L5 19" stroke="{fill}" stroke-width="1.9" stroke-linecap="round"/></svg>')


def mic(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<rect x="9" y="2.5" width="6" height="10.5" rx="3" fill="{fill}"/>'
            f'<path d="M5.5 11v1a6.5 6.5 0 0 0 13 0v-1" fill="none" stroke="{fill}" stroke-width="2"/>'
            f'<path d="M12 19v3.4" stroke="{fill}" stroke-width="2" stroke-linecap="round"/></svg>')


def lens(size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<rect x="2" y="2" width="20" height="20" rx="6" fill="#FFFFFF"/>'
            f'<path d="M4 10a8 8 0 0 1 16 0z" fill="{G_BLUE}"/>'
            f'<path d="M20 10a8 8 0 0 1-8 8z" fill="{G_RED}"/>'
            f'<path d="M12 18a8 8 0 0 1-8-8z" fill="{G_YELLOW}"/>'
            f'<circle cx="12" cy="10" r="3.1" fill="{G_GREEN}"/>'
            f'<circle cx="12" cy="10" r="1.3" fill="#FFFFFF"/></svg>')


def apps(size, fill):
    dots = ''.join(f'<circle cx="{3 + 9 * (i % 3)}" cy="{3 + 9 * (i // 3)}" r="2.6"/>' for i in range(9))
    return f'<svg width="{size}" height="{size}" viewBox="0 0 30 30" fill="{fill}">{dots}</svg>'


def pinwheel(size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<circle cx="12" cy="12" r="11" fill="#FFFFFF"/>'
            f'<path d="M12 1a11 11 0 0 1 9.53 5.5L12 12z" fill="{G_RED}"/>'
            f'<path d="M21.53 6.5A11 11 0 0 1 12 23L12 12z" fill="{G_GREEN}"/>'
            f'<path d="M12 23A11 11 0 0 1 2.47 17.5L12 12z" fill="{G_YELLOW}"/>'
            f'<circle cx="12" cy="12" r="5" fill="{G_BLUE}"/><circle cx="12" cy="12" r="2.1" fill="#FFFFFF"/></svg>')


def youtube(size):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<rect x="1" y="4.5" width="22" height="15" rx="4.5" fill="{G_RED}"/>'
            f'<path d="M9.6 8.4l6.4 3.6-6.4 3.6z" fill="#FFFFFF"/></svg>')


def swatch_square(size, fill):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<rect x="1.5" y="1.5" width="21" height="21" rx="6" fill="{fill}"/></svg>')


def folder(size=12):
    g = f'stroke="{color("bookmark_text")}" stroke-width="1.6" stroke-linejoin="round" fill="none"'
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24">'
            f'<path d="M3 7.5h6l2 2.5h10v8.5a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 18.5z" {g}/></svg>')


def win_buttons():
    g = f'stroke="{WCTRL_FG}" stroke-width="1.5" stroke-linecap="round" fill="none"'
    return ('<div class="wtools">'
            f'<svg width="10" height="10" viewBox="0 0 12 12"><path d="M1.2 6h9.6" {g}/></svg>'
            f'<svg width="10" height="10" viewBox="0 0 12 12"><rect x="1.8" y="1.8" width="8.4" height="8.4" rx="2" {g}/></svg>'
            f'<svg width="10" height="10" viewBox="0 0 12 12"><path d="M2.2 2.2l7.6 7.6M9.8 2.2L2.2 9.8" {g}/></svg>'
            '</div>')


def nav_icons():
    g = f'stroke="{color("toolbar_button_icon")}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" fill="none"'
    return ('<div class="nav">'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M15 5l-7 7 7 7" {g}/></svg>'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7" {g}/></svg>'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M20 12a8 8 0 1 1-2.6-5.9" {g}/><path d="M20 3.6V7h-3.4" {g}/></svg>'
            f'<svg width="16" height="16" viewBox="0 0 24 24"><path d="M4 11l8-7 8 7v8.5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z" {g}/></svg>'
            '</div>')


def tab(title, kind, active=False):
    cls = 'tab on' if active else 'tab off'
    return (f'<div class="{cls}"><i>{favicon(kind)}</i>'
            f'<span class="t">{title}</span>'
            f'<span class="x">{close_x(9, color("tab_background_text"))}</span></div>')


def favicon(kind, size=12):
    tint = {'yt': G_RED, 'themebake': '#6C4BB6', 'chrome': G_BLUE,
            'cal': G_GREEN, 'doc': '#B3B3B3'}[kind]
    return swatch_square(size, tint)


def bookmarks():
    kids = ''.join(f'<div class="bm">{folder()}{n}</div>'
                   for n in ('Tools', 'AI', 'UI', 'Nav', 'Temp', 'API', 'Dev'))
    return ('<div class="bookmarks">' + apps(13, color('bookmark_text'))
            + '<div class="sep"></div>' + kids + '</div>')


def window():
    tabs = (('Project overview', 'doc', False),
            ('(1) Excel for Data Analytics', 'cal', False),
            ('ThemeBake - Create your own', 'themebake', False),
            ('Extensions', 'chrome', False),
            ('New Tab', 'chrome', True))
    strip = ('<div class="tabstrip">'
             f'<div class="chev">{chevron(11, color("tab_text"))}</div>'
             + ''.join(tab(t, k, on) for t, k, on in tabs)
             + f'<div class="newtab">{plus(13, color("toolbar_button_icon"))}</div>'
             + win_buttons() + '</div>')
    omni = '<div class="omni">' + g_mark(14, LABEL_GREY) + '<span class="ph"></span></div>'
    star = (f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{color("toolbar_button_icon")}" '
            'stroke-width="1.6" stroke-linejoin="round"><path d="M12 3.6l2.5 5.6 6.1.5-4.6 4 1.4 6-5.4-3.2-5.4 3.2 1.4-6-4.6-4 6.1-.5z"/></svg>')
    puzzle = (f'<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="{color("toolbar_button_icon")}" '
              'stroke-width="1.6" stroke-linejoin="round"><path d="M10 4.6a2 2 0 1 1 4 0V6h3.4v3.4H19a2 2 0 1 1 0 4h-1.6V17H14v1.4a2 2 0 1 1-4 0V17H6.6v-3.6H5a2 2 0 1 1 0-4h1.6V6H10z"/></svg>')
    dots = ''.join(f'<circle cx="12" cy="{5 + 7 * i}" r="1.7" fill="{color("toolbar_button_icon")}"/>' for i in range(3))
    kebab = f'<svg width="15" height="15" viewBox="0 0 24 24">{dots}</svg>'
    avatar = f'<div class="avatar">{chevron(5, color("toolbar_button_icon"))}</div>'
    toolbar = ('<div class="toolbar">' + nav_icons() + omni
               + f'<div class="tools">{star}{puzzle}{kebab}{avatar}</div></div>')
    glogo = '<div class="glogo">Google</div>'
    nsearch = ('<div class="nsearch">' + g_mark(15, LABEL_GREY)
               + '<span class="ph">Search Google or type a URL</span>'
               + mic(17, LABEL_GREY) + lens(19) + '</div>')
    short = ('<div class="shortcuts">'
             f'<div class="shortcut"><div class="circle">{youtube(18)}</div><div class="lbl">YouTube</div></div>'
             f'<div class="shortcut"><div class="circle">{pinwheel(18)}</div><div class="lbl">Web Store</div></div>'
             f'<div class="shortcut"><div class="circle">{plus(16, ADD_FG)}</div><div class="lbl">Add shortcut</div></div>'
             '</div>')
    customize = ('<div class="customize">'
                 f'<svg width="12" height="12" viewBox="0 0 24 24"><path d="M4 20l4.2-1.1L20 7.1 16.9 4 5.1 15.8z" '
                 f'fill="none" stroke="{CPILL_FG}" stroke-width="2" stroke-linejoin="round"/></svg>'
                 'Customize Chrome</div>')
    ntp = (f'<div class="ntp"><div class="gtop"><span>Images</span>{apps(14, PAGE_UI)}</div>'
           f'{glogo}{nsearch}{short}{customize}</div>')
    return '<div class="window">' + strip + toolbar + bookmarks() + ntp + '</div>'


LOGO_URI = ('data:image/png;base64,'
            + base64.b64encode((ROOT / 'logo' / 'logo.png').read_bytes()).decode())

tile = ('<div class="tile"><div class="glow"></div>'
        f'<img src="{LOGO_URI}" alt="Moon Glimmer logo">'
        '<h1>Moon Glimmer</h1><div class="kicker">CHROME THEME</div>'
        '<p>Silvery lilac light for a calmer browser.</p></div>')

marquee = ('<div class="marquee"><h1>Moon Glimmer Theme</h1>'
           '<p>Soft lilac surfaces, deep violet text and one midnight indigo accent.</p>'
           '<div class="frame">' + window() + '</div></div>')

cards = ''.join(
    f'<div class="card" style="background:{color(k)};color:{color(fg)}">'
    f'<strong>{name}</strong><span>{color(k)} &middot; {role}</span></div>'
    for name, k, role, fg in PALETTE)
intro = ('<div class="intro"><div class="kicker">A MOONLIT LILAC PALETTE</div>'
         '<h1>Moon Glimmer Theme</h1>'
         '<p class="lead">Four solid tones: soft lilac surfaces, deep violet type, one indigo accent.</p>'
         '<div class="cards">' + cards + '</div>'
         '<p class="chips">Solid colors &middot; Minimal design &middot; Light interface &middot; Tuned for contrast</p></div>')


def page(body):
    return ('<!doctype html><html lang="en"><meta charset="utf-8"><style>'
            + CSS + '</style><body>' + body + '</body></html>')


# name, store size, capture-space size, body
JOBS = [
    ('screenshot-1-browser', 1280, 800, window()),
    ('screenshot-2-introduction', 1280, 800, intro),
    ('promo-440x280', 440, 280, tile),
    ('promo-1400x560', 1400, 560, marquee),
]

with sync_playwright() as p:
    engine = p.chromium.launch(headless=True)
    for name, w, h, body in JOBS:
        # screenshot-1 is authored in capture space (1080x645) and mapped onto
        # 1280x800; the other sheets are authored at their final size.
        if name == 'screenshot-1-browser':
            stage = (f'<div class="stage" style="width:{w}px;height:{h}px">'
                     f'<div style="transform:scale({SX},{SY});transform-origin:top left">'
                     + body + '</div></div>')
            design_w, design_h = w, h
        else:
            stage, design_w, design_h = body, w, h
        html = page(stage)
        (OUT / f'{name}.html').write_text(html, 'utf-8')
        sheet = engine.new_page(device_scale_factor=1,
                                viewport={'width': design_w, 'height': design_h})
        sheet.set_content(html)
        sheet.screenshot(path=str(OUT / f'{name}.png'))
        sheet.close()
        destination = ROOT / 'store-assets' / (
            'promo' if name.startswith('promo-') else 'screenshots/en') / (
            name.removeprefix('promo-') + '.png')
        destination.parent.mkdir(parents=True, exist_ok=True)
        temp = destination.with_suffix('.new.png')
        with Image.open(OUT / f'{name}.png') as img:
            out = img.convert('RGB')
            if out.size != (w, h):
                print(f'  resampling {name} {out.size} -> {(w, h)}')
                out = out.resize((w, h), Image.LANCZOS)
            assert out.size == (w, h), f'{name}: got {out.size}, expected {(w, h)}'
            out.save(temp)
        temp.replace(destination)
        print(f'Rendered {name} {w}x{h}')
    engine.close()
