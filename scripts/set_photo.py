#!/usr/bin/env python3
"""Install a profile photo for the animated identity card.

    python scripts/set_photo.py path/to/photo.jpg [--focus 0.35] [--crop x0,y0,x1,y1]

Crops to 4:5 (portrait), resizes, strips metadata (EXIF/GPS) and saves
data/avatar.jpg, then rebuilds the identity card.
  --focus  vertical crop centre, 0 (top) to 1 (bottom); lower it if your head gets cut off
  --crop   exact pixel box to frame first (e.g. tighten on your face), then fit to 4:5
"""
import argparse

from PIL import Image, ImageOps

from theme import AVATAR


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("photo")
    parser.add_argument("--focus", type=float, default=0.35, help="vertical crop centre, 0 (top) to 1 (bottom)")
    parser.add_argument("--crop", help="pixel box x0,y0,x1,y1 to cut out before fitting")
    args = parser.parse_args()

    img = ImageOps.exif_transpose(Image.open(args.photo)).convert("RGB")
    if args.crop:
        img = img.crop(tuple(int(v) for v in args.crop.split(",")))
    img = ImageOps.fit(img, (672, 840), Image.Resampling.LANCZOS, centering=(0.5, args.focus))
    AVATAR.parent.mkdir(parents=True, exist_ok=True)
    img.save(AVATAR, "JPEG", quality=88, optimize=True)  # re-encoding drops all EXIF/GPS data
    print(f"Saved {AVATAR.name} ({img.width}x{img.height})")

    import make_info_card
    make_info_card.main()


if __name__ == "__main__":
    main()
