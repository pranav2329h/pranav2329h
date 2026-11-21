#!/usr/bin/env python3
"""Generate one luxury project card per featured project in data/profile.json.

Live stars / language / last-updated come from data/repos.json (fetch_repos.py).
"""
import textwrap
from datetime import datetime

from theme import (BG, GOLD, GOLD_DEEP, GOLD_LIGHT, IVORY, LINE, MONO, MUTED, PANEL, SANS, SERIF,
                   esc, gold_gradient, load_json, load_profile, svg_open, write_svg)

W, H = 600, 320
PAD = 34


def chip_width(label: str) -> float:
    return len(label) * 7.6 + 24


def card(project, meta):
    repo = project.get("repo")
    status = project.get("status") or ("" if repo else "COMING SOON")
    lines = textwrap.wrap(project["description"], 60)[:3]

    out = [
        svg_open(W, H, f"{project['title']} — {project['tagline']}"),
        "<defs>",
        gold_gradient("gold", shimmer=True, dur="8s"),
        f'<linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.85"/>'
        f'<stop offset="0.45" stop-color="{LINE}"/><stop offset="1" stop-color="{GOLD_DEEP}" stop-opacity="0.7"/></linearGradient>',
        f'<radialGradient id="glow" cx="1" cy="0" r="0.9"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.16"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>',
        f'<linearGradient id="sheen" x1="0" x2="1"><stop offset="0" stop-color="{GOLD_LIGHT}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{GOLD_LIGHT}" stop-opacity="0.9"/><stop offset="1" stop-color="{GOLD_LIGHT}" stop-opacity="0"/></linearGradient>',
        "</defs>",
        "<style>",
        f".kind{{font:600 12px {MONO};letter-spacing:3.5px;fill:{GOLD}}}",
        f".meta{{font:500 12px {MONO};fill:{MUTED};letter-spacing:1px}}",
        f".title{{font:400 34px {SERIF};fill:url(#gold);letter-spacing:.5px}}",
        f".tag{{font:italic 400 16px {SERIF};fill:{GOLD_LIGHT}}}",
        f".desc{{font:400 15.5px {SANS};fill:{IVORY};fill-opacity:.82}}",
        f".chip{{font:500 12px {MONO};fill:{IVORY}}}",
        f".cta{{font:700 12px {MONO};letter-spacing:3px;fill:{GOLD}}}",
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
        ".r{animation:rise .8s ease-out both}",
        f"@keyframes sheen{{0%{{transform:translateX(-200px)}}60%,100%{{transform:translateX({W + 200}px)}}}}",
        ".sh{animation:sheen 6s ease-in-out 1s infinite}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="{BG}" stroke="url(#bd)" stroke-width="1.5"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="url(#glow)"/>',
        f'<clipPath id="top"><rect x="1" y="0" width="{W - 2}" height="3"/></clipPath>',
        f'<g clip-path="url(#top)"><rect class="sh" x="0" y="0" width="160" height="3" fill="url(#sheen)"/></g>',
        f'<g class="r"><text class="kind" x="{PAD}" y="48">{esc(project["kind"])}</text>',
    ]

    right = ""
    if status:
        right = f'<tspan style="fill:{GOLD_LIGHT}">●</tspan> {esc(status)}'
    elif meta and meta.get("stars"):
        # Only surface social proof once there is some.
        right = f'<tspan style="fill:{GOLD}">★</tspan> {meta["stars"]}'
        if meta.get("forks"):
            right += f"  ·  {meta['forks']} forks"
    if right:
        out.append(f'<text class="meta" x="{W - PAD}" y="48" text-anchor="end">{right}</text>')
    out.append("</g>")

    out.append(f'<g class="r" style="animation-delay:.15s"><text class="title" x="{PAD}" y="98">{esc(project["title"])}</text>')
    out.append(f'<text class="tag" x="{PAD}" y="126">{esc(project["tagline"])}</text></g>')
    out.append(f'<g class="r" style="animation-delay:.3s">')
    for i, line in enumerate(lines):
        out.append(f'<text class="desc" x="{PAD}" y="{164 + i * 23}">{esc(line)}</text>')
    out.append("</g>")

    # tech chips (single row; drop any that would overflow)
    x, y = PAD, 236
    out.append(f'<g class="r" style="animation-delay:.45s">')
    for label in project["stack"]:
        w = chip_width(label)
        if x + w > W - PAD:
            break
        out.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{PANEL}" '
                   f'stroke="{GOLD}" stroke-opacity="0.35"/>')
        out.append(f'<text class="chip" x="{x + w / 2:.0f}" y="{y + 17}" text-anchor="middle">{esc(label)}</text>')
        x += w + 8
    out.append("</g>")

    # footer
    out.append(f'<line x1="{PAD}" y1="282" x2="{W - PAD}" y2="282" stroke="{LINE}"/>')
    left_bits = []
    if meta and meta.get("language"):
        left_bits.append(f'<tspan style="fill:{GOLD}">◆</tspan> {esc(meta["language"])}')
    if meta and meta.get("pushed_at"):
        pushed = datetime.fromisoformat(meta["pushed_at"].replace("Z", "+00:00"))
        left_bits.append(f"updated {pushed.strftime('%b %Y')}")
    if left_bits:
        joined = "  ·  ".join(left_bits)
        out.append(f'<text class="meta" x="{PAD}" y="304">{joined}</text>')
    cta = "VIEW REPOSITORY  →" if repo else "COMING SOON"
    out.append(f'<text class="cta" x="{W - PAD}" y="304" text-anchor="end">{cta}</text>')
    out.append("</svg>")
    return out


def main():
    profile = load_profile()
    repos = load_json("repos.json", {}) or {}
    for project in profile["projects"]:
        meta = repos.get(project.get("repo") or "")
        write_svg(f"projects/{project['slug']}.svg", card(project, meta))


if __name__ == "__main__":
    main()
