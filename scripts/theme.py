"""Shared design tokens and helpers for every generated profile SVG.

Palette: "Neon Terminal" - cyan -> violet -> pink accents on GitHub's own
surfaces. Every SVG is rendered twice (assets/dark + assets/light) and the
README swaps them with <picture>, so the profile adapts to the viewer's theme.
"""
import json
from html import escape
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ASSETS = ROOT / "assets"
AVATAR = DATA / "avatar.jpg"

THEMES = [
    SimpleNamespace(
        name="dark",
        bg="#0D1117", panel="#161B22", line="#30363D",
        text="#E6EDF3", muted="#8B949E",
        c1="#22D3EE", c2="#A78BFA", c3="#F472B6", ok="#3FB950",
        heat=["#161B22", "#0C4A5E", "#0E7490", "#22D3EE", "#A5F3FC"],
        glow=0.30,
    ),
    SimpleNamespace(
        name="light",
        bg="#FFFFFF", panel="#F6F8FA", line="#D0D7DE",
        text="#1F2328", muted="#656D76",
        c1="#0891B2", c2="#7C3AED", c3="#DB2777", ok="#1A7F37",
        heat=["#EBEDF0", "#A5F3FC", "#22D3EE", "#0891B2", "#155E75"],
        glow=0.14,
    ),
]

# SVGs rendered through <img> cannot load web fonts, so use system stacks.
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "'SF Mono', 'JetBrains Mono', 'Cascadia Code', Consolas, 'Liberation Mono', Menlo, monospace"

# GitHub linguist colours for the language dot on project cards
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Shell": "#89E051",
    "HCL": "#844FBA", "Java": "#B07219", "HTML": "#E34C26", "CSS": "#663399",
}


def esc(text) -> str:
    return escape(str(text), quote=True)


def load_json(name: str, default=None):
    path = DATA / name
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_profile() -> dict:
    return load_json("profile.json")


def write_svg(t, relative: str, parts) -> Path:
    out = ASSETS / t.name / relative
    out.parent.mkdir(parents=True, exist_ok=True)
    body = parts if isinstance(parts, str) else "\n".join(parts)
    out.write_text(body + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT).as_posix()}")
    return out


def neon_gradient(t, gid: str, shimmer: bool = True, dur: str = "6s") -> str:
    """Horizontal cyan -> violet -> pink gradient, optionally sliding sideways."""
    anim = ""
    if shimmer:
        anim = (
            f'<animateTransform attributeName="gradientTransform" type="translate" '
            f'values="0 0;1 0" dur="{dur}" repeatCount="indefinite"/>'
        )
    return (
        f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0" spreadMethod="repeat">'
        f'<stop offset="0" stop-color="{t.c1}"/><stop offset="0.33" stop-color="{t.c2}"/>'
        f'<stop offset="0.66" stop-color="{t.c3}"/><stop offset="1" stop-color="{t.c1}"/>'
        f"{anim}</linearGradient>"
    )


def svg_open(width: int, height: int, label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title>"
    )


def window_chrome(t, width: int, title: str, radius: int = 16) -> str:
    """macOS-style terminal title bar."""
    r = radius
    return (
        f'<path d="M1 44 V{r + 1} a{r} {r} 0 0 1 {r} -{r} H{width - r - 1} a{r} {r} 0 0 1 {r} {r} V44 Z" fill="{t.panel}"/>'
        f'<line x1="1" y1="44" x2="{width - 1}" y2="44" stroke="{t.line}"/>'
        f'<circle cx="26" cy="23" r="6.5" fill="#FF5F57"/><circle cx="48" cy="23" r="6.5" fill="#FEBC2E"/>'
        f'<circle cx="70" cy="23" r="6.5" fill="#28C840"/>'
        f'<text x="{width / 2}" y="28" text-anchor="middle" style="font:500 13px {MONO};fill:{t.muted}">{esc(title)}</text>'
    )
