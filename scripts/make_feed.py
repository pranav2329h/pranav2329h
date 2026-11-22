#!/usr/bin/env python3
"""Generate the live commit feed: my latest real commits rolling upward like credits."""
from datetime import date

from theme import LANG_COLORS, MONO, THEMES, esc, load_json, load_profile, svg_open, window_chrome, write_svg

W = 1200
ROW_H = 52
VIEW_TOP, VIEW_H = 92, 364
SECONDS_PER_ROW = 2.4


def ago(day: str, today: date) -> str:
    days = (today - date.fromisoformat(day)).days
    if days <= 0:
        return "today"
    if days == 1:
        return "yesterday"
    if days < 30:
        return f"{days} days ago"
    months = days // 30
    return f"{months} month{'s' if months > 1 else ''} ago"


def render(t, profile, commits, today):
    repos = load_json("repos.json", {}) or {}
    rows = []
    for i, c in enumerate(commits * 2):  # two copies -> seamless loop
        y = VIEW_TOP + 34 + i * ROW_H
        msg = c["message"] if len(c["message"]) <= 66 else c["message"][:63] + "…"
        lang = (repos.get(c["repo"]) or {}).get("language")
        dot = LANG_COLORS.get(lang, t.c2)
        rows.append(
            f'<g><circle cx="58" cy="{y - 5}" r="6" fill="{t.bg}" stroke="{dot}" stroke-width="3"/>'
            f'<text class="sha" x="80" y="{y}">{esc(c["sha"])}</text>'
            f'<text class="repo" x="170" y="{y}">{esc(c["repo"][:24])}</text>'
            f'<text class="msg" x="420" y="{y}">{esc(msg)}</text>'
            f'<text class="when" x="{W - 40}" y="{y}" text-anchor="end">{ago(c["date"], today)}</text></g>'
        )
    loop_h = len(commits) * ROW_H
    H = VIEW_TOP + VIEW_H + 54
    return [
        svg_open(W, H, "Live feed of recent commits: " + "; ".join(c["message"] for c in commits[:5])),
        "<defs>",
        f'<clipPath id="view"><rect x="0" y="{VIEW_TOP}" width="{W}" height="{VIEW_H}"/></clipPath>',
        '<linearGradient id="v" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".16" stop-color="#fff"/><stop offset=".84" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<mask id="fade"><rect x="0" y="{VIEW_TOP}" width="{W}" height="{VIEW_H}" fill="url(#v)"/></mask>',
        "</defs>",
        "<style>",
        f".sha{{font:700 16px {MONO};fill:{t.c3}}}",
        f".repo{{font:700 16px {MONO};fill:{t.c2}}}",
        f".msg{{font:500 16px {MONO};fill:{t.text}}}",
        f".when{{font:500 14px {MONO};fill:{t.muted}}}",
        f".cmd{{font:600 15px {MONO};fill:{t.text}}}",
        f"@keyframes roll{{from{{transform:translateY(0)}}to{{transform:translateY(-{loop_h}px)}}}}",
        f".roll{{animation:roll {len(commits) * SECONDS_PER_ROW:.1f}s linear infinite}}",
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.2}}.pulse{animation:pulse 1.4s ease-in-out infinite}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t.bg}" stroke="{t.line}" stroke-width="1.5"/>',
        window_chrome(t, W, f"{profile['handle']}@github: ~ — git log --all --author={profile['handle']}"),
        f'<text class="cmd" x="40" y="76"><tspan style="fill:{t.ok}">➜</tspan> <tspan style="fill:{t.c1}">git log</tspan> '
        f'--all --oneline --no-merges <tspan style="fill:{t.muted}"># live feed, refreshed daily</tspan></text>',
        f'<g clip-path="url(#view)" mask="url(#fade)">',
        f'<line x1="58" y1="{VIEW_TOP}" x2="58" y2="{VIEW_TOP + VIEW_H}" stroke="{t.line}" stroke-width="2"/>',
        f'<g class="roll">{"".join(rows)}</g></g>',
        f'<line x1="40" y1="{H - 44}" x2="{W - 40}" y2="{H - 44}" stroke="{t.line}"/>',
        f'<text class="when" x="40" y="{H - 18}"><tspan class="pulse" style="fill:{t.ok}">●</tspan> LIVE · '
        f'{len(commits)} latest hand-written commits across public repos</text>',
        f'<text class="when" x="{W - 40}" y="{H - 18}" text-anchor="end">bots &amp; merges filtered out</text>',
        "</svg>",
    ]


def main():
    commits = load_json("activity.json")
    if not commits:
        print("No data/activity.json; skipping commit feed")
        return
    profile = load_profile()
    today = date.today()
    for t in THEMES:
        write_svg(t, "feed.svg", render(t, profile, commits, today))


if __name__ == "__main__":
    main()
