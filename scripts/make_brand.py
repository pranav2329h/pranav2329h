#!/usr/bin/env python3
"""Generate the brand SVGs: hero header, section titles, divider and footer."""
import random

from theme import (BG, GOLD, GOLD_DEEP, GOLD_LIGHT, IVORY, LINE, MONO, MUTED, SANS, SERIF,
                   esc, gold_gradient, load_profile, svg_open, write_svg)

W = 1200

SECTIONS = [
    ("about", "01", "ABOUT", "The Engineer"),
    ("arsenal", "02", "ARSENAL", "Tech Arsenal"),
    ("work", "03", "PORTFOLIO", "Featured Work"),
    ("activity", "04", "ACTIVITY", "Contribution Matrix"),
    ("insights", "05", "INSIGHTS", "GitHub Analytics"),
    ("connect", "06", "CONNECT", "Let’s Build Together"),
]


def corner(x, y, sx, sy):
    """Art-deco corner ornament; sx/sy flip it into each corner."""
    d1 = f"M{x} {y + sy * 46} V{y} H{x + sx * 46}"
    d2 = f"M{x + sx * 8} {y + sy * 30} V{y + sy * 8} H{x + sx * 30}"
    dx, dy = x + sx * 16, y + sy * 16
    diamond = f"M{dx} {dy - 4} L{dx + 4} {dy} L{dx} {dy + 4} L{dx - 4} {dy} Z"
    return (
        f'<path d="{d1}" fill="none" stroke="{GOLD}" stroke-width="1.4"/>'
        f'<path d="{d2}" fill="none" stroke="{GOLD}" stroke-opacity="0.55" stroke-width="1"/>'
        f'<path d="{diamond}" fill="{GOLD}"/>'
    )


def ornament(cx, y, half, cls=""):
    """Two hairlines meeting at a central diamond."""
    return (
        f'<g class="{cls}">'
        f'<line x1="{cx - half}" y1="{y}" x2="{cx - 14}" y2="{y}" stroke="url(#fadeL)" stroke-width="1.2"/>'
        f'<line x1="{cx + 14}" y1="{y}" x2="{cx + half}" y2="{y}" stroke="url(#fadeR)" stroke-width="1.2"/>'
        f'<path d="M{cx} {y - 6} L{cx + 6} {y} L{cx} {y + 6} L{cx - 6} {y} Z" fill="{GOLD}"/>'
        f'<path d="M{cx} {y - 11} L{cx + 11} {y} L{cx} {y + 11} L{cx - 11} {y} Z" fill="none" '
        f'stroke="{GOLD}" stroke-opacity="0.5"/>'
        f"</g>"
    )


FADES = (
    f'<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>'
    f'<stop offset="1" stop-color="{GOLD}"/></linearGradient>'
    f'<linearGradient id="fadeR" x1="0" x2="1"><stop offset="0" stop-color="{GOLD}"/>'
    f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>'
)


def header(profile):
    H = 420
    cx, cy = W / 2, 205
    rng = random.Random(2329)
    particles = []
    for i in range(26):
        x, y = rng.uniform(60, W - 60), rng.uniform(50, H - 50)
        r = rng.choice([1, 1.2, 1.5, 2])
        dur, delay = rng.uniform(5, 10), rng.uniform(0, 6)
        particles.append(
            f'<circle class="p" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{GOLD_LIGHT}" '
            f'style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>'
        )
    subtitle = f"{profile['headline'].upper()}  ·  {profile['location'].upper()}"
    return [
        svg_open(W, H, f"{profile['name']} — {profile['headline']}"),
        "<defs>",
        gold_gradient("goldShimmer", shimmer=True, dur="7s"),
        FADES,
        f'<radialGradient id="glow" cx="0.5" cy="0.48" r="0.55"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.20"/>'
        f'<stop offset="0.6" stop-color="{GOLD}" stop-opacity="0.04"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">'
        f'<path d="M40 0H0V40" fill="none" stroke="{LINE}" stroke-width="1"/></pattern>',
        '<radialGradient id="gridFade" cx="0.5" cy="0.5" r="0.6"><stop offset="0" stop-color="#fff" stop-opacity="0.9"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        f'<mask id="gridMask"><rect width="{W}" height="{H}" fill="url(#gridFade)"/></mask>',
        "</defs>",
        "<style>",
        f".eyebrow{{font:600 13px {MONO};letter-spacing:6px;fill:{GOLD}}}",
        f".name{{font:400 76px {SERIF};letter-spacing:10px;fill:url(#goldShimmer)}}",
        f".sub{{font:500 15px {SANS};letter-spacing:7px;fill:{IVORY};fill-opacity:.82}}",
        f".handle{{font:500 13px {MONO};letter-spacing:3px;fill:{MUTED}}}",
        "@keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}",
        "@keyframes draw{from{stroke-dashoffset:600}to{stroke-dashoffset:0}}",
        "@keyframes spin{to{transform:rotate(360deg)}}",
        "@keyframes twinkle{0%,100%{opacity:.08;transform:translateY(0)}50%{opacity:.9;transform:translateY(-16px)}}",
        "@keyframes pulse{0%,100%{opacity:.35}50%{opacity:1}}",
        ".a1{animation:rise 1s ease-out .1s both}.a2{animation:rise 1.2s ease-out .35s both}",
        ".a3{animation:rise 1s ease-out .8s both}.a4{animation:rise 1s ease-out 1.1s both}",
        f".ring{{transform-origin:{cx}px {cy}px;animation:spin 80s linear infinite}}",
        f".ring2{{transform-origin:{cx}px {cy}px;animation:spin 120s linear infinite reverse}}",
        ".p{animation:twinkle 7s ease-in-out infinite}",
        ".dot{animation:pulse 2.4s ease-in-out infinite}",
        "</style>",
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#grid)" mask="url(#gridMask)" opacity="0.55"/>',
        f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
        f'<circle class="ring" cx="{cx}" cy="{cy}" r="178" fill="none" stroke="{GOLD}" stroke-opacity="0.16" stroke-dasharray="2 10"/>',
        f'<circle class="ring2" cx="{cx}" cy="{cy}" r="196" fill="none" stroke="{GOLD}" stroke-opacity="0.10" stroke-dasharray="60 18 4 18"/>',
        *particles,
        f'<rect x="22" y="22" width="{W - 44}" height="{H - 44}" fill="none" stroke="{GOLD}" stroke-opacity="0.22"/>',
        corner(22, 22, 1, 1), corner(W - 22, 22, -1, 1), corner(22, H - 22, 1, -1), corner(W - 22, H - 22, -1, -1),
        f'<text class="eyebrow a1" x="{cx}" y="118" text-anchor="middle">{esc(profile["eyebrow"])}</text>',
        f'<text class="name a2" x="{cx}" y="{cy + 22}" text-anchor="middle" textLength="920" lengthAdjust="spacingAndGlyphs">'
        f'{esc(profile["name"].upper())}</text>',
        ornament(cx, 262, 230, "a3"),
        f'<text class="sub a3" x="{cx}" y="308" text-anchor="middle">{esc(subtitle)}</text>',
        f'<g class="a4"><circle class="dot" cx="{cx - 92}" cy="345" r="4" fill="{GOLD_LIGHT}"/>'
        f'<text class="handle" x="{cx - 80}" y="350">@{esc(profile["handle"])} · ONLINE</text></g>',
        "</svg>",
    ]


def section_title(num, eyebrow, title):
    H = 120
    cx = W / 2
    return [
        svg_open(W, H, title),
        f"<defs>{gold_gradient('g', shimmer=True, dur='9s')}{FADES}</defs>",
        "<style>",
        f".n{{font:600 13px {MONO};letter-spacing:6px;fill:{GOLD}}}",
        f".t{{font:400 44px {SERIF};letter-spacing:3px;fill:url(#g)}}",
        "</style>",
        f'<text class="n" x="{cx}" y="26" text-anchor="middle">{num}  —  {esc(eyebrow)}</text>',
        f'<text class="t" x="{cx}" y="82" text-anchor="middle">{esc(title)}</text>',
        ornament(cx, 106, 170),
        "</svg>",
    ]


def divider():
    return [
        svg_open(W, 30, "divider"),
        f"<defs>{FADES}</defs>",
        ornament(W / 2, 15, 560),
        "</svg>",
    ]


def footer(profile):
    H = 230
    cx = W / 2
    return [
        svg_open(W, H, "Thanks for visiting"),
        f"<defs>{gold_gradient('g', shimmer=True, dur='8s')}{FADES}"
        f'<linearGradient id="floor" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0.10"/></linearGradient></defs>',
        "<style>",
        f".t{{font:italic 400 38px {SERIF};fill:url(#g)}}",
        f".s{{font:500 12px {MONO};letter-spacing:5px;fill:{MUTED}}}",
        f".k{{font:600 12px {MONO};letter-spacing:4px;fill:{GOLD}}}",
        "@keyframes pulse{0%,100%{opacity:.3}50%{opacity:1}}.dot{animation:pulse 2.4s ease-in-out infinite}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>',
        f'<rect width="{W}" height="{H}" rx="18" fill="url(#floor)"/>',
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/>',
        ornament(cx, 44, 260),
        f'<text class="t" x="{cx}" y="112" text-anchor="middle">Thanks for visiting</text>',
        f'<text class="s" x="{cx}" y="150" text-anchor="middle">BUILT WITH CODE, CURIOSITY &amp; COFFEE</text>',
        f'<circle class="dot" cx="{cx - 186}" cy="185" r="4" fill="{GOLD_LIGHT}"/>',
        f'<text class="k" x="{cx + 8}" y="189" text-anchor="middle">SYSTEM STATUS: ONLINE'
        f'<tspan style="fill:{MUTED}">   [ OK ]</tspan></text>',
        "</svg>",
    ]


def main():
    profile = load_profile()
    write_svg("header.svg", header(profile))
    write_svg("divider.svg", divider())
    write_svg("footer.svg", footer(profile))
    for slug, num, eyebrow, title in SECTIONS:
        write_svg(f"titles/{slug}.svg", section_title(num, eyebrow, title))


if __name__ == "__main__":
    main()
