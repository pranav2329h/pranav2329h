#!/usr/bin/env python3
"""Regenerate every profile SVG (dark + light) and README.md from data/ (no network).

    python scripts/fetch_contributions.py   # refresh calendar data
    python scripts/fetch_repos.py           # refresh repo + account stats
    python scripts/fetch_activity.py        # refresh the live commit feed
    python scripts/set_photo.py photo.jpg   # (once) add your animated portrait
    python scripts/build.py                 # render assets/ and README.md
"""
import make_brand
import make_feed
import make_info_card
import make_marquee
import make_orbit
import make_project_cards
import make_readme
import make_terminal
import make_timeline
import render_heatmap_svg

STEPS = [make_brand, make_marquee, make_info_card, make_terminal, make_orbit, make_project_cards,
         make_timeline, render_heatmap_svg, make_feed, make_readme]


def main():
    for step in STEPS:
        step.main()


if __name__ == "__main__":
    main()
