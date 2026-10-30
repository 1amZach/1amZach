#!/usr/bin/env python3
"""Builds every panel on the profile into assets/.

Static art and live numbers come from the same place so the whole page shares
one look. GitHub stats need GITHUB_TOKEN; the Discord counts use the public
invite endpoint. If a request fails the last good numbers in assets/data.json
are reused, so a bad run never blanks the page.
"""

import base64
import datetime as dt
import json
import math
import os
import random
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'assets'
LOGIN = os.environ.get('USERNAME', '1amZach')
INVITE = 'agn'

# sampled from the Astra logo banner
VIOLET = '#9C2CF1'
DEEP = '#6913E7'
INDIGO = '#3A05C7'
BLUE = '#216EEF'
TEAL = '#2BD9CC'
ORCHID = '#C241F3'
SILVER = '#E2DEE9'
MUTED = '#8F86B8'
PANEL = '#0D0B1C'
LINE = '#2C2455'

NAME_BOX = (378, 370, 1128, 600)  # neon name inside the 1500x600 banner


# ---------------------------------------------------------------- helpers

def b64(path):
    return base64.b64encode((ASSETS / path).read_bytes()).decode()


def fonts(*which):
    faces = {
        'raj500': ("R", 500), 'raj700': ("R", 700), 'jbm500': ("M", 500),
    }
    rules = []
    for key in which:
        family, weight = faces[key]
        rules.append(f"@font-face{{font-family:{family};font-weight:{weight};"
                     f"src:url(data:font/woff2;base64,{b64(f'fonts/{key}.woff2')}) format('woff2')}}")
    return '\n'.join(rules)


def esc(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def svg(w, h, body, style='', defs='', view=None):
    view = view or f'0 0 {w} {h}'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="{view}">\n<style>\n{style}\n</style>\n'
            f'<defs>{defs}</defs>\n{body}\n</svg>\n')


def image(href_b64, mime, **attrs):
    a = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    data = f'data:{mime};base64,{href_b64}'
    return f'<image {a} href="{data}" xlink:href="{data}"/>'


def brackets(x, y, w, h, size=14, colour=TEAL, width=2):
    """HUD corner brackets around a box."""
    s = size
    d = (f'M{x},{y + s} V{y} H{x + s} M{x + w - s},{y} H{x + w} V{y + s} '
         f'M{x + w},{y + h - s} V{y + h} H{x + w - s} M{x + s},{y + h} H{x} V{y + h - s}')
    return f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}"/>'


def panel(x, y, w, h, title=None, live=False):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="url(#panelfill)" stroke="{LINE}"/>',
           brackets(x, y, w, h)]
    if title:
        out.append(f'<text x="{x + 20}" y="{y + 30}" class="m" font-size="12" fill="{TEAL}" letter-spacing="3">{esc(title)}</text>')
    if live:
        out.append(f'<circle class="blink" cx="{x + w - 70}" cy="{y + 26}" r="4" fill="{TEAL}"/>'
                   f'<text x="{x + w - 20}" y="{y + 30}" class="m" font-size="11" fill="{TEAL}" text-anchor="end" letter-spacing="2">LIVE</text>')
    return ''.join(out)


BASE_STYLE = f'''
.r {{ font-family:R,'Segoe UI',sans-serif; font-weight:700; }}
.r5 {{ font-family:R,'Segoe UI',sans-serif; font-weight:500; }}
.m {{ font-family:M,Consolas,monospace; font-weight:500; }}
.blink {{ animation: blink 1.4s ease-in-out infinite; }}
@keyframes blink {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.2 }} }}
'''

PANEL_DEFS = f'''
<linearGradient id="panelfill" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#110d26"/><stop offset="1" stop-color="{PANEL}"/>
</linearGradient>
<linearGradient id="brand" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{BLUE}"/>
</linearGradient>
'''


# ---------------------------------------------------------------- data

def graphql(token):
    query = '''
    query($login: String!) {
      user(login: $login) {
        databaseId createdAt
        followers { totalCount }
        contributionsCollection {
          totalCommitContributions totalPullRequestContributions restrictedContributionsCount
          contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
        }
      }
    }'''
    req = urllib.request.Request(
        'https://api.github.com/graphql',
        data=json.dumps({'query': query, 'variables': {'login': LOGIN}}).encode(),
        headers={'Authorization': f'bearer {token}', 'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        body = json.load(res)
    if 'errors' in body:
        raise RuntimeError(body['errors'])
    return body['data']['user']


def discord():
    req = urllib.request.Request(f'https://discord.com/api/v10/invites/{INVITE}?with_counts=true',
                                 headers={'User-Agent': 'profile-build'})
    with urllib.request.urlopen(req, timeout=30) as res:
        d = json.load(res)
    return {'online': d['approximate_presence_count'], 'members': d['approximate_member_count']}


def load_data():
    cache = ASSETS / 'data.json'
    data = json.loads(cache.read_text()) if cache.exists() else {}

    token = os.environ.get('GITHUB_TOKEN')
    if token:
        try:
            u = graphql(token)
            cc = u['contributionsCollection']
            days = [d for w in cc['contributionCalendar']['weeks'] for d in w['contributionDays']]
            data['github'] = {
                'id': u['databaseId'],
                'created': u['createdAt'][:10],
                'followers': u['followers']['totalCount'],
                'total': cc['contributionCalendar']['totalContributions'],
                'commits': cc['totalCommitContributions'] + cc['restrictedContributionsCount'],
                'prs': cc['totalPullRequestContributions'],
                'days': [[d['date'], d['contributionCount']] for d in days],
            }
        except Exception as e:  # keep the last good numbers
            print('github fetch failed:', e)

    try:
        data['discord'] = discord()
    except Exception as e:
        print('discord fetch failed:', e)

    cache.write_text(json.dumps(data))
    return data


# ---------------------------------------------------------------- panels

def loading():
    """The banner as a server loading screen."""
    random.seed(3)
    w, h = 1500, 600
    mx, my, mx2, my2 = NAME_BOX
    surge_w, travel = 320, NAME_BOX[2] - NAME_BOX[0] + 320

    sparks = ''.join(
        f'<circle class="spark" cx="{random.uniform(0, w):.0f}" cy="{random.uniform(h * .35, h * .85):.0f}" '
        f'r="{random.choice([1.2, 1.6, 2.2])}" fill="{random.choice([VIOLET, TEAL, ORCHID, SILVER])}" '
        f'style="animation-duration:{random.uniform(5, 9):.1f}s;animation-delay:-{random.uniform(0, 9):.1f}s"/>'
        for _ in range(34)
    )

    tips = ['mounting ox_lib', 'starting devkit', 'syncing Astra Gaming Network', 'spawning IamZach']
    tip_svg = ''.join(
        f'<text class="m tip" x="70" y="532" font-size="22" fill="{SILVER}" style="animation-delay:{i * 2}s">'
        f'<tspan fill="{TEAL}">&gt;</tspan> {esc(t)}</text>' for i, t in enumerate(tips)
    )

    style = BASE_STYLE + fonts('raj700', 'jbm500') + f'''
.spark {{ opacity:0; animation: spark 7s ease-in-out infinite; }}
@keyframes spark {{ 0% {{ opacity:0; transform:translate(0,0) }} 20% {{ opacity:.9 }} 100% {{ opacity:0; transform:translate(30px,-170px) }} }}
.surge {{ animation: surge 4s cubic-bezier(.5,0,.4,1) infinite; }}
@keyframes surge {{ 0% {{ transform:translateX(0) }} 50%,100% {{ transform:translateX({travel}px) }} }}
.charge {{ animation: charge 4s linear infinite; }}
@keyframes charge {{ 0%,46% {{ opacity:0 }} 50% {{ opacity:.85 }} 53% {{ opacity:.2 }} 56% {{ opacity:.6 }} 75%,100% {{ opacity:0 }} }}
.halo {{ animation: halo 4s ease-in-out infinite; }}
@keyframes halo {{ 0%,100% {{ opacity:.3 }} 50% {{ opacity:1 }} }}
.tip {{ opacity:0; animation: tip 8s steps(1) infinite; }}
@keyframes tip {{ 0% {{ opacity:1 }} 25%,100% {{ opacity:0 }} }}
.bar {{ transform-origin:70px 0; animation: bar 8s cubic-bezier(.3,.1,.3,1) infinite; }}
@keyframes bar {{ 0% {{ transform:scaleX(0) }} 22% {{ transform:scaleX(.31) }} 30% {{ transform:scaleX(.36) }} 55% {{ transform:scaleX(.68) }} 62% {{ transform:scaleX(.7) }} 92%,100% {{ transform:scaleX(1) }} }}
.spin {{ transform-origin:1418px 520px; animation: spin 1.1s linear infinite; }}
@keyframes spin {{ to {{ transform:rotate(360deg) }} }}
'''
    defs = f'''
<clipPath id="frame"><rect width="{w}" height="{h}" rx="20"/></clipPath>
<mask id="name" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">
  {image(b64('name-mask.png'), 'image/png', x=mx, y=my, width=mx2 - mx, height=my2 - my)}
</mask>
<linearGradient id="surgefill" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset=".35" stop-color="{TEAL}"/>
  <stop offset=".52" stop-color="#fff"/><stop offset=".62" stop-color="#fff"/>
  <stop offset=".78" stop-color="{ORCHID}"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
</linearGradient>
<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#05030c" stop-opacity="0"/><stop offset="1" stop-color="#05030c" stop-opacity=".92"/>
</linearGradient>
<linearGradient id="top" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#05030c" stop-opacity=".75"/><stop offset="1" stop-color="#05030c" stop-opacity="0"/>
</linearGradient>
<linearGradient id="barfill" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{TEAL}"/><stop offset=".6" stop-color="{VIOLET}"/><stop offset="1" stop-color="{ORCHID}"/>
</linearGradient>
<filter id="halo" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="10"/></filter>
<filter id="barglow" x="-5%" y="-300%" width="110%" height="700%"><feGaussianBlur stdDeviation="4"/></filter>
'''
    body = f'''
<g clip-path="url(#frame)">
  {image(b64('banner.jpg'), 'image/jpeg', width=w, height=h)}
  <g class="halo" filter="url(#halo)"><g mask="url(#name)"><rect x="{mx}" y="{my}" width="{mx2 - mx}" height="{my2 - my}" fill="{TEAL}"/></g></g>
  <g mask="url(#name)">
    <rect class="charge" x="{mx}" y="{my}" width="{mx2 - mx}" height="{my2 - my}" fill="{SILVER}"/>
    <rect class="surge" x="{mx - surge_w}" y="{my}" width="{surge_w}" height="{my2 - my}" fill="url(#surgefill)"/>
  </g>
  {sparks}
  <rect width="{w}" height="90" fill="url(#top)"/>
  <rect y="440" width="{w}" height="160" fill="url(#fade)"/>
  <text class="r" x="70" y="54" font-size="20" fill="{SILVER}" letter-spacing="6" opacity=".85">ASTRA GAMING NETWORK</text>
  <text class="m" x="{w - 70}" y="54" font-size="17" fill="{TEAL}" text-anchor="end" letter-spacing="2">discord.gg/agn</text>
  {tip_svg}
  <g class="spin"><circle cx="1418" cy="520" r="13" fill="none" stroke="{LINE}" stroke-width="4"/>
    <path d="M1418,507 a13,13 0 0 1 13,13" fill="none" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/></g>
  <text class="r" x="1390" y="528" font-size="20" fill="{SILVER}" text-anchor="end" letter-spacing="4">LOADING</text>
  <rect x="70" y="556" width="1360" height="6" rx="3" fill="#ffffff" fill-opacity=".1"/>
  <rect class="bar" x="70" y="552" width="1360" height="14" rx="7" fill="url(#barfill)" filter="url(#barglow)" opacity=".7"/>
  <rect class="bar" x="70" y="556" width="1360" height="6" rx="3" fill="url(#barfill)"/>
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="20" fill="none" stroke="{VIOLET}" stroke-opacity=".45" stroke-width="2"/>
'''
    return svg(1000, 400, body, style, defs, view=f'0 0 {w} {h}')


def license_and_server(data):
    g = data.get('github', {})
    dc = data.get('discord', {'online': 0, 'members': 0})
    created = dt.date.fromisoformat(g.get('created', '2024-01-31'))

    # guilloche: layered sine waves, the security pattern on real IDs
    waves = []
    for i in range(14):
        amp, phase, yb = 10 + i * 1.6, i * 0.55, 120 + i * 20
        pts = ' '.join(f'{x},{yb + amp * math.sin(x / 38 + phase):.1f}' for x in range(20, 621, 10))
        waves.append(f'<polyline points="{pts}" fill="none" stroke="{VIOLET}" stroke-opacity=".09" stroke-width="1"/>')

    random.seed(158)
    bars, bx = [], 452
    while bx < 596:
        bw = random.choice([1, 1, 2, 3])
        bars.append(f'<rect x="{bx}" y="344" width="{bw}" height="36" fill="{SILVER}" fill-opacity=".75"/>')
        bx += bw + random.choice([1, 2, 2, 3])

    def field(x, y, label, value, size=22, colour='#fff'):
        return (f'<text class="r5" x="{x}" y="{y}" font-size="12" fill="{MUTED}" letter-spacing="2.5">{esc(label)}</text>'
                f'<text class="r" x="{x}" y="{y + 26}" font-size="{size}" fill="{colour}">{esc(value)}</text>')

    chips, cx = [], 240
    for label in ('ESX', 'QBCORE', 'QBOX'):
        cw = len(label) * 9 + 22
        chips.append(f'<rect x="{cx}" y="354" width="{cw}" height="24" rx="4" fill="{VIOLET}" fill-opacity=".18" stroke="{VIOLET}" stroke-opacity=".6"/>'
                     f'<text class="r" x="{cx + cw / 2}" y="371" font-size="13" fill="{SILVER}" text-anchor="middle" letter-spacing="1.5">{label}</text>')
        cx += cw + 6

    xp = g.get('total', 0)
    level = int(math.isqrt(xp))
    lo, hi = level ** 2, (level + 1) ** 2
    progress = (xp - lo) / (hi - lo) if hi > lo else 0
    days = g.get('days', [])
    active = sum(1 for _, c in days if c)

    style = BASE_STYLE + fonts('raj500', 'raj700', 'jbm500') + f'''
.holo {{ animation: holo 5s ease-in-out infinite; }}
@keyframes holo {{ 0% {{ transform:translateX(-420px) }} 60%,100% {{ transform:translateX(760px) }} }}
.xp {{ transform-origin:660px 0; animation: xp 2.2s .4s cubic-bezier(.2,.8,.2,1) both; }}
@keyframes xp {{ from {{ transform:scaleX(0) }} to {{ transform:scaleX(1) }} }}
.connect {{ animation: connect 2.4s ease-in-out infinite; }}
@keyframes connect {{ 0%,100% {{ opacity:.35 }} 50% {{ opacity:.9 }} }}
'''
    defs = PANEL_DEFS + f'''
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#1c1342"/><stop offset=".55" stop-color="#120f2e"/><stop offset="1" stop-color="#0b1838"/>
</linearGradient>
<linearGradient id="band" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{DEEP}"/><stop offset=".6" stop-color="{INDIGO}"/><stop offset="1" stop-color="{BLUE}"/>
</linearGradient>
<linearGradient id="holofill" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="{TEAL}" stop-opacity=".16"/>
  <stop offset=".55" stop-color="#fff" stop-opacity=".22"/><stop offset=".75" stop-color="{ORCHID}" stop-opacity=".16"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<clipPath id="cardclip"><rect x="20" y="20" width="600" height="380" rx="20"/></clipPath>
<clipPath id="photo"><rect x="44" y="114" width="172" height="214" rx="12"/></clipPath>
<clipPath id="icon"><rect x="662" y="62" width="62" height="62" rx="14"/></clipPath>
<filter id="soft" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
'''
    card = f'''
<g clip-path="url(#cardclip)">
  <rect x="20" y="20" width="600" height="380" fill="url(#card)"/>
  {''.join(waves)}
  <rect x="20" y="20" width="600" height="74" fill="url(#band)"/>
  <text class="r5" x="44" y="50" font-size="13" fill="{SILVER}" letter-spacing="4" opacity=".85">STATE OF</text>
  <text class="r" x="44" y="80" font-size="30" fill="#fff" letter-spacing="3">SAN ANDREAS</text>
  <text class="r" x="596" y="56" font-size="15" fill="{TEAL}" text-anchor="end" letter-spacing="3">DEVELOPER</text>
  <text class="r" x="596" y="80" font-size="15" fill="#fff" text-anchor="end" letter-spacing="3">LICENSE</text>
  <rect x="42" y="112" width="176" height="218" rx="14" fill="none" stroke="{TEAL}" stroke-opacity=".5"/>
  <g clip-path="url(#photo)">{image(b64('avatar.jpg'), 'image/jpeg', x=44, y=114, width=172, height=214, preserveAspectRatio='xMidYMid slice')}</g>
  {field(240, 128, 'DL NO.', g.get('id', '158304866'), colour=TEAL)}
  {field(440, 128, 'CLASS', 'FULL STACK')}
  {field(240, 184, 'NAME', 'IAMZACH', size=26)}
  {field(440, 184, 'HANDLE', '@' + LOGIN)}
  {field(240, 240, 'ORG', 'ASTRA GAMING NETWORK')}
  {field(240, 296, 'ISSUED', created.strftime('%m/%d/%Y'))}
  {field(440, 296, 'EXPIRES', 'NEVER', colour=TEAL)}
  <text class="r5" x="240" y="346" font-size="11" fill="{MUTED}" letter-spacing="2.5">ENDORSEMENTS</text>
  {''.join(chips)}
  <text class="r" x="56" y="372" font-size="30" fill="{SILVER}" font-style="italic" transform="rotate(-4 56 372)" opacity=".9">IamZach</text>
  <line x1="44" y1="380" x2="216" y2="380" stroke="{MUTED}" stroke-opacity=".5"/>
  {''.join(bars)}
  <rect class="holo" x="20" y="20" width="260" height="380" fill="url(#holofill)" transform="skewX(-18)"/>
</g>
<rect x="20" y="20" width="600" height="380" rx="20" fill="none" stroke="{VIOLET}" stroke-opacity=".55" stroke-width="1.5"/>
'''
    server = f'''
{panel(640, 20, 340, 182, 'SERVER BROWSER', live=True)}
<rect x="660" y="60" width="66" height="66" rx="16" fill="none" stroke="{VIOLET}" stroke-opacity=".7"/>
<g clip-path="url(#icon)">{image(b64('agn-icon.jpg'), 'image/jpeg', x=662, y=62, width=62, height=62)}</g>
<text class="r" x="740" y="88" font-size="22" fill="#fff">Astra Gaming Network</text>
<text class="r5" x="740" y="112" font-size="14" fill="{MUTED}">voice-first gaming community</text>
<text class="r" x="660" y="176" font-size="30" fill="{TEAL}">{dc['online']}</text>
<text class="r5" x="{660 + len(str(dc['online'])) * 16 + 6}" y="176" font-size="13" fill="{MUTED}" letter-spacing="2">ONLINE</text>
<text class="r" x="660" y="154" font-size="13" fill="{SILVER}" letter-spacing="2">{dc['members']} MEMBERS</text>
<rect class="connect" x="842" y="146" width="122" height="38" rx="6" fill="{VIOLET}" filter="url(#soft)"/>
<rect x="842" y="146" width="122" height="38" rx="6" fill="{VIOLET}"/>
<text class="r" x="903" y="171" font-size="16" fill="#fff" text-anchor="middle" letter-spacing="3">CONNECT</text>
'''
    stats = [('COMMITS', g.get('commits', 0)), ('PRS', g.get('prs', 0)), ('ACTIVE DAYS', active)]
    stat_svg = ''.join(
        f'<text class="r" x="{660 + i * 106}" y="372" font-size="24" fill="#fff">{v}</text>'
        f'<text class="r5" x="{660 + i * 106}" y="390" font-size="11" fill="{MUTED}" letter-spacing="2">{k}</text>'
        for i, (k, v) in enumerate(stats)
    )
    level_svg = f'''
{panel(640, 218, 340, 182, 'PLAYER LEVEL')}
<text class="r" x="660" y="296" font-size="54" fill="#fff">{level}</text>
<text class="r5" x="{664 + len(str(level)) * 29}" y="296" font-size="15" fill="{MUTED}" letter-spacing="3">LVL</text>
<text class="r" x="960" y="270" font-size="20" fill="{TEAL}" text-anchor="end">{xp} XP</text>
<text class="r5" x="960" y="292" font-size="12" fill="{MUTED}" text-anchor="end" letter-spacing="1.5">{hi - xp} TO LVL {level + 1}</text>
<rect x="660" y="310" width="300" height="8" rx="4" fill="#fff" fill-opacity=".08"/>
<rect class="xp" x="660" y="310" width="{max(6, 300 * progress):.0f}" height="8" rx="4" fill="url(#brand)"/>
<text class="r5" x="660" y="338" font-size="11" fill="{MUTED}" letter-spacing="2">CONTRIBUTIONS, LAST 12 MONTHS</text>
{stat_svg}
'''
    return svg(1000, 420, card + server + level_svg, style, defs)


def mission():
    objectives = ['Grab coords from anywhere', 'Inspect any entity', 'Place and copy props', 'Draw ox_lib zones']
    obj_svg = []
    for i, text in enumerate(objectives):
        y = 178 + i * 32
        delay = 0.5 + i * 0.45
        obj_svg.append(
            f'<rect x="40" y="{y - 15}" width="18" height="18" rx="3" fill="none" stroke="{TEAL}" stroke-opacity=".7"/>'
            f'<path class="tick" d="M43,{y - 6} l5,5 l9,-10" fill="none" stroke="{TEAL}" stroke-width="2.6" '
            f'stroke-linecap="round" stroke-linejoin="round" style="animation-delay:{delay:.2f}s"/>'
            f'<text class="r5 obj" x="72" y="{y}" font-size="19" fill="{SILVER}" style="animation-delay:{delay:.2f}s">{esc(text)}</text>'
        )

    random.seed(11)
    blips = []
    for _ in range(9):
        a, d = random.uniform(0, math.tau), random.uniform(25, 100)
        colour = random.choice([VIOLET, VIOLET, TEAL, ORCHID])
        blips.append(f'<circle class="blip" cx="{820 + d * math.cos(a):.0f}" cy="{150 + d * math.sin(a):.0f}" r="4.5" fill="{colour}" '
                     f'style="animation-delay:-{random.uniform(0, 3):.1f}s"/>')
    zone = ' '.join(f'{820 + x},{150 + y}' for x, y in [(-70, -40), (-20, -78), (30, -52), (10, -10), (-48, 2)])

    style = BASE_STYLE + fonts('raj500', 'raj700', 'jbm500') + f'''
.tick {{ stroke-dasharray:24; stroke-dashoffset:24; animation: tick .35s ease-out forwards; }}
@keyframes tick {{ to {{ stroke-dashoffset:0 }} }}
.obj {{ opacity:.45; animation: obj .35s ease-out forwards; }}
@keyframes obj {{ to {{ opacity:1 }} }}
.sweep {{ transform-origin:820px 150px; animation: sweep 4s linear infinite; }}
@keyframes sweep {{ to {{ transform:rotate(360deg) }} }}
.blip {{ animation: blip 3s ease-in-out infinite; }}
@keyframes blip {{ 0%,100% {{ opacity:.25 }} 50% {{ opacity:1 }} }}
.zone {{ animation: zone 3s ease-in-out infinite; }}
@keyframes zone {{ 0%,100% {{ fill-opacity:.12 }} 50% {{ fill-opacity:.28 }} }}
'''
    defs = PANEL_DEFS + f'''
<radialGradient id="radar"><stop offset="0" stop-color="#16123a"/><stop offset="1" stop-color="#07061a"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/><stop offset="1" stop-color="{TEAL}" stop-opacity=".55"/>
</linearGradient>
<clipPath id="radarclip"><circle cx="820" cy="150" r="118"/></clipPath>
'''
    body = f'''
{panel(10, 10, 980, 280)}
<circle class="blink" cx="44" cy="44" r="5" fill="{TEAL}"/>
<text class="m" x="58" y="49" font-size="13" fill="{TEAL}" letter-spacing="3">ACTIVE MISSION</text>
<text class="r" x="40" y="104" font-size="50" fill="#fff">devkit</text>
<rect x="196" y="76" width="132" height="30" rx="4" fill="{VIOLET}" fill-opacity=".2" stroke="{VIOLET}"/>
<circle class="blink" cx="214" cy="91" r="4.5" fill="{TEAL}"/>
<text class="r" x="226" y="97" font-size="15" fill="{SILVER}" letter-spacing="2.5">IN TESTING</text>
<text class="r5" x="40" y="138" font-size="18" fill="{MUTED}">In-game tools for building FiveM servers. Point, click, paste.</text>
{''.join(obj_svg)}
<text class="m" x="440" y="274" font-size="12" fill="{MUTED}" letter-spacing="1.5">REWARD: open source // MIT</text>
<circle cx="820" cy="150" r="124" fill="none" stroke="{VIOLET}" stroke-opacity=".6" stroke-width="2"/>
<circle cx="820" cy="150" r="118" fill="url(#radar)"/>
<g clip-path="url(#radarclip)">
  <g stroke="{LINE}" fill="none"><circle cx="820" cy="150" r="40"/><circle cx="820" cy="150" r="80"/>
    <line x1="702" y1="150" x2="938" y2="150"/><line x1="820" y1="32" x2="820" y2="268"/></g>
  <polygon class="zone" points="{zone}" fill="{VIOLET}" stroke="{VIOLET}" stroke-width="1.5"/>
  {''.join(blips)}
  <path class="sweep" d="M820,150 L938,150 A118,118 0 0 0 903,66 Z" fill="url(#beam)"/>
</g>
<path d="M820,140 l7,16 l-7,-4 l-7,4 Z" fill="#fff"/>
'''
    return svg(1000, 300, body, style, defs)


def inventory():
    items = [
        ('lua', 'Lua'), ('ts', 'TypeScript'), ('js', 'JavaScript'), ('svelte', 'Svelte'),
        ('html', 'HTML'), ('css', 'CSS'), ('nodejs', 'Node'), ('vite', 'Vite'),
        ('mariadb', 'MariaDB'), ('git', 'Git'), ('rest', 'REST'), ('ws', 'WebSockets'),
    ]
    rarity = [VIOLET, BLUE, TEAL]
    tile_w, tile_h, gap = 148, 132, 12
    x0 = (1000 - (6 * tile_w + 5 * gap)) / 2
    slots = []

    for i, (key, label) in enumerate(items):
        x = x0 + (i % 6) * (tile_w + gap)
        y = 70 + (i // 6) * (tile_h + gap)
        ix, iy = x + tile_w / 2 - 32, y + 18

        if key in ('mariadb', 'rest', 'ws'):
            icon = f'<rect x="{ix}" y="{iy}" width="64" height="64" rx="15" fill="#242938"/>'
            if key == 'mariadb':
                path = (ASSETS / 'icons/mariadb-raw.svg').read_text().split('d="')[1].split('"')[0]
                icon += f'<path d="{path}" fill="#C49A6C" transform="translate({ix + 12} {iy + 12}) scale(1.67)"/>'
            elif key == 'rest':
                icon += f'<text class="m" x="{ix + 32}" y="{iy + 42}" font-size="28" fill="{TEAL}" text-anchor="middle">{{}}</text>'
            else:
                icon += (f'<path d="M{ix + 16},{iy + 26} h28 l-7,-7 M{ix + 48},{iy + 40} h-28 l7,7" fill="none" '
                         f'stroke="{TEAL}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            icon = image(base64.b64encode((ASSETS / f'icons/{key}.svg').read_bytes()).decode(), 'image/svg+xml',
                         x=ix, y=iy, width=64, height=64)

        hotkey = ''
        if i < 5:
            hotkey = (f'<rect x="{x + 8}" y="{y + 8}" width="20" height="20" rx="4" fill="#fff" fill-opacity=".08"/>'
                      f'<text class="r" x="{x + 18}" y="{y + 23}" font-size="14" fill="{SILVER}" text-anchor="middle">{i + 1}</text>')

        slots.append(f'''
<g>
  <rect x="{x}" y="{y}" width="{tile_w}" height="{tile_h}" rx="8" fill="#120e27" stroke="{LINE}"/>
  <rect class="glint" x="{x}" y="{y}" width="{tile_w}" height="{tile_h}" rx="8" fill="none" stroke="{TEAL}" stroke-width="1.5" style="animation-delay:{i * 0.6:.1f}s"/>
  {hotkey}
  <text class="r5" x="{x + tile_w - 10}" y="{y + 22}" font-size="12" fill="{MUTED}" text-anchor="end">x1</text>
  {icon}
  <text class="r" x="{x + tile_w / 2}" y="{y + 108}" font-size="15" fill="{SILVER}" text-anchor="middle" letter-spacing="1">{esc(label.upper())}</text>
  <rect x="{x + 1}" y="{y + tile_h - 5}" width="{tile_w - 2}" height="4" rx="2" fill="{rarity[i % 3]}" opacity=".85"/>
</g>''')

    style = BASE_STYLE + fonts('raj500', 'raj700', 'jbm500') + '''
.glint { opacity:0; animation: glint 7.2s ease-in-out infinite; }
@keyframes glint { 0%,100% { opacity:0 } 4% { opacity:1 } 12% { opacity:0 } }
'''
    body = f'''
{panel(10, 10, 980, 360)}
<text class="r" x="40" y="50" font-size="26" fill="#fff" letter-spacing="2">INVENTORY</text>
<text class="m" x="190" y="48" font-size="12" fill="{TEAL}" letter-spacing="2">TOOLBOX</text>
<text class="r5" x="960" y="48" font-size="15" fill="{MUTED}" text-anchor="end" letter-spacing="2">12 / 12 SLOTS</text>
{''.join(slots)}
'''
    return svg(1000, 380, body, style, PANEL_DEFS)


def history(data):
    g = data.get('github', {})
    days = g.get('days', [])
    if not days:
        days = [[(dt.date.today() - dt.timedelta(days=i)).isoformat(), 0] for i in range(364, -1, -1)]

    first = dt.date.fromisoformat(days[0][0])
    peak = max(c for _, c in days) or 1
    levels = ['#1a1633', INDIGO, DEEP, VIOLET, TEAL]

    cell, gap, x0, y0 = 13, 3, 80, 82
    cells, months, last_month = [], [], None
    for i, (date, count) in enumerate(days):
        d = dt.date.fromisoformat(date)
        col = (i + first.isoweekday() % 7) // 7
        row = d.isoweekday() % 7
        lvl = 0 if count == 0 else min(4, 1 + int(3 * count / peak + 0.5)) if count < peak else 4
        x, y = x0 + col * (cell + gap), y0 + row * (cell + gap)
        cells.append(f'<rect class="c" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{levels[lvl]}" '
                     f'style="animation-delay:{col * 0.025:.3f}s"/>')
        if d.day <= 7 and d.month != last_month and row == 0:
            months.append(f'<text class="r5" x="{x}" y="{y0 - 10}" font-size="12" fill="{MUTED}">{d.strftime("%b").upper()}</text>')
            last_month = d.month

    streak = best = 0
    for _, c in days:
        streak = streak + 1 if c else 0
        best = max(best, streak)

    stats = [('CONTRIBUTIONS', g.get('total', 0)), ('COMMITS', g.get('commits', 0)), ('PULL REQUESTS', g.get('prs', 0)),
             ('ACTIVE DAYS', sum(1 for _, c in days if c)), ('BEST DAY', peak if days else 0), ('LONGEST STREAK', best)]
    stat_svg = ''.join(
        f'<text class="r" x="{60 + i * 152}" y="262" font-size="30" fill="#fff">{v}</text>'
        f'<text class="r5" x="{60 + i * 152}" y="282" font-size="11" fill="{MUTED}" letter-spacing="2">{k}</text>'
        for i, (k, v) in enumerate(stats)
    )
    legend = ''.join(f'<rect x="{846 + i * 17}" y="196" width="13" height="13" rx="3" fill="{c}"/>' for i, c in enumerate(levels))

    style = BASE_STYLE + fonts('raj500', 'raj700', 'jbm500') + '''
.c { opacity:0; animation: c .4s ease-out forwards; }
@keyframes c { from { opacity:0; transform:translateY(4px) } to { opacity:1; transform:none } }
'''
    body = f'''
{panel(10, 10, 980, 290)}
<text class="r" x="40" y="50" font-size="26" fill="#fff" letter-spacing="2">PLAYER HISTORY</text>
<text class="m" x="268" y="48" font-size="12" fill="{TEAL}" letter-spacing="2">LAST 12 MONTHS</text>
{''.join(months)}
<text class="r5" x="40" y="{y0 + 1 * 16 + 11}" font-size="11" fill="{MUTED}">MON</text>
<text class="r5" x="40" y="{y0 + 3 * 16 + 11}" font-size="11" fill="{MUTED}">WED</text>
<text class="r5" x="40" y="{y0 + 5 * 16 + 11}" font-size="11" fill="{MUTED}">FRI</text>
{''.join(cells)}
<text class="r5" x="838" y="207" font-size="11" fill="{MUTED}" text-anchor="end">LESS</text>{legend}
<text class="r5" x="934" y="207" font-size="11" fill="{MUTED}">MORE</text>
<line x1="40" y1="226" x2="960" y2="226" stroke="{LINE}"/>
{stat_svg}
'''
    return svg(1000, 310, body, style, PANEL_DEFS)


def footer():
    style = BASE_STYLE + fonts('raj700', 'jbm500') + f'''
.key {{ animation: key 1.8s ease-in-out infinite; }}
@keyframes key {{ 0%,100% {{ stroke-opacity:.4 }} 50% {{ stroke-opacity:1 }} }}
.press {{ transform-origin:322px 60px; animation: press 1.8s ease-in-out infinite; }}
@keyframes press {{ 0%,80%,100% {{ transform:scale(1) }} 88% {{ transform:scale(.9) }} }}
'''
    defs = PANEL_DEFS + '<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>'
    body = f'''
<rect x="280" y="26" width="440" height="68" rx="10" fill="#0f0c22" fill-opacity=".95" stroke="{LINE}"/>
<g class="press">
  <rect class="key" x="300" y="38" width="44" height="44" rx="8" fill="{VIOLET}" fill-opacity=".25" stroke="{TEAL}" stroke-width="2" filter="url(#glow)"/>
  <rect x="300" y="38" width="44" height="44" rx="8" fill="{VIOLET}" fill-opacity=".25" stroke="{TEAL}" stroke-width="2"/>
  <text class="r" x="322" y="70" font-size="26" fill="#fff" text-anchor="middle">E</text>
</g>
<text class="r" x="362" y="66" font-size="24" fill="#fff" letter-spacing="2">JOIN ASTRA GAMING NETWORK</text>
<text class="m" x="500" y="114" font-size="12" fill="{MUTED}" text-anchor="middle" letter-spacing="2">discord.gg/agn</text>
'''
    return svg(1000, 124, body, style, defs)


if __name__ == '__main__':
    data = load_data()
    out = {
        'loading.svg': loading(),
        'license.svg': license_and_server(data),
        'mission.svg': mission(),
        'inventory.svg': inventory(),
        'history.svg': history(data),
        'footer.svg': footer(),
    }
    for name, content in out.items():
        (ASSETS / name).write_text(content)
        print(f'{name:14} {len(content) / 1024:6.0f} KB')
