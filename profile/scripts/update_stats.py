#!/usr/bin/env python3
"""Update local SVG stats for the Verge organization profile (no Shields.io runtime)."""
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from html import escape

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"
TOKEN = os.getenv("GITHUB_TOKEN", "")

def github(path):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "verge-profile-stats", "X-GitHub-Api-Version": "2022-11-28"}
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
    req = Request(API + path, headers=headers)
    with urlopen(req, timeout=25) as response:
        return json.load(response)

def compact(x):
    if x >= 1000000:
        return f"{x/1000000:.1f}M"
    if x >= 10000:
        return f"{x/1000:.1f}k"
    return format(x, ",")

repo = github('/repos/vergecurrency/verge')
# Subscribers are people watching the repository, not organization followers.
values = [compact(repo['stargazers_count']), compact(repo['forks_count']), compact(repo['subscribers_count'])]
# Sum releases asset downloads; stop at a short page (GitHub API max page size 100).
downloads = 0
for page in range(1, 21):
    releases = github(f'/repos/vergecurrency/verge/releases?per_page=100&page={page}')
    for release in releases:
        downloads += sum(asset.get('download_count', 0) for asset in release.get('assets', []))
    if len(releases) < 100:
        break
values.append(compact(downloads))
colors = ['#05D9E8', '#FF2A6D', '#9D4EDD', '#FF9E00']
labels = ['CORE STARS', 'FORKS', 'WATCHERS', 'TOTAL DOWNLOADS']
parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 188" width="1120" height="188" role="img" aria-label="Verge Core live repository statistics">',
         '<rect x="0" y="0" width="1120" height="188" rx="16" fill="#0D0221"/>',
         '<rect x="1" y="1" width="1118" height="186" rx="15" fill="none" stroke="#5F367A"/>']
for i, (label, value, color) in enumerate(zip(labels, values, colors)):
    x = 24 + i * 276
    parts.extend([f'<rect x="{x}" y="22" width="250" height="142" rx="11" fill="#170B36" stroke="{color}" stroke-opacity=".55"/>',
                  f'<rect x="{x+17}" y="38" width="7" height="7" rx="3.5" fill="{color}"/>',
                  f'<text x="{x+33}" y="48" font-family="Arial,sans-serif" font-size="14" font-weight="700" letter-spacing="1" fill="{color}">{escape(label)}</text>',
                  f'<text x="{x+18}" y="122" font-family="Arial,sans-serif" font-size="41" font-weight="800" fill="#F5F3FF">{escape(str(value))}</text>'])
parts.append('</svg>')
(ROOT / 'assets' / 'core-stats.svg').write_text(''.join(parts) + '\n', encoding='utf-8')
print('Updated Verge Core stats:', dict(zip(labels, values)))
