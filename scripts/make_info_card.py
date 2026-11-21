#!/usr/bin/env python3
"""Generate the identity card: animated photo (ASCII decode -> photo -> glitch) + neofetch facts.

The photo comes from data/avatar.jpg (create it with scripts/set_photo.py). Without
it, an animated monogram is shown instead. Live stats come from contributions.json.
"""
import base64
import io

from contrib_stats import compute_stats
from theme import (AVATAR, MONO, SANS, THEMES, esc, load_json, load_profile, neon_gradient,
                   svg_open, window_chrome, write_svg)

W, H = 1200, 540
PX, PY, PW, PH = 40, 76, 336, 420          # photo frame (4:5)
ROW_X, VAL_X, ROW_Y0, ROW_STEP = 430, 570, 150, 28
ASCII_COLS, ASCII_ROWS = 48, 36
RAMP = " .:-=+*#%@"
CYCLE = 14  # seconds for one ASCII -> photo -> glitch loop


def load_avatar():
    """Return (jpeg_base64, grayscale ASCII-ready image) or None."""
    if not AVATAR.exists():
        return None
    from PIL import Image, ImageOps  # only needed when a photo is present

    img = ImageOps.exif_transpose(Image.open(AVATAR)).convert("RGB")
    img = ImageOps.fit(img, (PW * 3 // 2, PH * 3 // 2), Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    gray = ImageOps.autocontrast(img.convert("L"), cutoff=2)
    small = gray.resize((ASCII_COLS, ASCII_ROWS), Image.Resampling.LANCZOS)
    return base64.b64encode(buf.getvalue()).decode("ascii"), small


def ascii_rows(small, dark: bool):
    px = list(small.getdata())
    rows = []
    for y in range(ASCII_ROWS):
        line = ""
        for b in px[y * ASCII_COLS:(y + 1) * ASCII_COLS]:
            level = b / 255 if dark else 1 - b / 255   # bright text on dark, dark text on light
            line += RAMP[min(len(RAMP) - 1, int(level * len(RAMP)))]
        rows.append(line)
    return rows


def photo_panel(t, avatar, handle):
    x, y, w, h = PX, PY, PW, PH
    out = [
        f'<clipPath id="frame"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18"/></clipPath>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{t.panel}"/>',
        f'<g clip-path="url(#frame)">',
    ]
    if avatar:
        b64, small = avatar
        href = f"data:image/jpeg;base64,{b64}"
        cell_h = h / ASCII_ROWS
        rows = ascii_rows(small, t.name == "dark")
        ascii_text = "".join(
            f'<text x="{x + 4}" y="{y + (i + 1) * cell_h - 2:.1f}" textLength="{w - 8}" lengthAdjust="spacingAndGlyphs" '
            f'xml:space="preserve">{esc(r)}</text>'
            for i, r in enumerate(rows)
        )
        img = f'<image href="{href}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>'
        slices = "".join(
            f'<clipPath id="s{i}"><rect x="{x}" y="{y + sy}" width="{w}" height="{sh}"/></clipPath>'
            for i, (sy, sh) in enumerate([(70, 26), (190, 14), (300, 34)])
        )
        out += [
            f"<defs>{slices}"
            f'<clipPath id="decode"><rect x="{x}" y="{y}" width="{w}" height="0">'
            f'<animate attributeName="height" values="0;{h};{h}" keyTimes="0;0.15;1" dur="{CYCLE}s" repeatCount="indefinite"/>'
            f"</rect></clipPath></defs>",
            f'<g class="photo">{img}'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#tint)"/></g>',
            *(f'<g class="glitch g{i}" clip-path="url(#s{i})">{img}'
              f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" opacity=".35"/></g>'
              for i, c in enumerate([t.c1, t.c3, t.c2])),
            f'<g class="ascii" clip-path="url(#decode)">{ascii_text}</g>',
        ]
    else:
        out += [
            f'<circle class="spin" cx="{x + w / 2}" cy="{y + h / 2 - 20}" r="104" fill="none" stroke="url(#neon)" '
            f'stroke-width="3" stroke-dasharray="120 533" stroke-linecap="round"/>',
            f'<circle cx="{x + w / 2}" cy="{y + h / 2 - 20}" r="90" fill="none" stroke="{t.line}"/>',
            f'<text class="mono" x="{x + w / 2}" y="{y + h / 2 + 8}" text-anchor="middle" fill="url(#neon)">PH</text>',
        ]
    # shared HUD: CRT lines, scan beam, labels, brackets, travelling border light
    out += [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#crt)"/>',
        f'<rect class="scan" x="{x}" y="{y - 70}" width="{w}" height="70" fill="url(#beam)"/>',
        f'<rect x="{x}" y="{y + h - 54}" width="{w}" height="54" fill="url(#shade)"/>',
        "</g>",
        f'<text class="hud" x="{x + 16}" y="{y + 26}"><tspan class="pulse" style="fill:{t.c3}">●</tspan> '
        f'{"IMG.DECODE" if avatar else "ID.CARD"}</text>',
        *([f'<text class="hud ascii" x="{x + w - 16}" y="{y + 26}" text-anchor="end">ascii → rgb</text>',
           f'<text class="hud photo" x="{x + w - 16}" y="{y + 26}" text-anchor="end">rgb ✔</text>']
          if avatar else [f'<text class="hud" x="{x + w - 16}" y="{y + 26}" text-anchor="end">v1.0</text>']),
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


def render(t, profile, stats, avatar):
    rows = [tuple(r) for r in profile["info"]]
    if stats:
        rows.append(("COMMITS", f"{stats['total']:,} contributions in the last year"))
        rows.append(("STREAK", f"{stats['current']} days current  ·  {stats['longest']} days best"))
    rows.append(("UPTIME", f"Shipping on GitHub since {profile['since']}"))

    out = [
        svg_open(W, H, f"{profile['name']} identity card"),
        "<defs>",
        neon_gradient(t, "neon", dur="5s"),
        f'<pattern id="crt" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="{t.bg}" opacity=".18"/></pattern>',
        f'<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.c1}" stop-opacity="0"/>'
        f'<stop offset=".85" stop-color="{t.c1}" stop-opacity=".28"/><stop offset="1" stop-color="{t.c1}" stop-opacity=".9"/></linearGradient>',
        f'<linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{t.bg}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{t.bg}" stop-opacity=".92"/></linearGradient>',
        f'<linearGradient id="tint" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t.c1}" stop-opacity=".10"/>'
        f'<stop offset="1" stop-color="{t.c2}" stop-opacity=".16"/></linearGradient>',
        "</defs>",
        "<style>",
        f".k{{font:700 15px {MONO};fill:{t.c1}}}",
        f".v{{font:500 15px {MONO};fill:{t.text}}}",
        f".h{{font:800 24px {MONO};fill:{t.text}}}",
        f".hud{{font:700 11px {MONO};fill:{t.text};letter-spacing:1.5px}}",
        f".tag{{font:700 12px {MONO};fill:{t.text};letter-spacing:1.5px}}",
        f".mono{{font:800 92px {SANS}}}",
        f"g.ascii text{{font:600 11.6px {MONO};fill:{t.c1}}}",
        f"@keyframes asciiFade{{0%,24%{{opacity:1}}32%,100%{{opacity:0}}}}.ascii{{animation:asciiFade {CYCLE}s linear infinite}}",
        f"@keyframes photoFade{{0%,24%{{opacity:0}}32%,84%{{opacity:1}}92%,100%{{opacity:0}}}}.photo{{animation:photoFade {CYCLE}s linear infinite}}",
        "@keyframes glitch{0%,79.9%{opacity:0;transform:none}80%{opacity:1;transform:translateX(-14px)}"
        "81%{transform:translateX(12px)}82%{transform:translateX(-7px)}83%{transform:translateX(9px)}84%,100%{opacity:0;transform:none}}",
        f".glitch{{opacity:0;animation:glitch {CYCLE}s steps(1) infinite}}.g1{{animation-delay:-.15s}}.g2{{animation-delay:.1s}}",
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
