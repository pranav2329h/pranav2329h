#!/usr/bin/env python3
"""Create an animated monochrome ASCII SVG from source-prepped.png."""
from pathlib import Path
from PIL import Image
import html

INPUT = Path("source-prepped.png")
OUTPUT = Path("avi-ascii.svg")
COLS = 88
ROWS = 48
CELL_W = 8
CELL_H = 12
RAMP = " .`:-=+*cs#%@"

def main():
    if not INPUT.exists():
        raise SystemExit("Missing source-prepped.png. Run scripts/prep_photo.py photo.jpg first.")
    im = Image.open(INPUT).convert("L")
    # Character cells are taller than wide; compensate for terminal glyph aspect ratio.
    im = im.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    pixels = list(im.getdata())
    width, height = COLS * CELL_W, ROWS * CELL_H
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        '<rect width="100%" height="100%" fill="#020617"/>',
        '<style>text{font-family:monospace;font-size:10px;fill:#b8c7d9;white-space:pre}</style>'
    ]
    for y in range(ROWS):
        chars = []
        for x in range(COLS):
            brightness = pixels[y * COLS + x]
            idx = round((255 - brightness) / 255 * (len(RAMP) - 1))
            chars.append(RAMP[idx])
        line = html.escape("".join(chars))
        y_pos = (y + 1) * CELL_H - 2
        # Each row wipes in once, staggered vertically. SMIL is supported in SVG renderers.
        delay = y * 0.045
        parts.append(
            f'<clipPath id="row{y}"><rect x="0" y="0" width="0" height="{CELL_H}">'
            f'<animate attributeName="width" from="0" to="{width}" dur="1.05s" '
            f'begin="{delay:.3f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(
            f'<text x="2" y="{y_pos}" clip-path="url(#row{y})">{line}</text>'
        )
    parts.append("</svg>")
    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
