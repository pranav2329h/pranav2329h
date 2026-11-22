#!/usr/bin/env python3
"""Generate the identity card: animated pixel-art portrait + neofetch facts.

Portrait loop (CYCLE seconds):
  1. 8-bit pixels pop in one by one          (pixel art, 24x30 grid, quantised palette)
  2. pixels burst away revealing 48x60 sprite (de-pixelation)
  3. sprite resolves into the real photo      (scan beam + HUD)
  4. RGB glitch slices
  5. photo dissolves into an ASCII rendering, then fades out and loops

The photo comes from data/avatar.jpg (create it with scripts/set_photo.py). Without
it, an animated monogram is shown instead. Live stats come from contributions.json.
"""
import base64
import io
import random

from contrib_stats import compute_stats
from theme import (AVATAR, MONO, SANS, THEMES, esc, load_json, load_profile, neon_gradient,
                   svg_open, window_chrome, write_svg)

W, H = 1200, 540
PX, PY, PW, PH = 40, 76, 336, 420          # photo frame (4:5)
ROW_X, VAL_X, ROW_Y0, ROW_STEP = 430, 570, 150, 28
GRID_C, GRID_R = 24, 30                     # pop-in pixel grid (14px cells)
SPRITE_C, SPRITE_R = 48, 60                 # intermediate sprite
ASCII_COLS, ASCII_ROWS = 48, 36
RAMP = " .:-=+*#%@"
ASCII_THRESHOLD = 0.42                      # raise if the background is noisy
CYCLE = 16
POP_SPREAD = 1.6                            # seconds over which pixels pop in


def b64png(img) -> str:
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def load_avatar():
    """Prepare every representation of the photo the animation needs, or None."""
    if not AVATAR.exists():
        return None
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps  # only needed when a photo is present

    img = ImageOps.exif_transpose(Image.open(AVATAR)).convert("RGB")
    img = ImageOps.fit(img, (PW * 3 // 2, PH * 3 // 2), Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=80, optimize=True, progressive=True)

    # Pixel art: shrink, punch up saturation, quantise to a small retro palette.
    punchy = ImageEnhance.Color(ImageEnhance.Contrast(img).enhance(1.15)).enhance(1.25)
    grid = punchy.resize((GRID_C, GRID_R), Image.Resampling.BOX).quantize(16, Image.Quantize.MEDIANCUT).convert("RGB")
    sprite = punchy.resize((SPRITE_C, SPRITE_R), Image.Resampling.BOX).quantize(32, Image.Quantize.MEDIANCUT).convert("RGB")

    # Equalise + edge-enhance so features survive the 48x36 downsample.
    gray = ImageOps.equalize(img.convert("L")).filter(ImageFilter.EDGE_ENHANCE_MORE)
    small = gray.resize((ASCII_COLS, ASCII_ROWS), Image.Resampling.LANCZOS)
    return {
        "jpeg": base64.b64encode(buf.getvalue()).decode("ascii"),
        "grid": list(zip(*[iter(grid.tobytes())] * 3)),  # RGB byte triples
        "sprite": b64png(sprite),
        "ascii": small,
    }


def ink(b: int) -> float:
    """Map brightness to glyph density: light walls go blank, hair/glasses/shirt go dense."""
    return max(0.0, (1 - b / 255 - ASCII_THRESHOLD) / (1 - ASCII_THRESHOLD)) ** 0.75


def ascii_rows(small):
    # The photo has a bright background, so dark areas (hair, glasses, shirt) get the
    # densest glyphs - it reads like an ink sketch in both themes.
    px = small.tobytes()  # one byte per pixel (mode L)
    return [
        "".join(RAMP[min(len(RAMP) - 1, int(ink(b) * len(RAMP)))] for b in px[y * ASCII_COLS:(y + 1) * ASCII_COLS])
        for y in range(ASCII_ROWS)
    ]


def pixel_layer(grid, x, y):
    rng = random.Random(42)
    cw, ch = PW / GRID_C, PH / GRID_R
    cells = []
    for r in range(GRID_R):
        for c in range(GRID_C):
            red, green, blue = grid[r * GRID_C + c]
            delay = rng.uniform(0, POP_SPREAD) * 0.6 + (r / GRID_R) * POP_SPREAD * 0.4  # loosely top-down
            cells.append(
                f'<rect x="{x + c * cw:.0f}" y="{y + r * ch:.0f}" width="{cw + .5:g}" height="{ch + .5:g}" '
                f'fill="#{red:02x}{green:02x}{blue:02x}" style="animation-delay:{delay:.2f}s"/>'
            )
    return "".join(cells)


def photo_panel(t, avatar, handle):
    x, y, w, h = PX, PY, PW, PH
    out = [
        f'<clipPath id="frame"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{t.panel}"/>',
        '<g clip-path="url(#frame)">',
    ]
    if avatar:
        # Embed the JPEG once; every layer that needs it references it with <use>.
        photo_def = (f'<image id="ph" href="data:image/jpeg;base64,{avatar["jpeg"]}" x="{x}" y="{y}" width="{w}" height="{h}" '
                     f'preserveAspectRatio="xMidYMid slice"/>')
        photo = '<use href="#ph"/>'
        cell_h = h / ASCII_ROWS
        ascii_text = "".join(
            f'<text x="{x + 4}" y="{y + (i + 1) * cell_h - 2:.1f}" textLength="{w - 8}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{esc(r)}</text>'
            for i, r in enumerate(ascii_rows(avatar["ascii"]))
        )
        slices = "".join(
            f'<clipPath id="s{i}"><rect x="{x}" y="{y + sy}" width="{w}" height="{sh}"/></clipPath>'
            for i, (sy, sh) in enumerate([(84, 24), (176, 14), (300, 34)])
        )
        out += [
            f"<defs>{photo_def}{slices}"
            f'<clipPath id="decode"><rect x="{x}" y="{y}" width="{w}" height="0">'
            f'<animate attributeName="height" values="0;0;{h};{h}" keyTimes="0;0.78;0.88;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f"</rect></clipPath></defs>",
            f'<g class="photo">{photo}<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#tint)"/></g>',
            *(f'<g class="glitch g{i}" clip-path="url(#s{i})">{photo}'
              f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" opacity=".35"/></g>'
              for i, c in enumerate([t.c1, t.c3, t.c2])),
            f'<image class="sprite" href="data:image/png;base64,{avatar["sprite"]}" x="{x}" y="{y}" width="{w}" height="{h}" '
            f'preserveAspectRatio="none" image-rendering="optimizeSpeed" style="image-rendering:pixelated"/>',
            f'<g class="pxs">{pixel_layer(avatar["grid"], x, y)}</g>',
            f'<rect class="asciibg" x="{x}" y="{y}" width="{w}" height="{h}" fill="{t.bg}"/>',
            f'<g class="ascii" clip-path="url(#decode)">{ascii_text}</g>',
        ]
    else:
        out += [
            f'<circle class="spin" cx="{x + w / 2}" cy="{y + h / 2 - 20}" r="104" fill="none" stroke="url(#neon)" '
            f'stroke-width="3" stroke-dasharray="120 533" stroke-linecap="round"/>',
            f'<circle cx="{x + w / 2}" cy="{y + h / 2 - 20}" r="90" fill="none" stroke="{t.line}"/>',
            f'<text class="mono" x="{x + w / 2}" y="{y + h / 2 + 8}" text-anchor="middle" fill="url(#neon)">PH</text>',
        ]
    out += [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#crt)"/>',
        f'<rect class="scan" x="{x}" y="{y - 70}" width="{w}" height="70" fill="url(#beam)"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="44" fill="url(#shadeTop)"/>',
        f'<rect x="{x}" y="{y + h - 54}" width="{w}" height="54" fill="url(#shade)"/>',
        "</g>",
        f'<text class="hud" x="{x + 16}" y="{y + 27}"><tspan class="pulse" style="fill:{t.c3}">●</tspan> '
        f'{"REC" if avatar else "ID.CARD"}</text>',
    ]
    if avatar:
        for cls, label in (("lbl1", "8-BIT ▸ 24×30"), ("lbl2", "RGB ✔ HI-RES"), ("lbl3", "ASCII ▸ TXT")):
            out.append(f'<text class="hud {cls}" x="{x + w - 16}" y="{y + 27}" text-anchor="end">{label}</text>')
    else:
        out.append(f'<text class="hud" x="{x + w - 16}" y="{y + 27}" text-anchor="end">v1.0</text>')
    out += [
        f'<text class="tag" x="{x + 16}" y="{y + h - 20}">{esc(handle.upper())} '
        f'<tspan style="fill:{t.ok}">// VERIFIED ✔</tspan></text>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="{t.line}" stroke-width="1.5"/>',
        f'<rect class="trail" x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="none" stroke="url(#neon)" '
        f'stroke-width="3" pathLength="1000" stroke-dasharray="180 820" stroke-linecap="round"/>',
    ]
    s = 22
    for (bx, by, dx, dy) in [(x - 8, y - 8, 1, 1), (x + w + 8, y - 8, -1, 1), (x - 8, y + h + 8, 1, -1), (x + w + 8, y + h + 8, -1, -1)]:
        out.append(f'<path d="M{bx} {by + dy * s} V{by} H{bx + dx * s}" fill="none" stroke="{t.c1}" stroke-width="2"/>')
    return out


# Phase keyframes (percent of CYCLE). Pixels own delays shift them by <= POP_SPREAD s.
PHASE_CSS = f"""
@keyframes px{{0%{{opacity:0;transform:scale(0)}}4%{{opacity:1;transform:scale(1)}}29%{{opacity:1;transform:scale(1)}}33%,100%{{opacity:0;transform:scale(2.2)}}}}
.pxs rect{{opacity:0;transform-box:fill-box;transform-origin:center;animation:px {CYCLE}s cubic-bezier(.2,.8,.2,1) infinite both}}
@keyframes sprite{{0%,16%{{opacity:0}}17%,40%{{opacity:1}}45%,100%{{opacity:0}}}}.sprite{{animation:sprite {CYCLE}s steps(1,end) infinite}}
@keyframes photo{{0%,16%{{opacity:0}}17%,82%{{opacity:1}}86%,100%{{opacity:0}}}}.photo{{animation:photo {CYCLE}s linear infinite}}
@keyframes glitch{{0%,71.9%{{opacity:0;transform:none}}72%{{opacity:1;transform:translateX(-14px)}}73%{{transform:translateX(12px)}}74%{{transform:translateX(-7px)}}75%{{transform:translateX(9px)}}76%,100%{{opacity:0;transform:none}}}}
.glitch{{opacity:0;animation:glitch {CYCLE}s steps(1) infinite}}.g1{{animation-delay:-.15s}}.g2{{animation-delay:.1s}}
@keyframes ascii{{0%,77%{{opacity:0}}80%,95%{{opacity:1}}99%,100%{{opacity:0}}}}.ascii,.asciibg{{animation:ascii {CYCLE}s linear infinite}}
@keyframes lbl1{{0%,40%{{opacity:1}}42%,100%{{opacity:0}}}}.lbl1{{animation:lbl1 {CYCLE}s steps(1) infinite}}
@keyframes lbl2{{0%,41%{{opacity:0}}42%,78%{{opacity:1}}79%,100%{{opacity:0}}}}.lbl2{{opacity:0;animation:lbl2 {CYCLE}s steps(1) infinite}}
@keyframes lbl3{{0%,78%{{opacity:0}}79%,100%{{opacity:1}}}}.lbl3{{opacity:0;animation:lbl3 {CYCLE}s steps(1) infinite}}
"""


def render(t, profile, stats, avatar):
    rows = [tuple(r) for r in profile["info"]]
    if stats:
        rows.append(("COMMITS", f"{stats['total']:,} contributions in the last year"))
        rows.append(("STREAK", f"{stats['current']} days current  ·  {stats['longest']} days best"))
    rows.append(("UPTIME", f"Shipping on GitHub since {profile['since']}"))

    out = [
        svg_open(W, H, f"{profile['name']} identity card with animated pixel-art portrait"),
        "<defs>",
        neon_gradient(t, "neon", dur="5s"),
        f'<pattern id="crt" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".12"/></pattern>',
        f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.c1}" stop-opacity="0"/>'
        f'<stop offset=".85" stop-color="{t.c1}" stop-opacity=".25"/><stop offset="1" stop-color="{t.c1}" stop-opacity=".9"/></linearGradient>',
        f'<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.bg}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{t.bg}" stop-opacity=".92"/></linearGradient>',
        f'<linearGradient id="shadeTop" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.bg}" stop-opacity=".75"/>'
        f'<stop offset="1" stop-color="{t.bg}" stop-opacity="0"/></linearGradient>',
        f'<linearGradient id="tint" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.c1}" stop-opacity=".08"/>'
        f'<stop offset="1" stop-color="{t.c2}" stop-opacity=".14"/></linearGradient>',
        "</defs>",
        "<style>",
        f".k{{font:700 15px {MONO};fill:{t.c1}}}",
        f".v{{font:500 15px {MONO};fill:{t.text}}}",
        f".h{{font:800 24px {MONO};fill:{t.text}}}",
        f".hud{{font:700 11px {MONO};fill:{t.text};letter-spacing:1.5px}}",
        f".tag{{font:700 12px {MONO};fill:{t.text};letter-spacing:1.5px}}",
        f".mono{{font:800 92px {SANS}}}",
        f"g.ascii text{{font:700 11.6px {MONO};fill:{t.c1}}}",
        PHASE_CSS,
        f"@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY({PH + 70}px)}}}}.scan{{animation:scan 3.2s linear infinite}}",
        "@keyframes trail{to{stroke-dashoffset:-1000}}.trail{animation:trail 6s linear infinite}",
        "@keyframes spin{to{transform:rotate(360deg)}}",
        f".spin{{transform-origin:{PX + PW / 2}px {PY + PH / 2 - 20}px;animation:spin 8s linear infinite}}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}.pulse{animation:pulse 1.6s ease-in-out infinite}",
        "@keyframes in{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}.row{animation:in .5s ease-out both}",
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s steps(1) infinite}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t.bg}" stroke="{t.line}" stroke-width="1.5"/>',
        window_chrome(t, W, f"{profile['handle']}@github: ~ — neofetch"),
        *photo_panel(t, avatar, profile["handle"]),
        f'<text class="h" x="{ROW_X}" y="104">{esc(profile["handle"])}<tspan style="fill:{t.c2}">@</tspan>github</text>',
        f'<rect x="{ROW_X}" y="118" width="300" height="3" rx="1.5" fill="url(#neon)"/>',
    ]
    for i, (key, value) in enumerate(rows):
        y = ROW_Y0 + i * ROW_STEP + 8
        out.append(
            f'<g class="row" style="animation-delay:{0.2 + i * 0.1:.2f}s">'
            f'<text class="k" x="{ROW_X}" y="{y}">{esc(key)}</text>'
            f'<text class="v" x="{VAL_X}" y="{y}">{esc(value)}</text></g>'
        )
    y = ROW_Y0 + len(rows) * ROW_STEP + 4
    swatches = t.heat[1:] + [t.c1, t.c2, t.c3, t.ok]
    for i, color in enumerate(swatches):
        out.append(f'<rect x="{ROW_X + i * 36}" y="{y}" width="30" height="16" rx="4" fill="{color}"/>')
    out.append(f'<rect class="cur" x="{ROW_X + len(swatches) * 36 + 6}" y="{y - 2}" width="10" height="20" fill="{t.c1}"/>')
    out.append("</svg>")
    return out


def main():
    profile = load_profile()
    stats = compute_stats(load_json("contributions.json"))
    avatar = load_avatar()
    for t in THEMES:
        write_svg(t, "info-card.svg", render(t, profile, stats, avatar))


if __name__ == "__main__":
    main()
