#!/usr/bin/env python3
"""Generate the neofetch-style identity card with a rotating monogram crest.

Reads data/profile.json and live stats from data/contributions.json.
Set STATIC=1 to disable animation.
"""
import os

from contrib_stats import compute_stats
from theme import (BG, GOLD, GOLD_DEEP, GOLD_LIGHT, HEAT, IVORY, LINE, MONO, MUTED, PANEL, SERIF,
                   esc, gold_gradient, load_json, load_profile, svg_open, write_svg)

STATIC = os.getenv("STATIC", "0") == "1"
W, H = 1200, 500
CREST_X, CREST_Y, CREST_R = 220, 272, 128
ROW_X, VAL_X, ROW_Y0, ROW_STEP = 470, 610, 150, 27


def initials(name: str) -> str:
    return "".join(part[0] for part in name.split()[:2]).upper()


def main():
    profile = load_profile()
    rows = [tuple(r) for r in profile["info"]]
    stats = compute_stats(load_json("contributions.json"))
    if stats:
        rows.append(("COMMITS", f"{stats['total']:,} contributions in the last year"))
        rows.append(("STREAK", f"{stats['current']} days current  ·  {stats['longest']} days best"))
    rows.append(("UPTIME", f"Shipping on GitHub since {profile['since']}"))

    ring_text = f"{profile['name'].upper()}  •  {profile['headline'].upper()}  •  "
    r_text = CREST_R + 22
    anim = "" if STATIC else (
        "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
        ".row{animation:in .5s ease-out both}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        f".spin{{transform-origin:{CREST_X}px {CREST_Y}px;animation:spin 40s linear infinite}}"
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1.1s steps(1) infinite}"
    )
    out = [
        svg_open(W, H, f"{profile['name']} identity card"),
        "<defs>",
        gold_gradient("gold", shimmer=not STATIC, dur="8s"),
        f'<radialGradient id="crestGlow"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>',
        f'<path id="ringPath" d="M{CREST_X - r_text} {CREST_Y} a{r_text} {r_text} 0 1 1 {2 * r_text} 0 '
        f'a{r_text} {r_text} 0 1 1 {-2 * r_text} 0"/>',
        f'<linearGradient id="border" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.7"/>'
        f'<stop offset="0.5" stop-color="{LINE}"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0.5"/></linearGradient>',
        "</defs>",
        "<style>",
        f".k{{font:700 15px {MONO};fill:{GOLD};letter-spacing:1px}}",
        f".v{{font:400 15px {MONO};fill:{IVORY}}}",
        f".h{{font:700 22px {MONO};fill:{GOLD_LIGHT}}}",
        f".m{{font:400 13px {MONO};fill:{MUTED}}}",
        f".mono{{font:400 92px {SERIF};fill:url(#gold);letter-spacing:4px}}",
        f".ring{{font:600 12.5px {MONO};fill:{GOLD};letter-spacing:4.2px}}",
        f".est{{font:600 12px {MONO};fill:{MUTED};letter-spacing:6px}}",
        anim,
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="20" fill="{BG}" stroke="url(#border)" stroke-width="1.5"/>',
        # window chrome
        f'<path d="M1 46 V21 a20 20 0 0 1 20 -20 H{W - 21} a20 20 0 0 1 20 20 V46 Z" fill="{PANEL}"/>',
        f'<line x1="1" y1="46" x2="{W - 1}" y2="46" stroke="{LINE}"/>',
        f'<circle cx="28" cy="24" r="6" fill="{GOLD_DEEP}"/><circle cx="48" cy="24" r="6" fill="{GOLD}"/>'
        f'<circle cx="68" cy="24" r="6" fill="{GOLD_LIGHT}"/>',
        f'<text class="m" x="{W / 2}" y="29" text-anchor="middle">{esc(profile["handle"])}@github: ~ — neofetch</text>',
        # crest
        f'<circle cx="{CREST_X}" cy="{CREST_Y}" r="{CREST_R + 60}" fill="url(#crestGlow)"/>',
        f'<g class="spin"><text class="ring"><textPath href="#ringPath" textLength="{2 * 3.14159 * r_text - 6:.0f}">'
        f"{esc(ring_text)}</textPath></text></g>",
        f'<circle cx="{CREST_X}" cy="{CREST_Y}" r="{CREST_R}" fill="{PANEL}" stroke="{GOLD}" stroke-width="1.5"/>',
        f'<circle cx="{CREST_X}" cy="{CREST_Y}" r="{CREST_R - 10}" fill="none" stroke="{GOLD}" stroke-opacity="0.35"/>',
        f'<text class="mono" x="{CREST_X}" y="{CREST_Y + 30}" text-anchor="middle">{esc(initials(profile["name"]))}</text>',
        f'<line x1="{CREST_X - 46}" y1="{CREST_Y + 56}" x2="{CREST_X + 46}" y2="{CREST_Y + 56}" stroke="{GOLD}" stroke-opacity="0.6"/>',
        f'<text class="est" x="{CREST_X + 3}" y="{CREST_Y + 80}" text-anchor="middle">EST. {esc(profile["since"])}</text>',
        f'<line x1="430" y1="76" x2="430" y2="{H - 30}" stroke="{LINE}"/>',
        # neofetch body
        f'<text class="h" x="{ROW_X}" y="96">{esc(profile["handle"])}<tspan style="fill:{MUTED}">@</tspan>github</text>',
        f'<line x1="{ROW_X}" y1="112" x2="{ROW_X + 280}" y2="112" stroke="{GOLD}" stroke-opacity="0.5" stroke-dasharray="4 4"/>',
    ]
    for i, (key, value) in enumerate(rows):
        y = ROW_Y0 + i * ROW_STEP
        out.append(
            f'<g class="row" style="animation-delay:{0.15 + i * 0.12:.2f}s">'
            f'<text class="k" x="{ROW_X}" y="{y}">{esc(key)}</text>'
            f'<text class="v" x="{VAL_X}" y="{y}">{esc(value)}</text></g>'
        )
    # palette swatches + blinking cursor
    y = ROW_Y0 + len(rows) * ROW_STEP + 4
    for i, color in enumerate(HEAT + [GOLD, GOLD_LIGHT, IVORY]):
        out.append(f'<rect x="{ROW_X + i * 34}" y="{y}" width="28" height="14" rx="3" fill="{color}"/>')
    out.append(f'<text class="v" x="{ROW_X + 8 * 34 + 14}" y="{y + 13}"><tspan style="fill:{GOLD}">$</tspan>'
               f' <tspan class="cur" style="fill:{GOLD_LIGHT}">█</tspan></text>')
    out.append("</svg>")
    write_svg("info-card.svg", out)


if __name__ == "__main__":
    main()
