#!/usr/bin/env python3
"""Fetch public GitHub contribution-calendar HTML and save daily levels."""
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USERNAME = os.getenv("GITHUB_USERNAME", "pranav2329h")
OUT = Path("data/contributions.json")
URL = f"https://github.com/users/{USERNAME}/contributions"

def main():
    response = requests.get(URL, timeout=30, headers={"User-Agent": "profile-contribution-calendar"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days = []
    for cell in soup.select(".ContributionCalendar-day"):
        day = cell.get("data-date")
        level = cell.get("data-level")
        if not day:
            title = cell.find("title")
            text = title.get_text(" ", strip=True) if title else ""
            # Older page markup may expose the date only in title text.
            import re
            match = re.search(r"(\d{4}-\d{2}-\d{2})", text)
            day = match.group(1) if match else None
        if day:
            try:
                level = int(level or 0)
            except ValueError:
                level = 0
            days.append({"date": day, "level": max(0, min(4, level))})

    # If the page layout changes, fail rather than overwriting with an empty calendar.
    if len(days) < 300:
        raise RuntimeError(f"Expected a contribution calendar, parsed only {len(days)} days.")

    days.sort(key=lambda item: item["date"])
    counts = [0] * 5
    for item in days:
        counts[item["level"]] += 1

    contributions = {
        "username": USERNAME,
        "fetched_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "days": days,
        "day_count": len(days),
        "level_counts": counts,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(contributions, indent=2), encoding="utf-8")
    print(f"Saved {len(days)} contribution days to {OUT}")

if __name__ == "__main__":
    main()
