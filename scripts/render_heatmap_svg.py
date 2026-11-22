#!/usr/bin/env python3
"""Render data/contributions.json as an animated contribution matrix (dark + light)."""
from datetime import date, timedelta

from contrib_stats import compute_stats
from theme import MONO, THEMES, esc, load_json, neon_gradient, svg_open, write_svg

W = 1200
CELL, GAP = 16, 4
STEP = CELL + GAP
GRID_TOP = 176
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


DIGIT_W, DIGIT_LH = 25, 48   # 42px monospace digit advance / roll line height


def odometer(oid, value, cx, baseline, color, delay):
    """Odometer-style counter: every digit spins a full turn then lands on its value."""
    width = sum(DIGIT_W if ch.isdigit() else DIGIT_W * 0.55 for ch in value)
    x = cx - width / 2
    parts = []
    for pos, ch in enumerate(value):
        if not ch.isdigit():
            parts.append(f'<text class="odo" x="{x:.1f}" y="{baseline}" style="fill:{color}">{esc(ch)}</text>')
            x += DIGIT_W * 0.55
            continue
        seq = list(range(10)) + list(range(int(ch) + 1))      # one full spin, then up to the digit
        col = "".join(f'<tspan x="{x:.1f}" y="{baseline + k * DIGIT_LH}">{d}</tspan>' for k, d in enumerate(seq))
        dur = 1.4 + pos * 0.25
        parts.append(
            f'<clipPath id="{oid}d{pos}"><rect x="{x - 2:.1f}" y="{baseline - 40}" width="{DIGIT_W + 4}" height="{DIGIT_LH}"/></clipPath>'
            f'<g clip-path="url(#{oid}d{pos})"><text class="odo roll" style="fill:{color};--to:-{(len(seq) - 1) * DIGIT_LH}px;'
            f'animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s">{col}</text></g>'
        )
        x += DIGIT_W
    return "".join(parts)


def render(t, payload, stats):
    levels = {d["date"]: int(d["level"]) for d in payload["days"]}
    first = date.fromisoformat(stats["first"])
    last = date.fromisoformat(stats["last"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday
    weeks = (last - start).days // 7 + 1

    grid_w = weeks * STEP - GAP
    left = (W - grid_w) / 2 + 18
    grid_h = 7 * STEP - GAP
    H = GRID_TOP + grid_h + 74

    out = [
        svg_open(W, H, f"{stats['total']} contributions in the last year"),
        "<defs>",
        neon_gradient(t, "neon", dur="6s"),
        f'<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="{t.c1}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{t.c1}" stop-opacity="0.28"/>'
        f'<stop offset="1" stop-color="{t.c1}" stop-opacity="0"/></linearGradient>',
        '<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        f'<clipPath id="gridClip"><rect x="{left}" y="{GRID_TOP}" width="{grid_w}" height="{grid_h}"/></clipPath>',
        "</defs>",
        "<style>",
        f"text{{font-family:{MONO}}}",
        f".lbl{{font-size:11px;font-weight:700;fill:{t.muted};letter-spacing:2px}}",
        f".odo{{font:800 42px {MONO}}}",
        "@keyframes roll{from{transform:translateY(0)}to{transform:translateY(var(--to))}}",
        ".roll{animation:roll 1.6s cubic-bezier(.15,.85,.25,1) both}",
        f".unit{{font-size:12px;fill:{t.muted}}}",
        f".axis{{font-size:12px;fill:{t.muted}}}",
        "@keyframes reveal{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:none}}",
        ".c{transform-box:fill-box;transform-origin:center;animation:reveal .6s cubic-bezier(.2,.8,.2,1) both}",
        "@keyframes twinkle{0%,100%{opacity:1}50%{opacity:.55}}.hot{animation:reveal .6s both,twinkle 2.4s ease-in-out 1.5s infinite}",
        f"@keyframes sweep{{from{{transform:translateX(0)}}to{{transform:translateX({grid_w + 160}px)}}}}",
        ".scan{animation:sweep 6s cubic-bezier(.45,0,.55,1) 1.5s infinite}",
        "@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}.up{animation:up .8s ease-out both}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t.bg}" stroke="{t.line}"/>',
    ]

    blocks = [
        ("CONTRIBUTIONS", f"{stats['total']:,}", "last 12 months"),
        ("ACTIVE DAYS", f"{stats['active_days']}", f"of {payload.get('day_count', len(levels))}"),
        ("CURRENT STREAK", f"{stats['current']}", "days"),
        ("LONGEST STREAK", f"{stats['longest']}", "days"),
        ("BEST DAY", f"{stats['best_count']}", date.fromisoformat(stats["best_date"]).strftime("%b %d, %Y")),
    ]
    col = (W - 80) / len(blocks)
    colors = [t.c1, t.c2, t.c3, t.c1, t.c2]
    for i, (label, value, unit) in enumerate(blocks):
        cx = 40 + col * i + col / 2
        out.append(f'<g class="up" style="animation-delay:{i * 0.12:.2f}s">'
                   f'<text class="lbl" x="{cx}" y="50" text-anchor="middle">{label}</text>'
                   f'<text class="unit" x="{cx}" y="126" text-anchor="middle">{esc(unit)}</text></g>')
        out.append(odometer(f"o{i}", value, cx, 100, colors[i], 0.3 + i * 0.15))
        if i:
            x = 40 + col * i
            out.append(f'<line x1="{x}" y1="36" x2="{x}" y2="126" stroke="{t.line}"/>')

    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text class="axis" x="{left - 12}" y="{GRID_TOP + row * STEP + 12}" text-anchor="end">{label}</text>')
    prev_month = None
    for week in range(weeks):
        sunday = start + timedelta(weeks=week)
        month = (sunday + timedelta(days=6)).month if week == 0 else sunday.month
        if month != prev_month and week < weeks - 2:
            out.append(f'<text class="axis" x="{left + week * STEP}" y="{GRID_TOP - 12}">{MONTHS[month - 1]}</text>')
        prev_month = month

    for week in range(weeks):
        for day in range(7):
            current = start + timedelta(days=week * 7 + day)
            if current < first or current > last:
                continue
            level = levels.get(current.isoformat(), 0)
            x = left + week * STEP
            y = GRID_TOP + day * STEP
            cls, extra = ("c hot", ' filter="url(#glow)"') if level == 4 else ("c", "")
            out.append(
                f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="4" fill="{t.heat[level]}"'
                f'{extra} style="animation-delay:{(week + day) * 0.014:.3f}s"/>'
            )

    out.append(
        f'<g clip-path="url(#gridClip)"><rect class="scan" x="{left - 160}" y="{GRID_TOP}" width="120" '
        f'height="{grid_h}" fill="url(#scan)"/></g>'
    )

    ly = GRID_TOP + grid_h + 40
    out.append(f'<text class="axis" x="{left}" y="{ly}">Less</text>')
    for i, color in enumerate(t.heat):
        out.append(f'<rect x="{left + 42 + i * STEP}" y="{ly - 12}" width="{CELL - 2}" height="{CELL - 2}" rx="3" fill="{color}"/>')
    out.append(f'<text class="axis" x="{left + 42 + 5 * STEP + 6}" y="{ly}">More</text>')
    updated = esc(payload.get("fetched_at", "")[:10])
    out.append(
        f'<text class="axis" x="{left + grid_w}" y="{ly}" text-anchor="end">'
        f'<tspan style="fill:{t.ok}">●</tspan> auto-refreshed daily · updated {updated}</text>'
    )
    out.append("</svg>")
    return out


def main():
    payload = load_json("contributions.json")
    if not payload or not payload.get("days"):
        raise SystemExit("Missing data/contributions.json. Run fetch_contributions.py first.")
    stats = compute_stats(payload)
    for t in THEMES:
        write_svg(t, "contrib-heatmap.svg", render(t, payload, stats))


if __name__ == "__main__":
    main()
