#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar and save daily counts + levels.

Writes data/contributions.json. Fails loudly (without overwriting the existing
file) if GitHub changes its markup and the calendar can no longer be parsed.
"""
import json
import os
import re
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

from theme import DATA

USERNAME = os.getenv("GITHUB_USERNAME", "pranav2329h")
OUT = DATA / "contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"
COUNT_RE = re.compile(r"([\d,]+)\s+contributions?", re.I)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def parse_count(text: str) -> int:
    match = COUNT_RE.search(text or "")
    return int(match.group(1).replace(",", "")) if match else 0


def main():
    response = requests.get(URL, timeout=30, headers={"User-Agent": "profile-readme-builder"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Exact per-day counts live in <tool-tip for="<cell id>"> elements.
    tooltips = {tip.get("for"): tip.get_text(" ", strip=True) for tip in soup.select("tool-tip[for]")}

    days = []
    for cell in soup.select(".ContributionCalendar-day"):
        day = cell.get("data-date")
        if not day:
            title = cell.find("title")
            match = DATE_RE.search(title.get_text(" ", strip=True) if title else "")
            day = match.group(1) if match else None
        if not day:
            continue
        try:
            level = max(0, min(4, int(cell.get("data-level") or 0)))
        except ValueError:
            level = 0
        count = parse_count(tooltips.get(cell.get("id"), ""))
        days.append({"date": day, "level": level, "count": count})

    # If the page layout changes, fail rather than overwriting with an empty calendar.
    if len(days) < 300:
        raise RuntimeError(f"Expected a contribution calendar, parsed only {len(days)} days.")

    days.sort(key=lambda item: item["date"])
    heading = soup.find(string=COUNT_RE)
    total = parse_count(str(heading)) if heading else sum(d["count"] for d in days)

    level_counts = [0] * 5
    for item in days:
        level_counts[item["level"]] += 1

    payload = {
        "username": USERNAME,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "total": total,
        "day_count": len(days),
        "level_counts": level_counts,
        "days": days,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(days)} days ({total} contributions) to {OUT.name}")


if __name__ == "__main__":
    main()
