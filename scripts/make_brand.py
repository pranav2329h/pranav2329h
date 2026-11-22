#!/usr/bin/env python3
"""Generate the brand SVGs: hero header, section titles and footer."""
import random

from contrib_stats import compute_stats
from theme import MONO, SANS, THEMES, esc, load_json, load_profile, neon_gradient, svg_open, write_svg

W = 1200

SECTIONS = [
    ("about", "01", "about.md", "The Engineer"),
    ("terminal", "02", "whoami.sh", "Live Terminal"),
    ("arsenal", "03", "stack.json", "Tech Arsenal"),
    ("work", "04", "projects/", "Featured Work"),
    ("journey", "05", "timeline.log", "The Journey"),
    ("activity", "06", "git log", "Contribution Matrix"),
    ("insights", "07", "analytics.py", "GitHub Analytics"),
    ("connect", "08", "contact.sh", "Let’s Build Together"),
]

RAIN_CHARS = "01{}[]<>/=;:$#*+-~ABCDEF0123456789"


def typed_clip(cid, x, y, h, full_w, chars, start, step, dur):
    """clipPath whose width grows one character at a time (discrete SMIL steps)."""
    times, vals = ["0"], ["0"]
    for i in range(1, chars + 1):
        times.append(f"{(start + i * step) / dur:.4f}")
        vals.append(f"{full_w * i / chars:.1f}")
    return (
        f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="0" height="{h}">'
        f'<animate attributeName="width" dur="{dur}s" fill="freeze" calcMode="discrete" '
        f'keyTimes="{";".join(times)}" values="{";".join(vals)}"/></rect></clipPath>'
    )


def corner_brackets(t, x, y, w, h, size=26):
    s = size
    paths = [
        f"M{x} {y + s} V{y} H{x + s}", f"M{x + w - s} {y} H{x + w} V{y + s}",
        f"M{x} {y + h - s} V{y + h} H{x + s}", f"M{x + w - s} {y + h} H{x + w} V{y + h - s}",
    ]
    return "".join(f'<path d="{d}" fill="none" stroke="{t.c1}" stroke-width="2"/>' for d in paths)


def header(t, profile, stats):
    H = 440
    cx = W / 2
    rng = random.Random(2329)

    rain = []
    for i, x in enumerate(range(30, W, 46)):
        chars = "".join(rng.choice(RAIN_CHARS) for _ in range(26))
        tspans = "".join(f'<tspan x="{x}" dy="18">{esc(c)}</tspan>' for c in chars)
        dur, delay = rng.uniform(9, 18), rng.uniform(0, 18)
        color = t.c1 if i % 3 else t.c2
        rain.append(
            f'<text class="rain" y="-470" style="fill:{color};animation-duration:{dur:.1f}s;'
            f'animation-delay:-{delay:.1f}s">{tspans}</text>'
        )

    # rotating roles: each visible for an equal slice of the cycle
    roles = profile["roles"]
    n, cycle = len(roles), 3.2 * len(roles)
    slice_pct = 100 / n
    role_css, role_svg = [], []
    for i, role in enumerate(roles):
        a = i * slice_pct
        b = a + slice_pct
        role_css.append(
            f"@keyframes role{i}{{0%,{max(a - 0.01, 0):.2f}%{{opacity:0;transform:translateY(12px)}}"
            f"{a + 3:.2f}%,{b - 4:.2f}%{{opacity:1;transform:none}}{b:.2f}%,100%{{opacity:0;transform:translateY(-12px)}}}}"
            f".role{i}{{animation:role{i} {cycle:.1f}s ease-in-out infinite}}"
        )
        role_svg.append(
            f'<text class="role role{i}" x="{cx}" y="300" text-anchor="middle">'
            f'<tspan style="fill:{t.c1}">&lt;</tspan> {esc(role)} <tspan style="fill:{t.c1}">/&gt;</tspan></text>'
        )

    prompt = f"./init.sh --user {profile['handle']}"
    prompt_w = (len(prompt) + 2) * 9.0  # 15px monospace glyphs are ~0.6em wide
    prompt_x = cx - prompt_w / 2
    chips = [
        (t.ok, "Open to opportunities"),
        (t.c2, profile["location"]),
        (t.c3, f"{stats['total']:,} contributions / year" if stats else f"Building since {profile['since']}"),
    ]
    chip_w = [len(label) * 8.2 + 46 for _, label in chips]
    x = cx - (sum(chip_w) + 16 * (len(chips) - 1)) / 2
    chip_svg = []
    for (color, label), w in zip(chips, chip_w):
        chip_svg.append(
            f'<rect x="{x:.0f}" y="342" width="{w:.0f}" height="34" rx="17" fill="{t.panel}" stroke="{t.line}"/>'
            f'<circle class="pulse" cx="{x + 20:.0f}" cy="359" r="5" fill="{color}"/>'
            f'<text class="chip" x="{x + 34:.0f}" y="364">{esc(label)}</text>'
        )
        x += w + 16

    return [
        svg_open(W, H, f"{profile['name']} — {profile['headline']}"),
        "<defs>",
        neon_gradient(t, "neon", dur="5s"),
        f'<radialGradient id="g1"><stop offset="0" stop-color="{t.c1}" stop-opacity="{t.glow}"/>'
        f'<stop offset="1" stop-color="{t.c1}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="g2"><stop offset="0" stop-color="{t.c2}" stop-opacity="{t.glow}"/>'
        f'<stop offset="1" stop-color="{t.c2}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="grid" width="44" height="44" patternUnits="userSpaceOnUse">'
        f'<path d="M44 0H0V44" fill="none" stroke="{t.line}" stroke-width="1"/></pattern>',
        '<linearGradient id="vfade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".3" stop-color="#fff" stop-opacity="1"/><stop offset=".7" stop-color="#fff" stop-opacity="1"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#vfade)"/></mask>',
        typed_clip("typed", prompt_x, 92, 30, prompt_w + 4, len(prompt) + 2, 0.4, 0.055, 3.2),
        "</defs>",
        "<style>",
        f".rain{{font:500 14px {MONO};opacity:.16;animation:fall 12s linear infinite}}",
        f"@keyframes fall{{from{{transform:translateY(0)}}to{{transform:translateY({H + 480}px)}}}}",
        f".name{{font:800 84px {SANS};letter-spacing:1px}}",
        f".role{{font:600 22px {MONO};fill:{t.text};opacity:0}}",
        f".prompt{{font:500 15px {MONO};fill:{t.muted}}}",
        f".chip{{font:600 14px {MONO};fill:{t.text}}}",
        "@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(60px,-30px)}}",
        ".drift1{animation:drift 14s ease-in-out infinite}.drift2{animation:drift 18s ease-in-out infinite reverse}",
        "@keyframes glitchA{0%,90%,100%{opacity:0;transform:none}91%{opacity:.85;transform:translate(-5px,2px)}"
        "92.5%{opacity:.85;transform:translate(4px,-2px)}94%{opacity:0}}",
        "@keyframes glitchB{0%,90%,100%{opacity:0;transform:none}91%{opacity:.85;transform:translate(5px,-2px)}"
        "92.5%{opacity:.85;transform:translate(-4px,1px)}94%{opacity:0}}",
        ".gA{animation:glitchA 7s steps(1) infinite}.gB{animation:glitchB 7s steps(1) infinite}",
        "@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}",
        ".in{animation:rise 1s cubic-bezier(.2,.8,.2,1) .2s both}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 1.8s ease-in-out infinite}",
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s steps(1) infinite}",
        *role_css,
        "</style>",
        f'<rect width="{W}" height="{H}" rx="18" fill="{t.bg}"/>',
        f'<rect width="{W}" height="{H}" rx="18" fill="url(#grid)" opacity=".5"/>',
        f'<circle class="drift1" cx="230" cy="120" r="320" fill="url(#g1)"/>',
        f'<circle class="drift2" cx="980" cy="330" r="340" fill="url(#g2)"/>',
        f'<g mask="url(#fade)">{"".join(rain)}</g>',
        corner_brackets(t, 24, 24, W - 48, H - 48),
        f'<text class="prompt" x="{prompt_x:.0f}" y="112" clip-path="url(#typed)">'
        f'<tspan style="fill:{t.c1}">❯</tspan> {esc(prompt)}</text>',
        f'<rect class="cur" x="{prompt_x + prompt_w + 6:.0f}" y="98" width="9" height="18" fill="{t.c1}"/>',
        f'<g class="in">',
        f'<text class="name gA" x="{cx}" y="222" text-anchor="middle" textLength="880" lengthAdjust="spacingAndGlyphs" style="fill:{t.c1}">{esc(profile["name"].upper())}</text>',
        f'<text class="name gB" x="{cx}" y="222" text-anchor="middle" textLength="880" lengthAdjust="spacingAndGlyphs" style="fill:{t.c3}">{esc(profile["name"].upper())}</text>',
        f'<text class="name" x="{cx}" y="222" text-anchor="middle" textLength="880" lengthAdjust="spacingAndGlyphs" fill="url(#neon)">{esc(profile["name"].upper())}</text>',
        "</g>",
        *role_svg,
        *chip_svg,
        "</svg>",
    ]


def section_title(t, num, file, title):
    H = 130
    cx = W / 2
    bar = 260
    return [
        svg_open(W, H, title),
        f"<defs>{neon_gradient(t, 'neon', dur='6s')}"
        f'<filter id="blur" x="-50%" y="-200%" width="200%" height="500%"><feGaussianBlur stdDeviation="4"/></filter></defs>',
        "<style>",
        f".n{{font:600 15px {MONO};fill:{t.muted}}}",
        f".t{{font:800 46px {SANS};letter-spacing:.5px}}",
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}",
        f".bar{{transform-origin:{cx}px 0;animation:grow 1.2s cubic-bezier(.2,.8,.2,1) both}}",
        f"@keyframes travel{{0%,100%{{transform:translateX(-{bar / 2 - 6}px)}}50%{{transform:translateX({bar / 2 - 6}px)}}}}",
        ".dot{animation:travel 3.2s ease-in-out infinite}",
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}.in{animation:rise .9s ease-out both}",
        "</style>",
        f'<text class="n in" x="{cx}" y="28" text-anchor="middle"><tspan style="fill:{t.c1}">//</tspan> {num} '
        f'<tspan style="fill:{t.c2}">·</tspan> {esc(file)}</text>',
        f'<text class="t in" x="{cx}" y="86" text-anchor="middle" fill="url(#neon)">{esc(title)}</text>',
        f'<rect class="bar" x="{cx - bar / 2}" y="108" width="{bar}" height="4" rx="2" fill="url(#neon)"/>',
        f'<g class="dot"><circle cx="{cx}" cy="110" r="9" fill="{t.c1}" opacity=".6" filter="url(#blur)"/>'
        f'<circle cx="{cx}" cy="110" r="4" fill="{t.bg}" stroke="{t.c1}" stroke-width="2"/></g>',
        "</svg>",
    ]


def footer(t, profile):
    H = 250
    cx = W / 2

    def wave(amp, length, y):
        d = f"M0 {y}"
        for x in range(0, W * 2 + length, length):
            d += f" q{length / 4} {-amp} {length / 2} 0 t{length / 2} 0"
        return d

    msg = "exit 0  # see you in the next commit"
    msg_w = (len(msg) + 2) * 9.6
    msg_x = cx - msg_w / 2
    return [
        svg_open(W, H, "Thanks for visiting"),
        f"<defs>{neon_gradient(t, 'neon', dur='6s')}"
        + typed_clip("typed", msg_x, 120, 30, msg_w + 4, len(msg) + 2, 0.8, 0.06, 4)
        + "</defs>",
        "<style>",
        f".t{{font:800 44px {SANS}}}",
        f".m{{font:500 16px {MONO};fill:{t.muted}}}",
        f".k{{font:700 13px {MONO};fill:{t.text};letter-spacing:2px}}",
        f"@keyframes slide{{from{{transform:translateX(0)}}to{{transform:translateX(-{W}px)}}}}",
        ".w1{animation:slide 14s linear infinite}.w2{animation:slide 20s linear infinite}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 1.8s ease-in-out infinite}",
        "@keyframes blink{50%{opacity:0}}.cur{animation:blink 1s steps(1) infinite}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="18" fill="{t.bg}" stroke="{t.line}"/>',
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
        f'<g clip-path="url(#card)" opacity=".55">'
        f'<path class="w1" d="{wave(14, 300, 214)}" fill="none" stroke="{t.c1}" stroke-width="2"/>'
        f'<path class="w2" d="{wave(10, 400, 226)}" fill="none" stroke="{t.c2}" stroke-width="2"/></g>',
        f'<text class="t" x="{cx}" y="86" text-anchor="middle" fill="url(#neon)">Thanks for visiting</text>',
        f'<text class="m" x="{msg_x:.0f}" y="141" clip-path="url(#typed)"><tspan style="fill:{t.c1}">❯</tspan> {esc(msg)}</text>',
        f'<rect class="cur" x="{msg_x + msg_w + 6:.0f}" y="127" width="9" height="18" fill="{t.c1}"/>',
        f'<circle class="pulse" cx="{cx - 112}" cy="179" r="5" fill="{t.ok}"/>',
        f'<text class="k" x="{cx - 98}" y="184">SYSTEM STATUS: ONLINE</text>',
        "</svg>",
    ]


def main():
    profile = load_profile()
    stats = compute_stats(load_json("contributions.json"))
    for t in THEMES:
        write_svg(t, "header.svg", header(t, profile, stats))
        write_svg(t, "footer.svg", footer(t, profile))
        for slug, num, file, title in SECTIONS:
            write_svg(t, f"titles/{slug}.svg", section_title(t, num, file, title))


if __name__ == "__main__":
    main()
