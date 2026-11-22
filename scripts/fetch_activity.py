#!/usr/bin/env python3
"""Fetch my most recent real commits across public repos -> data/activity.json.

Automated noise (bot refreshes, [skip ci], merges) is filtered out so the
scrolling commit feed only shows hand-written work.
"""
import json
import os
import re

import requests

from fetch_repos import github_headers
from theme import DATA, load_profile

NOISE = re.compile(r"^(merge\b|chore: refresh)|\[skip ci\]", re.I)
LIMIT = 14


def main():
    owner = os.getenv("GITHUB_USERNAME", load_profile()["handle"])
    url = "https://api.github.com/search/commits"
    params = {"q": f"author:{owner}", "sort": "author-date", "order": "desc", "per_page": 100}
    try:
        r = requests.get(url, params=params, headers=github_headers(), timeout=30)
        r.raise_for_status()
    except requests.RequestException as exc:
        print(f"warning: commit search failed ({exc}); keeping previous feed")
        return

    commits, seen = [], set()
    for item in r.json().get("items", []):
        message = item["commit"]["message"].splitlines()[0].strip()
        if not message or NOISE.search(message):
            continue
        key = (item["repository"]["name"], message)
        if key in seen:  # identical messages pushed to several branches
            continue
        seen.add(key)
        commits.append({
            "repo": item["repository"]["name"],
            "sha": item["sha"][:7],
            "message": message,
            "date": item["commit"]["author"]["date"][:10],
        })
        if len(commits) == LIMIT:
            break

    if commits:
        (DATA / "activity.json").write_text(json.dumps(commits, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(commits)} recent commits")


if __name__ == "__main__":
    main()
