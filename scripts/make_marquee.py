#!/usr/bin/env python3
"""Generate the infinite scrolling ticker: two bands sliding in opposite directions."""
from theme import MONO, SANS, THEMES, esc, load_profile, neon_gradient, svg_open, write_svg

W, H = 1200, 150


def band(t, items, y, size, cls, outline, char_w):
    """One seamless row: the item strip is repeated so it can slide exactly one strip width."""
    sep = "  ✦  "
    strip = sep.join(items) + sep
    strip_w = len(strip) * char_w
    copies = int(W // strip_w) + 2
    style = (f"fill:none;stroke:url(#neon);stroke-width:1.2" if outline else f"fill:{t.text}")
    texts = "".join(
        f'<text x="{i * strip_w:.1f}" y="{y}" style="{style}" xml:space="preserve">{esc(strip)}</text>'
        for i in range(copies)
    )
    return f'<g class="{cls}" style="--w:{strip_w:.1f}px;font-size:{size}px">{texts}</g>', strip_w


def render(t, profile):
    top, bottom = profile["marquee"]
    row1, w1 = band(t, top, 62, 34, "b1", True, 34 * 0.62)
    row2, w2 = band(t, bottom, 118, 18, "b2", False, 18 * 0.6)
    return [
        svg_open(W, H, "Scrolling ticker: " + " · ".join(top + bottom)),
        "<defs>",
        neon_gradient(t, "neon", dur="4s"),
        '<linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".08" stop-color="#fff"/><stop offset=".92" stop-color="#fff"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<mask id="fade"><rect width="{W}" height="{H}" fill="url(#edge)"/></mask>',
        "</defs>",
        "<style>",
        f".b1 text{{font-family:{SANS};font-weight:900;letter-spacing:1px}}",
        f".b2 text{{font-family:{MONO};font-weight:600;letter-spacing:0}}",
        f"@keyframes left{{from{{transform:translateX(0)}}to{{transform:translateX(-{w1:.1f}px)}}}}",
        f"@keyframes right{{from{{transform:translateX(-{w2:.1f}px)}}to{{transform:translateX(0)}}}}",
        f".b1{{animation:left {w1 / 45:.1f}s linear infinite}}.b2{{animation:right {w2 / 30:.1f}s linear infinite}}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="16" fill="{t.panel}"/>',
        f'<rect y="84" width="{W}" height="54" fill="{t.bg}" opacity=".7"/>',
        f'<g mask="url(#fade)">{row1}{row2}</g>',
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{t.line}"/>',
        "</svg>",
    ]


def main():
    profile = load_profile()
    for t in THEMES:
        write_svg(t, "marquee.svg", render(t, profile))


if __name__ == "__main__":
    main()
