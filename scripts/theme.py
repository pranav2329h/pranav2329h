"""Shared design tokens and helpers for every generated profile SVG.

Palette: "Obsidian & Gold" - near-black surfaces, champagne-gold accents and
ivory text. Change a value here and re-run ``python scripts/build.py`` to
restyle the whole profile at once.
"""
import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"

# Surfaces
BG = "#0B0B0F"
PANEL = "#111118"
LINE = "#2A2418"
# Gold
GOLD = "#D4AF37"
GOLD_LIGHT = "#F3D98B"
GOLD_DEEP = "#8C6A1F"
# Text
IVORY = "#EDE6D6"
MUTED = "#8A8475"
# Contribution levels 0-4, dark to bright gold
HEAT = ["#17171E", "#3A2E12", "#6E5518", "#B08A2E", "#F0CF6B"]

# SVGs rendered through <img> cannot load web fonts, so use system stacks that
# look right on macOS, Windows and Linux.
SERIF = "Didot, 'Bodoni 72', 'Bodoni MT', 'Playfair Display', 'Cormorant Garamond', Georgia, 'Times New Roman', serif"
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', 'Cascadia Code', Consolas, 'Liberation Mono', monospace"


def esc(text) -> str:
    return escape(str(text), quote=True)


def load_json(name: str, default=None):
    path = DATA / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile() -> dict:
    return load_json("profile.json")


def write_svg(relative: str, parts) -> Path:
    out = ASSETS / relative
    out.parent.mkdir(parents=True, exist_ok=True)
    body = parts if isinstance(parts, str) else "\n".join(parts)
    out.write_text(body + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT).as_posix()}")
    return out


def gold_gradient(gid: str, shimmer: bool = False, dur: str = "6s") -> str:
    """A horizontal champagne-gold gradient, optionally with a moving sheen."""
    anim = ""
    if shimmer:
        anim = (
            f'<animateTransform attributeName="gradientTransform" type="translate" '
            f'values="-1 0;1 0;-1 0" dur="{dur}" repeatCount="indefinite"/>'
        )
    return (
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">'
        f'<stop offset="0" stop-color="{GOLD_DEEP}"/>'
        f'<stop offset="0.35" stop-color="{GOLD}"/>'
        f'<stop offset="0.5" stop-color="{GOLD_LIGHT}"/>'
        f'<stop offset="0.65" stop-color="{GOLD}"/>'
        f'<stop offset="1" stop-color="{GOLD_DEEP}"/>'
        f"{anim}</linearGradient>"
    )


def svg_open(width: int, height: int, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title>"
    )
