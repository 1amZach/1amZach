"""Draws the profile art into assets/. Run it again after editing.

Colours are sampled from the Astra logo banner.
"""

import base64
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / 'assets'

# sampled from the Astra logo banner
PURPLE = '#9C2CF1'   # logo star
DEEP = '#6913E7'
INDIGO = '#3A05C7'
BLUE = '#216EEF'     # right side of the banner
TEAL = '#2BD9CC'     # neon name
ORCHID = '#C241F3'
SILVER = '#E2DEE9'   # the white half of the logo

# where the neon name sits in the 1500x600 banner, matches assets/name-mask.png
NAME_BOX = (378, 370, 1128, 600)

TITLE_FONT = "'Arial Black','Segoe UI Black','Helvetica Neue',Arial,sans-serif"
SANS = "'Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"

GLOW = '''<filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="{0}" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>'''


def header():
    """The banner, with current running through the neon name and a few layers on top."""
    random.seed(7)
    photo = base64.b64encode((ASSETS / 'banner.jpg').read_bytes()).decode()
    mask = base64.b64encode((ASSETS / 'name-mask.png').read_bytes()).decode()
    w, h = 1500, 600
    mx, my, mx2, my2 = NAME_BOX

    streaks = []
    for _ in range(9):
        x, y = random.uniform(-200, w), random.uniform(h * 0.3, h + 200)
        length = random.uniform(120, 260)
        colour = random.choice([PURPLE, PURPLE, BLUE, TEAL])
        dur, delay = random.uniform(2.5, 4.5), random.uniform(0, 6)
        streaks.append(
            f'<line class="streak" x1="{x:.0f}" y1="{y:.0f}" x2="{x + length * 0.7:.0f}" y2="{y - length:.0f}" '
            f'stroke="{colour}" style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>'
        )

    sparks = []
    for _ in range(40):
        x, y = random.uniform(0, w), random.uniform(h * 0.35, h)
        r = random.choice([1.2, 1.6, 2.0, 2.6])
        colour = random.choice([PURPLE, TEAL, ORCHID, SILVER])
        dur, delay = random.uniform(5, 9), random.uniform(0, 9)
        sparks.append(
            f'<circle class="spark" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{colour}" '
            f'style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>'
        )

    surge_w = 320
    travel = mx2 - mx + surge_w

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>
.streak {{ stroke-width:2.2; stroke-linecap:round; opacity:0; animation: streak 3.5s linear infinite; }}
@keyframes streak {{
  0% {{ opacity:0; transform:translate(0,0) }}
  15% {{ opacity:.9 }}
  60% {{ opacity:.7 }}
  100% {{ opacity:0; transform:translate(320px,-460px) }}
}}
.spark {{ opacity:0; animation: spark 7s ease-in-out infinite; }}
@keyframes spark {{
  0% {{ opacity:0; transform:translate(0,0) }}
  20% {{ opacity:.9 }}
  100% {{ opacity:0; transform:translate(30px,-170px) }}
}}
.sweep {{ animation: sweep 9s ease-in-out infinite; }}
@keyframes sweep {{ 0% {{ transform:translateX(-700px) }} 40%,100% {{ transform:translateX({w + 700}px) }} }}
.surge {{ animation: surge 4s cubic-bezier(.5,0,.4,1) infinite; }}
@keyframes surge {{ 0% {{ transform:translateX(0) }} 50%,100% {{ transform:translateX({travel}px) }} }}
.charge {{ animation: charge 4s linear infinite; }}
@keyframes charge {{ 0%,46% {{ opacity:0 }} 50% {{ opacity:.85 }} 53% {{ opacity:.2 }} 56% {{ opacity:.6 }} 75%,100% {{ opacity:0 }} }}
.halo {{ animation: halo 4s ease-in-out infinite; }}
@keyframes halo {{ 0%,100% {{ opacity:.3 }} 50% {{ opacity:1 }} }}
</style>
<defs>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="22"/></clipPath>
  <mask id="name" maskUnits="userSpaceOnUse" x="0" y="0" width="{w}" height="{h}">
    <image x="{mx}" y="{my}" width="{mx2 - mx}" height="{my2 - my}" href="data:image/png;base64,{mask}" xlink:href="data:image/png;base64,{mask}"/>
  </mask>
  <linearGradient id="surgefill" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{TEAL}" stop-opacity="0"/>
    <stop offset=".35" stop-color="{TEAL}" stop-opacity="1"/>
    <stop offset=".52" stop-color="#ffffff" stop-opacity="1"/>
    <stop offset=".62" stop-color="#ffffff" stop-opacity="1"/>
    <stop offset=".78" stop-color="{ORCHID}" stop-opacity="1"/>
    <stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="sweepfill" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <radialGradient id="vignette" cx=".5" cy=".5" r=".75">
    <stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/>
  </radialGradient>
  <filter id="blur" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.2"/></filter>
  <filter id="halo" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="10"/></filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".16"/></pattern>
</defs>
<g clip-path="url(#frame)">
  <image width="{w}" height="{h}" href="data:image/jpeg;base64,{photo}" xlink:href="data:image/jpeg;base64,{photo}"/>
  <g class="halo" filter="url(#halo)"><g mask="url(#name)"><rect x="{mx}" y="{my}" width="{mx2 - mx}" height="{my2 - my}" fill="{TEAL}"/></g></g>
  <g mask="url(#name)">
    <rect class="charge" x="{mx}" y="{my}" width="{mx2 - mx}" height="{my2 - my}" fill="{SILVER}"/>
    <rect class="surge" x="{mx - surge_w}" y="{my}" width="{surge_w}" height="{my2 - my}" fill="url(#surgefill)"/>
  </g>
  <g filter="url(#blur)">{"".join(streaks)}</g>
  {"".join(sparks)}
  <rect class="sweep" x="-500" y="0" width="500" height="{h}" fill="url(#sweepfill)" transform="skewX(-20)"/>
  <rect width="{w}" height="{h}" fill="url(#scan)"/>
  <rect width="{w}" height="{h}" fill="url(#vignette)"/>
</g>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="22" fill="none" stroke="{PURPLE}" stroke-opacity=".4" stroke-width="2"/>
</svg>
'''


def avatar():
    photo = base64.b64encode((ASSETS / 'avatar.jpg').read_bytes()).decode()
    s, c, r = 240, 120, 92

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{s}" height="{s}" viewBox="0 0 {s} {s}">
<style>
.spin {{ animation: spin 6s linear infinite; transform-origin:{c}px {c}px; }}
.spin2 {{ animation: spin 10s linear infinite reverse; transform-origin:{c}px {c}px; }}
@keyframes spin {{ to {{ transform:rotate(360deg) }} }}
.halo {{ animation: halo 3s ease-in-out infinite; }}
@keyframes halo {{ 0%,100% {{ opacity:.45 }} 50% {{ opacity:.95 }} }}
</style>
<defs>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{TEAL}"/><stop offset=".35" stop-color="{BLUE}"/><stop offset=".65" stop-color="{DEEP}"/><stop offset="1" stop-color="{ORCHID}"/>
  </linearGradient>
  <clipPath id="circle"><circle cx="{c}" cy="{c}" r="{r}"/></clipPath>
  <filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<g class="spin">
  <circle class="halo" cx="{c}" cy="{c}" r="{r + 8}" fill="none" stroke="url(#ring)" stroke-width="10" filter="url(#blur)"/>
  <circle cx="{c}" cy="{c}" r="{r + 7}" fill="none" stroke="url(#ring)" stroke-width="3.5"/>
  <circle cx="{c}" cy="{c - r - 7}" r="4" fill="#fff"/>
</g>
<circle class="spin2" cx="{c}" cy="{c}" r="{r + 16}" fill="none" stroke="{PURPLE}" stroke-opacity=".55" stroke-width="1.2" stroke-dasharray="3 9"/>
<image clip-path="url(#circle)" x="{c - r}" y="{c - r}" width="{r * 2}" height="{r * 2}" href="data:image/jpeg;base64,{photo}" xlink:href="data:image/jpeg;base64,{photo}"/>
</svg>
'''


def card():
    chips, x = [], 40
    for label in ('Coords overlay', 'Entity inspector', 'Prop placer', 'Zone builder'):
        w = len(label) * 7.4 + 24
        chips.append(
            f'<rect x="{x:.0f}" y="138" width="{w:.0f}" height="30" rx="15" fill="{PURPLE}" fill-opacity=".1" stroke="{PURPLE}" stroke-opacity=".5"/>'
            f'<text x="{x + w / 2:.0f}" y="158" text-anchor="middle">{label}</text>'
        )
        x += w + 8

    code = [
        ('#ff7b72', 'lib.zones.poly', '#e6edf3', '({'),
        ('#e6edf3', '  points = {', None, None),
        ('#79c0ff', '    vec3', '#a5d6ff', '(215.12, -810.44, 30.73),'),
        ('#79c0ff', '    vec3', '#a5d6ff', '(228.90, -815.02, 30.73),'),
        ('#79c0ff', '    vec3', '#a5d6ff', '(224.31, -828.67, 30.73),'),
        ('#e6edf3', '  },', None, None),
        ('#e6edf3', '  thickness = ', '#a5d6ff', '4.00,'),
        ('#e6edf3', '})', None, None),
    ]
    lines = []
    for i, (c1, t1, c2, t2) in enumerate(code):
        tail = f'<tspan fill="{c2}">{t2}</tspan>' if t2 else ''
        lines.append(f'<text x="640" y="{82 + i * 17}" fill="{c1}" class="ln" style="animation-delay:{0.25 * i:.2f}s">'
                     f'{t1.replace(" ", "&#160;")}{tail}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="250" viewBox="0 0 1000 250">
<style>
.ln {{ opacity:0; animation: in .4s ease-out forwards; }}
@keyframes in {{ from {{ opacity:0; transform:translateX(-6px) }} to {{ opacity:1; transform:none }} }}
.border {{ stroke-dasharray: 260 2400; animation: run 6s linear infinite; }}
@keyframes run {{ to {{ stroke-dashoffset:-2660 }} }}
.dot {{ animation: pulse 1.6s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f1120"/><stop offset="1" stop-color="#1a0f2e"/></linearGradient>
  <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{TEAL}"/><stop offset=".5" stop-color="{PURPLE}"/><stop offset="1" stop-color="{ORCHID}"/></linearGradient>
  {GLOW.format(3)}
</defs>
<rect x="1" y="1" width="998" height="248" rx="16" fill="url(#bg)" stroke="#30363d"/>
<rect class="border" x="1" y="1" width="998" height="248" rx="16" fill="none" stroke="url(#edge)" stroke-width="2.5" filter="url(#glow)"/>
<g font-family="{SANS}">
  <text x="40" y="66" font-size="38" font-weight="800" fill="#ffffff">devkit</text>
  <rect x="196" y="40" width="138" height="28" rx="14" fill="{PURPLE}" fill-opacity=".15" stroke="{PURPLE}" stroke-opacity=".7"/>
  <circle class="dot" cx="214" cy="54" r="5" fill="{TEAL}"/>
  <text x="273" y="59" text-anchor="middle" font-size="12" font-weight="700" fill="{SILVER}" textLength="90" lengthAdjust="spacingAndGlyphs">IN TESTING</text>
  <text x="40" y="104" font-size="17" fill="#c9d1d9">In-game tools for building FiveM servers.</text>
  <text x="40" y="126" font-size="17" fill="#8b949e">Point, click, paste. No more guessing coords.</text>
  <g font-size="12" font-weight="600" fill="{SILVER}">{"".join(chips)}</g>
  <text x="40" y="212" font-size="14" fill="#8b949e"><tspan fill="#2C7BE5">&#9679;</tspan> Lua   <tspan dx="14" fill="{PURPLE}">&#9679;</tspan> ox_lib   <tspan dx="14" fill="{TEAL}">&#9679;</tspan> ESX · QBCore · Qbox · standalone</text>
</g>
<rect x="615" y="34" width="350" height="182" rx="10" fill="#0a0b14" stroke="#30363d"/>
<circle cx="636" cy="52" r="5" fill="#ff5f57"/><circle cx="654" cy="52" r="5" fill="#febc2e"/><circle cx="672" cy="52" r="5" fill="#28c840"/>
<text x="950" y="56" text-anchor="end" font-family="Consolas,monospace" font-size="11" fill="#6e7681">copied to clipboard</text>
<g font-family="{MONO}" font-size="13">{"".join(lines)}</g>
</svg>
'''


if __name__ == '__main__':
    (ASSETS / 'header.svg').write_text(header())
    (ASSETS / 'avatar.svg').write_text(avatar())
    (ASSETS / 'devkit-card.svg').write_text(card())
    print('ok')
