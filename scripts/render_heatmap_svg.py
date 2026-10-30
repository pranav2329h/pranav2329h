#!/usr/bin/env python3
"""Render data/contributions.json as an animated GitHub-style SVG heatmap."""
import json
from pathlib import Path
from datetime import date

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL = 11
GAP = 3
LEFT, TOP = 38, 26
WEEKS = 53
DAYS = 7

def main():
    if not DATA.exists():
        raise SystemExit("Missing data/contributions.json. Run fetch_contributions.py first.")
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    by_date = {x["date"]: int(x["level"]) for x in payload["days"]}
    dates = sorted(by_date)
    if not dates:
        raise SystemExit("Contribution data is empty.")

    # Anchor the 53 columns to the latest Sunday-based week in fetched data.
    latest = date.fromisoformat(dates[-1])
    start = latest
    while start.weekday() != 6:  # Sunday
        from datetime import timedelta
        start -= timedelta(days=1)
    start -= __import__("datetime").timedelta(weeks=52)

    width = LEFT + WEEKS * (CELL + GAP) + 12
    height = TOP + DAYS * (CELL + GAP) + 42
    total = sum(1 for v in by_date.values() if v > 0)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        '<rect width="100%" height="100%" rx="10" fill="#020617"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#8b949e;font-size:10px}.cell{opacity:0.15;animation:reveal .55s ease forwards}@keyframes reveal{to{opacity:1}}</style>',
    ]
    weekdays = ["Mon", "", "Wed", "", "Fri", "", ""]
    for row, label in enumerate(weekdays):
        if label:
            y = TOP + row * (CELL + GAP) + 9
            svg.append(f'<text x="8" y="{y}">{label}</text>')

    for week in range(WEEKS):
        for day in range(DAYS):
            from datetime import timedelta
            current = start + timedelta(days=week * 7 + day)
            key = current.isoformat()
            level = by_date.get(key, 0)
            x = LEFT + week * (CELL + GAP)
            y = TOP + day * (CELL + GAP)
            delay = (week + day) * 0.012
            svg.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{COLORS[level]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{key}: contribution level {level}</title></rect>'
            )

    legend_y = height - 18
    svg.append(f'<text x="{LEFT}" y="{legend_y}">Less</text>')
    for i, color in enumerate(COLORS):
        x = LEFT + 30 + i * (CELL + GAP)
        svg.append(f'<rect x="{x}" y="{legend_y-9}" width="{CELL}" height="{CELL}" rx="2" fill="{color}"/>')
    svg.append(f'<text x="{LEFT+30+5*(CELL+GAP)+3}" y="{legend_y}">More</text>')
    svg.append(f'<text x="{width-12}" y="{legend_y}" text-anchor="end">{total} active days in calendar</text>')
    svg.append("</svg>")
    OUT.write_text("\n".join(svg), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    main()
