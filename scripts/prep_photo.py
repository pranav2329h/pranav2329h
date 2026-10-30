#!/usr/bin/env python3
"""Prepare a portrait for ASCII conversion. Usage: python scripts/prep_photo.py photo.jpg"""
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prep_photo.py source-photo.jpg")
    src = Path(sys.argv[1])
    out = Path("source-prepped.png")
    image = Image.open(src).convert("RGBA")

    # Optional background removal. If rembg is unavailable, continue with the original image.
    try:
        from rembg import remove
        image = remove(image)
    except Exception as exc:
        print(f"Background removal skipped ({exc}).")

    rgba = np.array(image)
    rgb = rgba[:, :, :3]
    alpha = rgba[:, :, 3] if rgba.shape[2] == 4 else np.full(rgb.shape[:2], 255, np.uint8)

    # Composite transparent pixels over white.
    a = alpha.astype(np.float32)[:, :, None] / 255.0
    rgb = (rgb.astype(np.float32) * a + 255.0 * (1.0 - a)).astype(np.uint8)

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.2, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    # Slight sharpening makes facial details survive downsampling.
    blur = cv2.GaussianBlur(gray, (0, 0), 1.0)
    gray = cv2.addWeighted(gray, 1.35, blur, -0.35, 0)
    Image.fromarray(gray).save(out)
    print(f"Prepared image saved to {out}")

if __name__ == "__main__":
    main()
