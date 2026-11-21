#!/usr/bin/env python3
"""Generate the animated tech orbit: skills travel around three elliptical rings."""
from theme import MONO, SANS, THEMES, esc, load_profile, neon_gradient, svg_open, write_svg

W, H = 1200, 480
CX, CY = W / 2, H / 2
RINGS = [(250, 92, 26), (410, 150, 38), (550, 206, 52)]  # rx, ry, seconds per lap


def ellipse_path(rx, ry):
    return (f"M{CX - rx} {CY} a{rx} {ry} 0 1 1 {2 * rx} 0 a{rx} {ry} 0 1 1 {-2 * rx} 0")


def render(t, profile):
    ring_colors = [t.c1, t.c2, t.c3]
    out = [
        svg_open(W, H, "Tech stack orbit: " + ", ".join(s for ring in profile["orbit"] for s in ring)),
        "<defs>",
        neon_gradient(t, "neon", dur="4s"),
        f'<radialGradient id="core"><stop offset="0" stop-color="{t.c2}" stop-opacity="{t.glow * 1.6:.2f}"/>'
        f'<stop offset="1" stop-color="{t.c2}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{t.line}"/></pattern>',
        "</defs>",
        "<style>",
        f".pill{{font:600 14px {MONO};fill:{t.text}}}",
        f".core{{font:800 40px {SANS}}}",
        f".sub{{font:600 12px {MONO};fill:{t.muted};letter-spacing:3px}}",
        "@keyframes dash{to{stroke-dashoffset:-200}}.ring{animation:dash 12s linear infinite}",
        "@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(1.12)}}",
        f".glow{{transform-origin:{CX}px {CY}px;animation:breathe 4s ease-in-out infinite}}",
        "@keyframes spin{to{transform:rotate(360deg)}}",
        f".spin{{transform-origin:{CX}px {CY}px;animation:spin 10s linear infinite}}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{t.bg}" stroke="{t.line}"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#dots)" opacity=".6"/>',
    ]
    for (rx, ry, _), color in zip(RINGS, ring_colors):
        out.append(f'<ellipse class="ring" cx="{CX}" cy="{CY}" rx="{rx}" ry="{ry}" fill="none" stroke="{color}" '
                   f'stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="6 10"/>')

    # pulsing core
    out += [
        f'<circle class="glow" cx="{CX}" cy="{CY}" r="120" fill="url(#core)"/>',
        f'<circle cx="{CX}" cy="{CY}" r="58" fill="{t.panel}" stroke="{t.line}" stroke-width="1.5"/>',
        f'<circle class="spin" cx="{CX}" cy="{CY}" r="66" fill="none" stroke="url(#neon)" stroke-width="3" '
        f'stroke-dasharray="90 325" stroke-linecap="round"/>',
        f'<text class="core" x="{CX}" y="{CY + 14}" text-anchor="middle" fill="url(#neon)">&lt;/&gt;</text>',
        f'<text class="sub" x="{CX}" y="{CY + 100}" text-anchor="middle">{esc(profile["handle"].upper())}.STACK</text>',
    ]

    # labels riding the rings (animateMotion keeps them upright)
    for ring_idx, ((rx, ry, lap), skills) in enumerate(zip(RINGS, profile["orbit"])):
        path = ellipse_path(rx, ry)
        color = ring_colors[ring_idx]
        reverse = ring_idx % 2 == 1
        for i, skill in enumerate(skills):
            w = len(skill) * 8.6 + 42
            offset = lap * i / len(skills)
            motion = (f'<animateMotion dur="{lap}s" repeatCount="indefinite" begin="-{offset:.2f}s" path="{path}"'
                      + (' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if reverse else "") + "/>")
            out.append(
                f"<g>{motion}"
                f'<rect x="{-w / 2:.0f}" y="-16" width="{w:.0f}" height="32" rx="16" fill="{t.panel}" stroke="{color}" stroke-opacity=".7"/>'
                f'<circle cx="{-w / 2 + 16:.0f}" cy="0" r="4" fill="{color}"/>'
                f'<text class="pill" x="{-w / 2 + 28:.0f}" y="5">{esc(skill)}</text></g>'
            )
    out.append("</svg>")
    return out


def main():
    profile = load_profile()
    for t in THEMES:
        write_svg(t, "orbit.svg", render(t, profile))


if __name__ == "__main__":
    main()
