#!/usr/bin/env python3
"""Generate an animated terminal session that types commands and prints output, on a loop.

Commands come from the "terminal" list in data/profile.json. Output lines may use
{total}, {active}, {current} and {longest} placeholders filled from live stats.
"""
from contrib_stats import compute_stats
from theme import MONO, THEMES, esc, load_json, load_profile, svg_open, window_chrome, write_svg

W = 1200
PAD_X, TOP, LINE_H = 34, 84, 34
CHAR_W = 10.2          # 17px monospace glyph width
TYPE_STEP = 0.055      # seconds per typed character
HOLD = 5.0             # seconds to admire the finished screen before looping


def build_timeline(session):
    """Return [(kind, color, text, start, chars)] plus total duration."""
    lines, clock = [], 0.6
    for block in session:
        cmd = block["cmd"]
        lines.append(("cmd", None, cmd, clock, len(cmd)))
        clock += len(cmd) * TYPE_STEP + 0.35
        for color, text in block["out"]:
            lines.append(("out", color, text, clock, 0))
            clock += 0.12
        clock += 0.55
    lines.append(("prompt", None, "", clock, 0))
    return lines, clock + HOLD


def reveal(cid, y, kind, chars, start, dur, prefix_w):
    """SMIL clip that hides a line until its moment, typing commands char-by-char."""
    times, vals = ["0", f"{start / dur:.4f}"], ["0", f"{prefix_w:.1f}" if kind == "cmd" else str(W)]
    if kind == "cmd":
        for i in range(1, chars + 1):
            times.append(f"{(start + i * TYPE_STEP) / dur:.4f}")
            vals.append(f"{prefix_w + i * CHAR_W:.1f}")
        times.append(f"{(start + chars * TYPE_STEP + 0.05) / dur:.4f}")
        vals.append(str(W))
    return (
        f'<clipPath id="{cid}"><rect x="0" y="{y - 24}" width="0" height="{LINE_H}">'
        f'<animate attributeName="width" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="{";".join(times)}" values="{";".join(vals)}"/></rect></clipPath>'
    )


def render(t, profile, stats):
    fill = {"total": f"{stats['total']:,}", "active": stats["active_days"],
            "current": stats["current"], "longest": stats["longest"]} if stats else {}
    session = []
    for block in profile["terminal"]:
        outs = []
        for color, text in block["out"]:
            try:
                text = text.format(**fill)
            except (KeyError, IndexError):
                continue  # placeholder needs stats we don't have; skip the line
            outs.append((color, text))
        session.append({"cmd": block["cmd"], "out": outs})

    lines, dur = build_timeline(session)
    H = TOP + len(lines) * LINE_H + 26
    prompt_html = (f'<tspan style="fill:{t.ok}">➜</tspan> <tspan style="fill:{t.c1}">~/{esc(profile["handle"])}</tspan> '
                   f'<tspan style="fill:{t.c2}">git:(</tspan><tspan style="fill:{t.c3}">main</tspan>'
                   f'<tspan style="fill:{t.c2}">)</tspan> ')
    prefix_chars = len(f"➜ ~/{profile['handle']} git:(main) ")
    prefix_w = PAD_X + prefix_chars * CHAR_W

    defs, body = [], []
    for i, (kind, color, text, start, chars) in enumerate(lines):
        y = TOP + i * LINE_H
        defs.append(reveal(f"l{i}", y, kind, chars, start, dur, prefix_w))
        if kind == "out":
            body.append(f'<text class="o" x="{PAD_X + 22}" y="{y}" clip-path="url(#l{i})" '
                        f'style="fill:{getattr(t, color, t.text)}">{esc(text)}</text>')
        else:
            body.append(f'<text class="c" x="{PAD_X}" y="{y}" clip-path="url(#l{i})">{prompt_html}{esc(text)}</text>')

    # blinking cursor parked on the final prompt
    last_y = TOP + (len(lines) - 1) * LINE_H
    _, _, _, last_start, _ = lines[-1]
    cursor = (
        f'<rect x="{prefix_w + 2:.0f}" y="{last_y - 17}" width="11" height="22" fill="{t.c1}" opacity="0">'
        f'<animate attributeName="opacity" dur="{dur:.2f}s" repeatCount="indefinite" calcMode="discrete" '
        f'keyTimes="0;{last_start / dur:.4f}" values="0;1"/>'
        f'<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>'
    )
    return [
        svg_open(W, H, "Animated terminal: whoami"),
        f"<defs>{''.join(defs)}</defs>",
        "<style>",
        f".c{{font:600 17px {MONO};fill:{t.text}}}",
        f".o{{font:500 17px {MONO}}}",
        "</style>",
        f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{t.bg}" stroke="{t.line}" stroke-width="1.5"/>',
        window_chrome(t, W, f"{profile['handle']}@github: ~ — zsh"),
        *body,
        cursor,
        "</svg>",
    ]


def main():
    profile = load_profile()
    stats = compute_stats(load_json("contributions.json"))
    for t in THEMES:
        write_svg(t, "terminal.svg", render(t, profile, stats))


if __name__ == "__main__":
    main()
