#!/usr/bin/env python3
"""Generate the animated journey timeline from real dates.

Milestones: GitHub join date, each featured project's repo creation date, and
"now" with the live contribution count. The line draws itself left to right and
each milestone pops in as the line reaches it.
"""
from datetime import datetime

from contrib_stats import compute_stats
from theme import MONO, SANS, THEMES, esc, load_json, load_profile, neon_gradient, svg_open, write_svg

W, H = 1200, 330
AXIS_Y = 162
DRAW = 3.2  # seconds for the line to cross the card


def milestones(profile):
    repos = load_json("repos.json", {}) or {}
    user = load_json("user.json", {}) or {}
    stats = compute_stats(load_json("contributions.json"))
    events = []
    if user.get("created_at"):
        events.append((user["created_at"], "Hello, GitHub", "first repo pushed"))
    for p in profile["projects"]:
        meta = repos.get(p.get("repo") or "")
        if meta and meta.get("created_at"):
            events.append((meta["created_at"], p["title"], p["tagline"]))
    events.sort(key=lambda e: e[0])
    now = f"{stats['total']:,} contributions this year" if stats else "still shipping"
    events.append((None, "Now", now))
    return [(datetime.fromisoformat(d.replace("Z", "+00:00")).strftime("%b %Y") if d else "TODAY", title, sub)
            for d, title, sub in events]


def render(t, events):
    left, right = 160, W - 160
    step = (right - left) / (len(events) - 1)
    colors = [t.c1, t.c2, t.c3]
    out = [
        svg_open(W, H, "Journey: " + "; ".join(f"{d} {title}" for d, title, _ in events)),
        "<defs>",
        neon_gradient(t, "neon", shimmer=False),
        f'<linearGradient id="axis" x1="{left}" x2="{right}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{t.c1}"/><stop offset=".5" stop-color="{t.c2}"/><stop offset="1" stop-color="{t.c3}"/></linearGradient>',
        '<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter>',
        "</defs>",
        "<style>",
        f".date{{font:700 13px {MONO};letter-spacing:2px}}",
        f".title{{font:800 19px {SANS};fill:{t.text}}}",
        f".sub{{font:500 13px {MONO};fill:{t.muted}}}",
        f"@keyframes draw{{from{{stroke-dashoffset:{right - left}}}to{{stroke-dashoffset:0}}}}",
        f".line{{stroke-dasharray:{right - left};animation:draw {DRAW}s cubic-bezier(.45,0,.25,1) .3s both}}",
        "@keyframes pop{0%{opacity:0;transform:scale(0)}70%{transform:scale(1.25)}100%{opacity:1;transform:none}}",
        ".node{transform-box:fill-box;transform-origin:center;animation:pop .6s ease-out both}",
        "@keyframes rise{from{opacity:0;transform:translateY(var(--d))}to{opacity:1;transform:none}}",
        ".lab{animation:rise .7s ease-out both}",
        "@keyframes ping{0%{transform:scale(1);opacity:.7}100%{transform:scale(3.2);opacity:0}}",
        ".ping{transform-box:fill-box;transform-origin:center;animation:ping 1.8s ease-out infinite}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t.bg}" stroke="{t.line}"/>',
        f'<line x1="{left}" y1="{AXIS_Y}" x2="{right}" y2="{AXIS_Y}" stroke="{t.line}" stroke-width="4" stroke-linecap="round"/>',
        f'<line class="line" x1="{left}" y1="{AXIS_Y}" x2="{right}" y2="{AXIS_Y}" stroke="url(#axis)" stroke-width="4" stroke-linecap="round"/>',
        # a comet keeps travelling the finished line (SMIL for broad renderer support)
        f'<circle r="6" fill="{t.c1}" filter="url(#glow)" opacity="0"><set attributeName="opacity" to="1" begin="{DRAW + .5}s"/>'
        f'<animateMotion path="M{left} {AXIS_Y} H{right}" dur="4s" begin="{DRAW + .5}s" repeatCount="indefinite"/></circle>',
    ]
    for i, (when, title, sub) in enumerate(events):
        x = left + i * step
        delay = 0.3 + DRAW * (x - left) / (right - left)
        color = colors[i % 3]
        up = i % 2 == 0
        ty = AXIS_Y - 92 if up else AXIS_Y + 58
        last = i == len(events) - 1
        out.append(f'<line x1="{x}" y1="{AXIS_Y + (-14 if up else 14)}" x2="{x}" y2="{AXIS_Y + (-36 if up else 36)}" '
                   f'stroke="{t.line}" stroke-width="2" stroke-dasharray="3 4"/>')
        if last:
            out.append(f'<circle class="ping" cx="{x}" cy="{AXIS_Y}" r="10" fill="{t.ok}" style="animation-delay:{delay:.2f}s"/>')
        out.append(f'<circle class="node" cx="{x}" cy="{AXIS_Y}" r="11" fill="{t.bg}" stroke="{t.ok if last else color}" '
                   f'stroke-width="4" style="animation-delay:{delay:.2f}s"/>')
        out.append(
            f'<g class="lab" style="--d:{-12 if up else 12}px;animation-delay:{delay + .1:.2f}s">'
            f'<text class="date" x="{x}" y="{ty}" text-anchor="middle" style="fill:{t.ok if last else color}">{esc(when.upper())}</text>'
            f'<text class="title" x="{x}" y="{ty + 26}" text-anchor="middle">{esc(title)}</text>'
            f'<text class="sub" x="{x}" y="{ty + 46}" text-anchor="middle">{esc(sub)}</text></g>'
        )
    out.append("</svg>")
    return out


def main():
    events = milestones(load_profile())
    for t in THEMES:
        write_svg(t, "timeline.svg", render(t, events))


if __name__ == "__main__":
    main()
