"""Draws assets/header.svg and assets/devkit.svg. Run it again after editing."""

import random
import sys
from pathlib import Path

out = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent / "assets")
random.seed(7)

W, H, HORIZON, CX = 1200, 340, 222, 600

# ---------- header ----------
stars = []
for _ in range(70):
    x, y = random.uniform(10, W - 10), random.uniform(8, HORIZON - 30)
    r = random.choice([0.6, 0.8, 1.0, 1.3])
    d = random.uniform(0, 4)
    stars.append(f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" style="animation-delay:-{d:.2f}s"/>')

stripes = []
for i, y in enumerate(range(HORIZON - 70, HORIZON, 12)):
    stripes.append(f'<rect x="0" y="{y}" width="{W}" height="{2 + i * 1.3:.1f}" fill="#000"/>')

verticals = []
for x in range(-2400, W + 2400 + 1, 120):
    verticals.append(f'<line x1="{CX}" y1="{HORIZON}" x2="{x}" y2="{H}"/>')

horizontals = []
n = 7
for i in range(n):
    begin = -i * (4.2 / n)
    horizontals.append(
        f'<line x1="0" x2="{W}" y1="{HORIZON}" y2="{HORIZON}">'
        f'<animate attributeName="y1" values="{HORIZON};{H}" dur="4.2s" begin="{begin:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines="0.55 0 1 1"/>'
        f'<animate attributeName="y2" values="{HORIZON};{H}" dur="4.2s" begin="{begin:.2f}s" repeatCount="indefinite" calcMode="spline" keySplines="0.55 0 1 1"/>'
        f'<animate attributeName="stroke-opacity" values="0;0.9" dur="4.2s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
        f'</line>'
    )

title_font = "'Arial Black','Segoe UI Black','Helvetica Neue',Arial,sans-serif"
mono = "'JetBrains Mono','Fira Code',Consolas,'Courier New',monospace"

header = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.tw {{ fill:#fff; animation: tw 4s ease-in-out infinite; }}
@keyframes tw {{ 0%,100% {{ opacity:.15 }} 50% {{ opacity:.9 }} }}
.sun {{ animation: pulse 6s ease-in-out infinite; transform-origin:{CX}px {HORIZON}px; }}
@keyframes pulse {{ 0%,100% {{ transform:scale(1) }} 50% {{ transform:scale(1.025) }} }}
.g1 {{ animation: g1 5s steps(1) infinite; }}
.g2 {{ animation: g2 5s steps(1) infinite; }}
@keyframes g1 {{ 0%,86%,100% {{ transform:translate(0,0) }} 88% {{ transform:translate(-6px,2px) }} 90% {{ transform:translate(5px,-2px) }} 92% {{ transform:translate(-3px,0) }} }}
@keyframes g2 {{ 0%,86%,100% {{ transform:translate(0,0) }} 88% {{ transform:translate(6px,-2px) }} 90% {{ transform:translate(-5px,2px) }} 92% {{ transform:translate(3px,1px) }} }}
.caret {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity:0 }} }}
</style>
<defs>
  <clipPath id="frame"><rect width="{W}" height="{H}" rx="18"/></clipPath>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#06050c"/><stop offset=".55" stop-color="#160a26"/><stop offset="1" stop-color="#3a0f3f"/>
  </linearGradient>
  <linearGradient id="sunfill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#FFE38A"/><stop offset=".5" stop-color="#FFAA1E"/><stop offset="1" stop-color="#FF3D7F"/>
  </linearGradient>
  <linearGradient id="floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#1b0a24"/><stop offset="1" stop-color="#05040a"/>
  </linearGradient>
  <linearGradient id="titlefill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#FFD59A"/>
  </linearGradient>
  <mask id="sunmask">
    <rect width="{W}" height="{HORIZON}" fill="#fff"/>
    {"".join(stripes)}
  </mask>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softglow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="28"/></filter>
  <filter id="lineglow"><feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".22"/></pattern>
</defs>
<g clip-path="url(#frame)">
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  {"".join(stars)}
  <g class="sun">
    <circle cx="{CX}" cy="{HORIZON - 40}" r="150" fill="#FF7A3D" opacity=".45" filter="url(#softglow)"/>
    <circle cx="{CX}" cy="{HORIZON - 40}" r="140" fill="url(#sunfill)" mask="url(#sunmask)"/>
  </g>
  <rect y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#floor)"/>
  <g stroke="#FF5FA8" stroke-opacity=".55" stroke-width="1.4" filter="url(#lineglow)">{"".join(verticals)}</g>
  <g stroke="#FFAA1E" stroke-width="1.6" filter="url(#lineglow)">{"".join(horizontals)}</g>
  <line x1="0" x2="{W}" y1="{HORIZON}" y2="{HORIZON}" stroke="#FFB347" stroke-width="2.5" filter="url(#glow)"/>
  <g font-family="{title_font}" font-size="112" font-weight="900" font-style="italic" text-anchor="middle" letter-spacing="6" transform="translate({CX} 0) skewX(-6) translate(-{CX} 0)">
    <text class="g1" x="{CX}" y="166" fill="#00E5FF" opacity=".75">IAMZACH</text>
    <text class="g2" x="{CX}" y="166" fill="#FF2E88" opacity=".75">IAMZACH</text>
    <text x="{CX}" y="166" fill="url(#titlefill)" filter="url(#glow)">IAMZACH</text>
  </g>
  <g font-family="{mono}" font-size="17" text-anchor="middle">
    <rect x="{CX - 260}" y="262" width="520" height="40" rx="20" fill="#05040a" fill-opacity=".78" stroke="#FFAA1E" stroke-opacity=".6"/>
    <text x="{CX - 6}" y="288" fill="#FFE7C2" letter-spacing="4">FIVEM DEV  //  LUA  //  OPEN SOURCE</text>
    <rect class="caret" x="{CX + 236}" y="273" width="9" height="18" fill="#FFAA1E"/>
  </g>
  <rect width="{W}" height="{H}" fill="url(#scan)"/>
</g>
</svg>
'''

# ---------- devkit card ----------
chips = ['Coords overlay', 'Entity inspector', 'Prop placer', 'Zone builder']
chip_svg, x = [], 40
for c in chips:
    w = len(c) * 7.4 + 24
    chip_svg.append(
        f'<rect x="{x:.0f}" y="138" width="{w:.0f}" height="30" rx="15" fill="#FFAA1E" fill-opacity=".1" stroke="#FFAA1E" stroke-opacity=".45"/>'
        f'<text x="{x + w / 2:.0f}" y="158" text-anchor="middle">{c}</text>'
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
code_svg = []
for i, (c1, t1, c2, t2) in enumerate(code):
    y = 82 + i * 17
    tail = f'<tspan fill="{c2}">{t2}</tspan>' if t2 else ''
    code_svg.append(
        f'<text x="640" y="{y}" fill="{c1}" style="animation-delay:{0.25 * i:.2f}s" class="ln">'
        f'{t1.replace(" ", "&#160;")}{tail}</text>'
    )

card = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="250" viewBox="0 0 1000 250">
<style>
.ln {{ opacity:0; animation: in .4s ease-out forwards; }}
@keyframes in {{ from {{ opacity:0; transform:translateX(-6px) }} to {{ opacity:1; transform:none }} }}
.border {{ stroke-dasharray: 260 2400; animation: run 6s linear infinite; }}
@keyframes run {{ to {{ stroke-dashoffset:-2660 }} }}
.dot {{ animation: pulse 1.6s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.25 }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#11141b"/><stop offset="1" stop-color="#1a0f22"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect x="1" y="1" width="998" height="248" rx="16" fill="url(#bg)" stroke="#30363d"/>
<rect class="border" x="1" y="1" width="998" height="248" rx="16" fill="none" stroke="#FFAA1E" stroke-width="2.5" filter="url(#glow)"/>
<g font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif">
  <text x="40" y="66" font-size="38" font-weight="800" fill="#ffffff">devkit</text>
  <rect x="196" y="40" width="112" height="28" rx="14" fill="#FFAA1E" fill-opacity=".15" stroke="#FFAA1E" stroke-opacity=".6"/>
  <circle class="dot" cx="214" cy="54" r="5" fill="#FFAA1E"/>
  <text x="226" y="59" font-size="13" font-weight="700" fill="#FFAA1E" letter-spacing="1.5">IN TESTING</text>
  <text x="40" y="104" font-size="17" fill="#c9d1d9">In-game tools for building FiveM servers.</text>
  <text x="40" y="126" font-size="17" fill="#8b949e">Point, click, paste. No more guessing coords.</text>
  <g font-size="12" font-weight="600" fill="#FFD59A">{"".join(chip_svg)}</g>
  <text x="40" y="212" font-size="14" fill="#8b949e"><tspan fill="#2C7BE5">&#9679;</tspan> Lua   <tspan dx="14" fill="#FFAA1E">&#9679;</tspan> ox_lib   <tspan dx="14" fill="#3fb950">&#9679;</tspan> ESX · QBCore · Qbox · standalone</text>
</g>
<rect x="615" y="34" width="350" height="182" rx="10" fill="#0a0c10" stroke="#30363d"/>
<circle cx="636" cy="52" r="5" fill="#ff5f57"/><circle cx="654" cy="52" r="5" fill="#febc2e"/><circle cx="672" cy="52" r="5" fill="#28c840"/>
<text x="950" y="56" text-anchor="end" font-family="Consolas,monospace" font-size="11" fill="#6e7681">copied to clipboard</text>
<g font-family="'JetBrains Mono',Consolas,'Courier New',monospace" font-size="13">{"".join(code_svg)}</g>
</svg>
'''

with open(f'{out}/header.svg', 'w') as f:
    f.write(header)
with open(f'{out}/devkit.svg', 'w') as f:
    f.write(card)
print('ok')
