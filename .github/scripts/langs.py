"""Gera langs.svg com as linguagens mais usadas nos repositórios públicos do usuário.

Cada repositório tem o mesmo peso no cálculo."""
import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "GusCfer")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = sys.argv[1] if len(sys.argv) > 1 else "langs.svg"
IGNORE = {"Jupyter Notebook", "Batchfile", "Shell", "PowerShell", "Dockerfile", "Makefile"}
COLORS = {
    "Python": "#3572A5", "Java": "#B07219", "JavaScript": "#F1E05A", "TypeScript": "#3178C6",
    "HTML": "#E34C26", "CSS": "#663399", "Kotlin": "#A97BFF", "C#": "#178600", "C": "#555555",
    "C++": "#F34B7D", "Go": "#00ADD8", "Rust": "#DEA584", "PHP": "#4F5D95", "Vue": "#41B883",
    "SCSS": "#C6538C", "Dart": "#00B4AB", "Ruby": "#701516",
}

def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "langs-card"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

totals = {}
for repo in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"):
    if repo["fork"] or repo["name"] == USER:
        continue
    langs = {k: v for k, v in get(repo["languages_url"]).items() if k not in IGNORE}
    repo_total = sum(langs.values())
    # cada repositório pesa igual, para um projeto gigante não dominar o card
    for lang, size in langs.items():
        totals[lang] = totals.get(lang, 0) + size / repo_total

total = sum(totals.values()) or 1
top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
rest = total - sum(v for _, v in top)
items = [(k, v / total * 100) for k, v in top]
if rest > 0:
    items.append(("Outras", rest / total * 100))

W, PAD = 360, 22
bar_y, bar_w = 56, W - 2 * PAD
rows = (len(items) + 1) // 2
H = bar_y + 26 + rows * 26 + 8

bar, x = [], PAD
for name, pct in items:
    w = bar_w * pct / 100
    bar.append(f'<rect x="{x:.2f}" y="{bar_y}" width="{w:.2f}" height="10" fill="{COLORS.get(name, "#8b949e")}"/>')
    x += w

legend = []
for i, (name, pct) in enumerate(items):
    cx = PAD + (i % 2) * (bar_w / 2)
    cy = bar_y + 36 + (i // 2) * 26
    legend.append(
        f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{COLORS.get(name, "#8b949e")}"/>'
        f'<text x="{cx + 16}" y="{cy}" class="l">{name}</text>'
        f'<text x="{cx + bar_w / 2 - 14}" y="{cy}" class="p" text-anchor="end">{pct:.1f}%</text>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.t{{font:600 15px 'Segoe UI',Helvetica,Arial,sans-serif;fill:#1f2328}}
.l{{font:400 13px 'Segoe UI',Helvetica,Arial,sans-serif;fill:#1f2328}}
.p{{font:400 12px 'Segoe UI',Helvetica,Arial,sans-serif;fill:#59636e}}
.bg{{fill:#ffffff;stroke:#d1d9e0}}
@media (prefers-color-scheme: dark){{
.t,.l{{fill:#e6edf3}}.p{{fill:#9198a1}}.bg{{fill:#0d1117;stroke:#3d444d}}
}}
</style>
<rect class="bg" x=".5" y=".5" width="{W-1}" height="{H-1}" rx="8"/>
<text x="{PAD}" y="34" class="t">Linguagens mais usadas</text>
<clipPath id="c"><rect x="{PAD}" y="{bar_y}" width="{bar_w}" height="10" rx="5"/></clipPath>
<g clip-path="url(#c)">{"".join(bar)}</g>
{"".join(legend)}
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg)
print("ok", items)
