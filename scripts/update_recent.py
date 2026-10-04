"""Rewrite the "Recently pushed" block in README.md from the GitHub API."""
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "abdallah")
COUNT = int(os.environ.get("RECENT_COUNT", "5"))
SKIP = {USER, f"{USER}.github.com", f"{USER}.github.io"}

req = urllib.request.Request(
    f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30&type=owner",
    headers={"Accept": "application/vnd.github+json"},
)
if os.environ.get("GITHUB_TOKEN"):
    req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
repos = json.load(urllib.request.urlopen(req))

lines = []
for r in repos:
    if r["fork"] or r["archived"] or r["private"] or r["name"] in SKIP:
        continue
    line = f"- [{r['name']}]({r['html_url']})"
    if r["description"]:
        line += f": {r['description']}"
    if r["language"]:
        line += f" · {r['language']}"
    line += f" · {r['pushed_at'][:10]}"
    lines.append(line)
    if len(lines) == COUNT:
        break

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
block = "<!-- RECENT:START -->\n" + "\n".join(lines) + "\n<!-- RECENT:END -->"
readme = re.sub(r"<!-- RECENT:START -->.*?<!-- RECENT:END -->", lambda _: block, readme, flags=re.S)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
