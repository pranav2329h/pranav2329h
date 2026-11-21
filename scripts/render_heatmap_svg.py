#!/usr/bin/env python3
"""Render data/contributions.json as an animated gold contribution matrix."""
from datetime import date, timedelta

from contrib_stats import compute_stats
from theme import (BG, GOLD, GOLD_LIGHT, HEAT, LINE, MONO, MUTED, SERIF,
                   esc, gold_gradient, load_json, svg_open, write_svg)

W = 1200
CELL, GAP = 16, 4
STEP = CELL + GAP
GRID_TOP = 170
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def main():
    payload = load_json("contributions.json")
    if not payload or not payload.get("days"):
        raise SystemExit("Missing data/contributions.json. Run fetch_contributions.py first.")
    stats = compute_stats(payload)
    levels = {d["date"]: int(d["level"]) for d in payload["days"]}
    counts = {d["date"]: d.get("count") for d in payload["days"]}

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
        gold_gradient("gold", shimmer=True, dur="9s"),
        f'<linearGradient id="scan" x1="0" x2="1"><stop offset="0" stop-color="{GOLD_LIGHT}" stop-opacity="0"/>'
        f'<stop offset="0.5" stop-color="{GOLD_LIGHT}" stop-opacity="0.22"/>'
        f'<stop offset="1" stop-color="{GOLD_LIGHT}" stop-opacity="0"/></linearGradient>',
        '<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="2.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
        f'<clipPath id="gridClip"><rect x="{left}" y="{GRID_TOP}" width="{grid_w}" height="{grid_h}"/></clipPath>',
        "</defs>",
        "<style>",
        f"text{{font-family:{MONO}}}",
        f".lbl{{font-size:11px;fill:{MUTED};letter-spacing:3px}}",
        f".val{{font:400 38px {SERIF};fill:url(#gold)}}",
        f".unit{{font-size:12px;fill:{MUTED}}}",
        f".axis{{font-size:12px;fill:{MUTED}}}",
        ".c{animation:reveal .6s ease-out both}",
        "@keyframes reveal{from{opacity:0;transform:scale(.4)}to{opacity:1;transform:none}}",
        ".c{transform-box:fill-box;transform-origin:center}",
        "@keyframes sweep{from{transform:translateX(0)}to{transform:translateX(" + f"{grid_w + 160}" + "px)}}",
        ".scan{animation:sweep 7s cubic-bezier(.45,0,.55,1) 1.5s infinite}",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{BG}" stroke="{LINE}"/>',
    ]

    # headline stats band
    blocks = [
        ("CONTRIBUTIONS", f"{stats['total']:,}", "last 12 months"),
        ("ACTIVE DAYS", f"{stats['active_days']}", f"of {payload.get('day_count', len(levels))}"),
        ("CURRENT STREAK", f"{stats['current']}", "days"),
        ("LONGEST STREAK", f"{stats['longest']}", "days"),
        ("BEST DAY", f"{stats['best_count']}", date.fromisoformat(stats["best_date"]).strftime("%b %d, %Y")),
    ]
    col = (W - 80) / len(blocks)
    for i, (label, value, unit) in enumerate(blocks):
        cx = 40 + col * i + col / 2
        out.append(f'<text class="lbl" x="{cx}" y="50" text-anchor="middle">{label}</text>')
        out.append(f'<text class="val" x="{cx}" y="98" text-anchor="middle">{value}</text>')
        out.append(f'<text class="unit" x="{cx}" y="122" text-anchor="middle">{esc(unit)}</text>')
        if i:
            x = 40 + col * i
            out.append(f'<line x1="{x}" y1="38" x2="{x}" y2="122" stroke="{LINE}"/>')

    # weekday + month axis
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text class="axis" x="{left - 12}" y="{GRID_TOP + row * STEP + 12}" text-anchor="end">{label}</text>')
    prev_month = None
    for week in range(weeks):
        sunday = start + timedelta(weeks=week)
        month = (sunday + timedelta(days=6)).month if week == 0 else sunday.month
        if month != prev_month and week < weeks - 2:
            out.append(f'<text class="axis" x="{left + week * STEP}" y="{GRID_TOP - 12}">{MONTHS[month - 1]}</text>')
        prev_month = month

    # cells
    for week in range(weeks):
        for day in range(7):
            current = start + timedelta(days=week * 7 + day)
            if current < first or current > last:
                continue
            key = current.isoformat()
            level = levels.get(key, 0)
            x = left + week * STEP
            y = GRID_TOP + day * STEP
            extra = ' filter="url(#glow)"' if level == 4 else ""
            out.append(
                f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3.5" fill="{HEAT[level]}"'
                f'{extra} style="animation-delay:{(week + day) * 0.014:.3f}s"/>'
            )

    # scanning sheen
    out.append(
        f'<g clip-path="url(#gridClip)"><rect class="scan" x="{left - 160}" y="{GRID_TOP}" width="120" '
        f'height="{grid_h}" fill="url(#scan)"/></g>'
    )

    # legend + footer
    ly = GRID_TOP + grid_h + 40
    out.append(f'<text class="axis" x="{left}" y="{ly}">Less</text>')
    for i, color in enumerate(HEAT):
        out.append(f'<rect x="{left + 42 + i * STEP}" y="{ly - 12}" width="{CELL - 2}" height="{CELL - 2}" rx="3" fill="{color}"/>')
    out.append(f'<text class="axis" x="{left + 42 + 5 * STEP + 6}" y="{ly}">More</text>')
    updated = esc(payload.get("fetched_at", "")[:10])
    out.append(
        f'<text class="axis" x="{left + grid_w}" y="{ly}" text-anchor="end">'
        f'<tspan style="fill:{GOLD}">◆</tspan> auto-refreshed daily · updated {updated}</text>'
    )
    out.append("</svg>")
    write_svg("contrib-heatmap.svg", out)


if __name__ == "__main__":
    main()
