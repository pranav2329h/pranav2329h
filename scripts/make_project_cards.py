#!/usr/bin/env python3
"""Generate one animated project card per featured project in data/profile.json.

Live stars / language / last-updated come from data/repos.json (fetch_repos.py).
"""
import textwrap
from datetime import datetime

from theme import (LANG_COLORS, MONO, SANS, THEMES, esc, load_json, load_profile, neon_gradient,
                   svg_open, write_svg)

W, H = 600, 330
PAD = 32


def chip_width(label: str) -> float:
    return len(label) * 8.1 + 26


def card(t, project, meta):
    repo = project.get("repo")
    status = project.get("status") or ("" if repo else "COMING SOON")
    lines = textwrap.wrap(project["description"], 56)[:3]

    out = [
        svg_open(W, H, f"{project['title']} — {project['tagline']}"),
        "<defs>",
        neon_gradient(t, "neon", dur="5s"),
        f'<radialGradient id="glow" cx="1" cy="0" r="1"><stop offset="0" stop-color="{t.c2}" stop-opacity="{t.glow * .6:.2f}"/>'
        f'<stop offset="1" stop-color="{t.c2}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="{t.line}"/></pattern>',
        "</defs>",
        "<style>",
        f".kind{{font:700 12px {MONO};letter-spacing:2px;fill:{t.c1}}}",
        f".meta{{font:600 13px {MONO};fill:{t.muted}}}",
        f".title{{font:800 32px {SANS};fill:{t.text}}}",
        f".tag{{font:600 15px {MONO};fill:{t.c2}}}",
        f".desc{{font:400 17px {SANS};fill:{t.text};fill-opacity:.82}}",
        f".chip{{font:600 13px {MONO};fill:{t.text}}}",
        f".cta{{font:800 13px {MONO};letter-spacing:1px}}",
        "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}.r{animation:rise .7s ease-out both}",
        "@keyframes trail{to{stroke-dashoffset:-1000}}.trail{animation:trail 5s linear infinite}",
        "@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}.go{animation:nudge 1.4s ease-in-out infinite}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 1.6s ease-in-out infinite}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t.bg}"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#dots)" opacity=".55"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#glow)"/>',
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="{t.line}" stroke-width="1.5"/>',
        f'<rect class="trail" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="none" stroke="url(#neon)" '
        f'stroke-width="2.5" pathLength="1000" stroke-dasharray="140 860" stroke-linecap="round"/>',
        f'<rect x="{PAD}" y="34" width="4" height="16" rx="2" fill="url(#neon)"/>',
        f'<g class="r"><text class="kind" x="{PAD + 14}" y="47">{esc(project["kind"])}</text>',
    ]

    right = ""
    if status:
        right = f'<tspan class="pulse" style="fill:{t.c3}">●</tspan> {esc(status)}'
    elif meta and meta.get("stars"):
        right = f'<tspan style="fill:{t.c1}">★</tspan> {meta["stars"]}'
        if meta.get("forks"):
            right += f"  ·  {meta['forks']} forks"
    if right:
        out.append(f'<text class="meta" x="{W - PAD}" y="47" text-anchor="end">{right}</text>')
    out.append("</g>")

    out.append(f'<g class="r" style="animation-delay:.12s"><text class="title" x="{PAD}" y="96">{esc(project["title"])}</text>')
    out.append(f'<text class="tag" x="{PAD}" y="124"><tspan style="fill:{t.c1}">//</tspan> {esc(project["tagline"])}</text></g>')
    out.append('<g class="r" style="animation-delay:.24s">')
    for i, line in enumerate(lines):
        out.append(f'<text class="desc" x="{PAD}" y="{162 + i * 25}">{esc(line)}</text>')
    out.append("</g>")

    x, y = PAD, 240
    out.append('<g class="r" style="animation-delay:.36s">')
    for label in project["stack"]:
        w = chip_width(label)
        if x + w > W - PAD:
            break
        out.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="28" rx="8" fill="{t.panel}" stroke="{t.line}"/>')
        out.append(f'<text class="chip" x="{x + w / 2:.0f}" y="{y + 19}" text-anchor="middle">{esc(label)}</text>')
        x += w + 8
    out.append("</g>")

    out.append(f'<line x1="{PAD}" y1="288" x2="{W - PAD}" y2="288" stroke="{t.line}"/>')
    bits = []
    if meta and meta.get("language"):
        lang = meta["language"]
        bits.append(f'<tspan style="fill:{LANG_COLORS.get(lang, t.c1)}">●</tspan> {esc(lang)}')
    if meta and meta.get("pushed_at"):
        pushed = datetime.fromisoformat(meta["pushed_at"].replace("Z", "+00:00"))
        bits.append(f"updated {pushed.strftime('%b %Y')}")
    if bits:
        joined = "  ·  ".join(bits)
        out.append(f'<text class="meta" x="{PAD}" y="313">{joined}</text>')
    if repo:
        out.append(f'<g class="go"><text class="cta" x="{W - PAD}" y="313" text-anchor="end" fill="url(#neon)">VIEW REPO →</text></g>')
    else:
        out.append(f'<text class="cta" x="{W - PAD}" y="313" text-anchor="end" style="fill:{t.muted}">COMING SOON</text>')
    out.append("</svg>")
    return out


def main():
    profile = load_profile()
    repos = load_json("repos.json", {}) or {}
    for t in THEMES:
        for project in profile["projects"]:
            meta = repos.get(project.get("repo") or "")
            write_svg(t, f"projects/{project['slug']}.svg", card(t, project, meta))


if __name__ == "__main__":
    main()
