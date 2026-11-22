#!/usr/bin/env python3
"""Generate README.md from data/profile.json.

Every image is a <picture> with dark + light sources, so GitHub shows the
variant that matches the viewer's theme.
"""
from urllib.parse import quote, urlencode

from theme import ROOT, THEMES, load_profile

DARK, LIGHT = THEMES


def hexs(color: str) -> str:
    return color.lstrip("#")


def picture(dark_src, light_src, alt, width="100%"):
    return (
        "<picture>"
        f'<source media="(prefers-color-scheme: dark)" srcset="{dark_src}" />'
        f'<source media="(prefers-color-scheme: light)" srcset="{light_src}" />'
        f'<img src="{dark_src}"{f" width={chr(34)}{width}{chr(34)}" if width else ""} alt="{alt}" />'
        "</picture>"
    )


def asset(name, alt, width="100%"):
    return picture(f"./assets/dark/{name}", f"./assets/light/{name}", alt, width)


def themed_url(build, alt, width="100%"):
    """Third-party image whose colours come from each theme."""
    return picture(build(DARK), build(LIGHT), alt, width)


def badge(label, message, logo, url):
    q = urlencode({"style": "for-the-badge", "logo": logo, "logoColor": "white", "labelColor": "0D1117"})
    src = f"https://img.shields.io/badge/{quote(label)}-{quote(message)}-{hexs(DARK.c1)}?{q}"
    return f'<a href="{url}"><img src="{src}" alt="{label}" /></a>'


def main():
    p = load_profile()
    user, links = p["handle"], p["links"]
    portfolio, linkedin, email = links["portfolio"], links["linkedin"], links["email"]

    typing = lambda t: ("https://readme-typing-svg.demolab.com?" + urlencode({
        "font": "JetBrains Mono", "weight": 600, "size": 20, "duration": 2600, "pause": 900,
        "color": hexs(t.c1), "center": "true", "vCenter": "true", "width": 720,
        "lines": ";".join(p["typing"])}))
    stats = lambda t: ("https://github-readme-stats.vercel.app/api?" + urlencode({
        "username": user, "show_icons": "true", "hide_rank": "true", "include_all_commits": "true",
        "bg_color": hexs(t.bg), "title_color": hexs(t.c1), "icon_color": hexs(t.c2),
        "text_color": hexs(t.text), "border_color": hexs(t.line), "border_radius": 14}))
    langs = lambda t: ("https://github-readme-stats.vercel.app/api/top-langs/?" + urlencode({
        "username": user, "layout": "compact", "langs_count": 8, "bg_color": hexs(t.bg),
        "title_color": hexs(t.c1), "text_color": hexs(t.text), "border_color": hexs(t.line), "border_radius": 14}))
    graph = lambda t: ("https://github-readme-activity-graph.vercel.app/graph?" + urlencode({
        "username": user, "bg_color": hexs(t.bg), "color": hexs(t.text), "title_color": hexs(t.c1),
        "line": hexs(t.c2), "point": hexs(t.c1), "area": "true", "area_color": hexs(t.c1),
        "hide_border": "true", "radius": 14, "custom_title": "Commit Velocity"}))
    snake = lambda t: f"https://raw.githubusercontent.com/{user}/{user}/output/snake-{t.name}.svg"

    skills_rows = "\n".join(
        f'<tr><td align="right"><b>{label}</b></td><td>'
        + picture(f"https://skillicons.dev/icons?i={ids}&theme=dark", f"https://skillicons.dev/icons?i={ids}&theme=light",
                  ids.replace(",", ", "), None)
        + "</td></tr>"
        for label, ids in p["skills"]
    )

    cards = []
    for proj in p["projects"]:
        img = asset(f"projects/{proj['slug']}.svg", f"{proj['title']} — {proj['tagline']}", "49%")
        cards.append(f'<a href="https://github.com/{user}/{proj["repo"]}">{img}</a>' if proj.get("repo") else img)

    contact = " ".join([
        badge("Portfolio", "Visit", "vercel", portfolio),
        badge("LinkedIn", "Connect", "linkedin", linkedin),
        badge("Email", "Say hello", "gmail", f"mailto:{email}"),
    ])
    feed = (asset("feed.svg", "Live feed of my latest commits, scrolling") if (ROOT / "assets/dark/feed.svg").exists() else "")
    views = (f'<img src="https://komarev.com/ghpvc/?username={user}&label=Profile+Views&color={hexs(DARK.c1)}'
             f'&style=for-the-badge" alt="Profile views" />')

    readme = f"""<!--
  ⚙️ GENERATED FILE — do not edit by hand.
  Edit data/profile.json, then run:  python scripts/build.py
  GitHub Actions refreshes stats and re-renders everything daily.
-->

<div align="center">

{asset("header.svg", f"{p['name']} — {p['headline']}")}

<a href="{portfolio}">{themed_url(typing, "Typing animation", None)}</a>

<p>
{contact}
{views}
</p>

{asset("marquee.svg", "Scrolling ticker of skills and values")}

{asset("titles/about.svg", "01 · The Engineer")}

{asset("info-card.svg", "Identity card: my photo animates from 8-bit pixel art to hi-res to ASCII, next to quick facts")}

<p><em>I build intelligent systems end to end, from training explainable ML models<br />
to shipping them behind clean React interfaces on containerised AWS infrastructure.</em></p>

<table>
<tr>
<td align="center" width="33%"><b>🤖 AI &amp; ML</b><br /><sub>Scikit-learn · SHAP · NLP · Deep Learning</sub></td>
<td align="center" width="33%"><b>⚡ Full Stack</b><br /><sub>React · Flask · Django · Node.js</sub></td>
<td align="center" width="33%"><b>☁️ Cloud &amp; DevOps</b><br /><sub>AWS · Docker · Jenkins · Terraform</sub></td>
</tr>
</table>

{asset("titles/terminal.svg", "02 · Live Terminal")}

{asset("terminal.svg", "Animated terminal session introducing Pranav")}

{asset("titles/arsenal.svg", "03 · Tech Arsenal")}

{asset("orbit.svg", "Animated orbit of the tech stack")}

<table>
{skills_rows}
</table>

{asset("titles/work.svg", "04 · Featured Work")}

{chr(10).join(cards)}

{asset("titles/journey.svg", "05 · The Journey")}

{asset("timeline.svg", "Animated timeline from joining GitHub to today")}

{asset("titles/activity.svg", "06 · Contribution Matrix")}

{asset("contrib-heatmap.svg", "Contribution matrix with rolling counters, yearly totals and streaks")}

{feed}

{themed_url(snake, "Snake eating my contribution graph")}

{asset("titles/insights.svg", "07 · GitHub Analytics")}

{themed_url(stats, "GitHub stats", "49%")}
{themed_url(langs, "Top languages", "49%")}

{themed_url(graph, "Contribution activity graph")}

<a href="https://github.com/{user}/TensorTonic-Solutions"><img src="https://www.tensortonic.com/api/badge/{user}.svg" width="60%" alt="TensorTonic verified ML solutions" /></a>

{asset("titles/connect.svg", "08 · Let’s Build Together")}

<p>Open to <b>AI/ML</b>, <b>full-stack</b> and <b>DevOps</b> roles, internships and collaborations.<br />
The fastest way to reach me is <a href="mailto:{email}">{email}</a>.</p>

<p>{contact}</p>

{asset("footer.svg", "Thanks for visiting — system status online")}

</div>
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print("Wrote README.md")


if __name__ == "__main__":
    main()
