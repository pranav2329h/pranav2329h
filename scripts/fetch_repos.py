#!/usr/bin/env python3
"""Fetch live metadata for featured repos (data/repos.json) and the account (data/user.json).

Uses GITHUB_TOKEN when available (as in GitHub Actions) to avoid the anonymous
rate limit. A failure for one repo keeps that repo's previous data.
"""
import json
import os

import requests

from theme import DATA, load_json, load_profile


def github_headers():
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-readme-builder"}
    if os.getenv("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    return headers


def main():
    profile = load_profile()
    owner = os.getenv("GITHUB_USERNAME", profile["handle"])
    headers = github_headers()

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
                "created_at": info.get("created_at"),
                "pushed_at": info.get("pushed_at"),
                "homepage": info.get("homepage") or None,
            }
        except requests.RequestException as exc:
            print(f"warning: {repo}: {exc}; keeping previous data")
            if repo in previous:
                result[repo] = previous[repo]
    (DATA / "repos.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Saved metadata for {len(result)} repos")

    try:
        r = requests.get(f"https://api.github.com/users/{owner}", headers=headers, timeout=30)
        r.raise_for_status()
        u = r.json()
        user = {k: u.get(k) for k in ("public_repos", "followers", "following", "created_at")}
        (DATA / "user.json").write_text(json.dumps(user, indent=2) + "\n", encoding="utf-8")
        print("Saved account stats")
    except requests.RequestException as exc:
        print(f"warning: user stats: {exc}; keeping previous data")


if __name__ == "__main__":
    main()
