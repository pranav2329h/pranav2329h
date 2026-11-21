#!/usr/bin/env python3
"""Optional: turn source-prepped.png into an animated gold ASCII portrait.

    pip install -r scripts/requirements-portrait.txt
    python scripts/prep_photo.py path/to/photo.jpg
    python scripts/make_ascii_svg.py          # -> assets/portrait-ascii.svg
"""
import html

from PIL import Image

from theme import BG, GOLD_LIGHT, MONO, ROOT, svg_open, write_svg

INPUT = ROOT / "source-prepped.png"
COLS, ROWS = 88, 48
CELL_W, CELL_H = 8, 12
RAMP = " .`:-=+*cs#%@"


def main():
    if not INPUT.exists():
        raise SystemExit("Missing source-prepped.png. Run scripts/prep_photo.py photo.jpg first.")
    # Glyphs are taller than wide, so the ROWS/COLS ratio compensates for aspect.
    im = Image.open(INPUT).convert("L").resize((COLS, ROWS), Image.Resampling.LANCZOS)
    pixels = list(im.getdata())
    width, height = COLS * CELL_W, ROWS * CELL_H
    parts = [
        svg_open(width, height, "ASCII portrait"),
        f'<rect width="100%" height="100%" rx="16" fill="{BG}"/>',
        f"<style>text{{font-family:{MONO};font-size:10px;fill:{GOLD_LIGHT};white-space:pre}}</style>",
    ]
    for y in range(ROWS):
        row = pixels[y * COLS:(y + 1) * COLS]
        line = "".join(RAMP[round((255 - b) / 255 * (len(RAMP) - 1))] for b in row)
        # Each row wipes in once, staggered top to bottom.
        parts.append(
            f'<clipPath id="row{y}"><rect x="0" y="{y * CELL_H}" width="0" height="{CELL_H}">'
            f'<animate attributeName="width" from="0" to="{width}" dur="1.05s" '
            f'begin="{y * 0.045:.3f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(
            f'<text x="2" y="{(y + 1) * CELL_H - 2}" clip-path="url(#row{y})" xml:space="preserve">'
            f"{html.escape(line)}</text>"
        )
    parts.append("</svg>")
    write_svg("portrait-ascii.svg", parts)


if __name__ == "__main__":
    main()
