#!/usr/bin/env python3
"""Builds assets/stats.svg from the GitHub GraphQL API.

Runs from the profile workflow, so the card never depends on a third-party
stats server being up.
"""

import json
import os
import urllib.request
from pathlib import Path

LOGIN = os.environ.get('USERNAME', '1amZach')
TOKEN = os.environ['GITHUB_TOKEN']
OUT = Path(__file__).resolve().parent.parent / 'assets' / 'stats.svg'

QUERY = '''
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount } }
      }
    }
  }
}
'''


def fetch():
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode(),
        headers={'Authorization': f'bearer {TOKEN}', 'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req) as res:
        body = json.load(res)

    if 'errors' in body:
        raise SystemExit(body['errors'])

    return body['data']['user']


def short(n):
    if n >= 1000:
        return f'{n / 1000:.1f}k'.replace('.0k', 'k')
    return str(n)


def sparkline(weeks, x, y, w, h):
    totals = [sum(d['contributionCount'] for d in wk['contributionDays']) for wk in weeks[-26:]]
    peak = max(totals) or 1
    step = w / (len(totals) - 1)
    pts = [(x + i * step, y + h - (t / peak) * h) for i, t in enumerate(totals)]

    line = ' '.join(f'{px:.1f},{py:.1f}' for px, py in pts)
    area = f'M{x},{y + h} L' + ' L'.join(f'{px:.1f},{py:.1f}' for px, py in pts) + f' L{x + w},{y + h} Z'
    return line, area


def render(user):
    cc = user['contributionsCollection']
    stars = sum(r['stargazerCount'] for r in user['repositories']['nodes'])
    days = [d['contributionCount'] for wk in cc['contributionCalendar']['weeks'] for d in wk['contributionDays']]

    stats = [
        ('Contributions', cc['contributionCalendar']['totalContributions']),
        ('Commits', cc['totalCommitContributions'] + cc['restrictedContributionsCount']),
        ('Pull requests', cc['totalPullRequestContributions']),
        ('Active days', sum(1 for d in days if d)),
        ('Best day', max(days, default=0)),
        ('Stars earned', stars),
    ]

    cells = []
    for i, (label, value) in enumerate(stats):
        cx = 25 + (i % 3) * 155
        cy = 72 + (i // 3) * 48
        cells.append(
            f'<g class="in" style="animation-delay:{0.1 * i:.1f}s">'
            f'<text x="{cx}" y="{cy}" class="num">{short(value)}</text>'
            f'<text x="{cx}" y="{cy + 17}" class="lbl">{label.upper()}</text></g>'
        )

    line, area = sparkline(cc['contributionCalendar']['weeks'], 25, 150, 445, 30)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="495" height="195" viewBox="0 0 495 195">
<style>
.num {{ font: 800 26px 'Segoe UI','Helvetica Neue',Arial,sans-serif; fill:#fff; }}
.lbl {{ font: 600 10px 'Segoe UI','Helvetica Neue',Arial,sans-serif; fill:#8b949e; letter-spacing:1.4px; }}
.ttl {{ font: 700 15px 'Segoe UI','Helvetica Neue',Arial,sans-serif; fill:#9C2CF1; }}
.sub {{ font: 500 11px 'Segoe UI','Helvetica Neue',Arial,sans-serif; fill:#6e7681; }}
.in {{ opacity:0; animation: in .5s ease-out forwards; }}
@keyframes in {{ from {{ opacity:0; transform:translateY(6px) }} to {{ opacity:1; transform:none }} }}
.spark {{ stroke-dasharray:1200; stroke-dashoffset:1200; animation: draw 2s .6s ease-out forwards; }}
@keyframes draw {{ to {{ stroke-dashoffset:0 }} }}
</style>
<defs>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#6913E7" stop-opacity=".45"/><stop offset="1" stop-color="#216EEF" stop-opacity="0"/>
  </linearGradient>
</defs>
<rect width="495" height="195" rx="8" fill="#0d1117"/>
<text x="25" y="35" class="ttl">Last 12 months</text>
<text x="470" y="35" class="sub" text-anchor="end">@{LOGIN}</text>
{"".join(cells)}
<path d="{area}" fill="url(#fill)"/>
<polyline class="spark" points="{line}" fill="none" stroke="#9C2CF1" stroke-width="2" stroke-linejoin="round"/>
</svg>
'''


if __name__ == '__main__':
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(render(fetch()))
    print(f'wrote {OUT}')
