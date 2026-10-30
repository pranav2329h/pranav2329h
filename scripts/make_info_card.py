#!/usr/bin/env python3
"""Generate a Neofetch-like SVG profile card. STATIC=1 disables animation."""
import os
from pathlib import Path

OUTPUT = Path("info-card.svg")
STATIC = os.getenv("STATIC", "0") == "1"
W, H = 490, 575

ROWS = [
    ("OS", "PranavOS 2026"),
    ("HOST", "Computer Science & AI"),
    ("ROLE", "Full Stack Developer"),
    ("FOCUS", "AI / ML • DevOps • Cloud"),
    ("STACK", "Python • React • Flask • Django"),
    ("DATABASE", "MongoDB • MySQL • Firebase"),
    ("CLOUD", "AWS • Docker • Terraform"),
    ("CI/CD", "Jenkins • GitHub Actions"),
    ("LEARNING", "Kubernetes • Cloud Automation"),
    ("MISSION", "Build intelligent systems"),
]

def main():
    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img">',
        '<rect width="100%" height="100%" rx="16" fill="#020617" stroke="#164e3b" stroke-width="2"/>',
        '<rect x="0" y="0" width="490" height="48" rx="16" fill="#0b1220"/>',
        '<rect x="0" y="32" width="490" height="16" fill="#0b1220"/>',
        '<circle cx="22" cy="24" r="6" fill="#ff5f56"/>',
        '<circle cx="42" cy="24" r="6" fill="#ffbd2e"/>',
        '<circle cx="62" cy="24" r="6" fill="#27c93f"/>',
        '<text x="245" y="29" text-anchor="middle" fill="#94a3b8" font-family="monospace" font-size="13">pranav@github:~</text>',
        '<text x="24" y="82" fill="#00f5a0" font-family="monospace" font-size="19" font-weight="bold">pranav@github</text>',
        '<text x="24" y="105" fill="#94a3b8" font-family="monospace" font-size="12">-------------------</text>',
    ]
    for i, (key, value) in enumerate(ROWS):
        y = 145 + i * 37
        delay = i * 0.16
        anim = "" if STATIC else (
            f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" '
            f'begin="{delay:.2f}s" fill="freeze"/>'
        )
        chunks.append(
            f'<g opacity="{1 if STATIC else 0}">'
            f'<text x="24" y="{y}" fill="#00f5a0" font-family="monospace" font-size="12">{key}</text>'
            f'<text x="125" y="{y}" fill="#dbeafe" font-family="monospace" font-size="12">{value}</text>'
            f'{anim}</g>'
        )
    chunks.extend([
        '<line x1="24" y1="520" x2="466" y2="520" stroke="#164e3b"/>',
        '<text x="24" y="545" fill="#64748b" font-family="monospace" font-size="11">STATUS: ONLINE</text>',
        '<text x="466" y="545" text-anchor="end" fill="#00f5a0" font-family="monospace" font-size="11">[ OK ]</text>',
        '</svg>'
    ])
    OUTPUT.write_text("\n".join(chunks), encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
