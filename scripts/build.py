#!/usr/bin/env python3
"""Regenerate every profile SVG from the data/ folder (no network access).

    python scripts/fetch_contributions.py   # refresh calendar data
    python scripts/fetch_repos.py           # refresh repo stars / languages
    python scripts/build.py                 # render all SVGs into assets/
"""
import make_brand
import make_info_card
import make_project_cards
import render_heatmap_svg
from theme import ROOT

STEPS = [make_brand, make_info_card, make_project_cards, render_heatmap_svg]


def main():
    for step in STEPS:
        step.main()
    # Optional ASCII portrait: only when a prepared photo exists locally.
    if (ROOT / "source-prepped.png").exists():
        import make_ascii_svg
        make_ascii_svg.main()


if __name__ == "__main__":
    main()
