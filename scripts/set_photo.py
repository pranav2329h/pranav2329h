#!/usr/bin/env python3
"""Install a profile photo for the animated identity card.

    python scripts/set_photo.py path/to/photo.jpg [--focus 0.35]

Crops to 4:5 (portrait), resizes, strips metadata (EXIF/GPS) and saves
data/avatar.jpg, then rebuilds the identity card. --focus sets where the crop
centres vertically (0 = top, 1 = bottom); lower it if your head gets cut off.
"""
import argparse

from PIL import Image, ImageOps

from theme import AVATAR


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("photo")
    parser.add_argument("--focus", type=float, default=0.35, help="vertical crop centre, 0 (top) to 1 (bottom)")
    args = parser.parse_args()

    img = ImageOps.exif_transpose(Image.open(args.photo)).convert("RGB")
    img = ImageOps.fit(img, (672, 840), Image.Resampling.LANCZOS, centering=(0.5, args.focus))
    AVATAR.parent.mkdir(parents=True, exist_ok=True)
    img.save(AVATAR, "JPEG", quality=88, optimize=True)  # re-encoding drops all EXIF/GPS data
    print(f"Saved {AVATAR.name} ({img.width}x{img.height})")

    import make_info_card
    make_info_card.main()


if __name__ == "__main__":
    main()
