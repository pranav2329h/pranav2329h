#!/usr/bin/env python3
"""Fetch live metadata (stars, forks, language, last push) for featured repos.

Writes data/repos.json, which the project cards read. Uses GITHUB_TOKEN when
available (as in GitHub Actions) to avoid the anonymous rate limit. A failure
for one repo keeps that repo's previous data instead of breaking the build.
"""
import json
import os

import requests

from theme import DATA, load_json, load_profile

OUT = DATA / "repos.json"


def main():
    profile = load_profile()
    owner = os.getenv("GITHUB_USERNAME", profile["handle"])
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-builder"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    previous = load_json("repos.json", {}) or {}
    result = {}
    for project in profile["projects"]:
        repo = project.get("repo")
        if not repo:
            continue
        try:
            r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers, timeout=30)
            r.raise_for_status()
            info = r.json()
            result[repo] = {
                "stars": info.get("stargazers_count", 0),
                "forks": info.get("forks_count", 0),
                "language": info.get("language"),
                "pushed_at": info.get("pushed_at"),
                "homepage": info.get("homepage") or None,
            }
        except requests.RequestException as exc:
            print(f"warning: {repo}: {exc}; keeping previous data")
            if repo in previous:
                result[repo] = previous[repo]

    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Saved metadata for {len(result)} repos to {OUT.name}")


if __name__ == "__main__":
    main()
