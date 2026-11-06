#!/usr/bin/env python3
"""Generates the course banner illustrations (SVG, 1180x404) in the ESA identity.
Run from the repo root:  python3 tools/course_art.py"""
import math, random

W, H = 1180, 404
Y, Y2, WH, MU, MU2, K = "#F3AE12", "#FFD36A", "#F5F5F2", "#3A3A42", "#26262C", "#0B0B0B"

def base(body, glow=(760, 200), accent=Y):
    gx, gy = glow
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#151518"/><stop offset="1" stop-color="#0A0A0B"/></linearGradient>
<radialGradient id="gl" cx="{gx/W:.3f}" cy="{gy/H:.3f}" r=".55"><stop offset="0" stop-color="{accent}" stop-opacity=".28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
<linearGradient id="gy" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{Y2}"/><stop offset="1" stop-color="{Y}"/></linearGradient>
<linearGradient id="panel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1E1E23"/><stop offset="1" stop-color="#141417"/></linearGradient>
<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#FFFFFF" fill-opacity=".06"/></pattern>
<filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".55"/></filter>
<filter id="gw" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#dots)"/><rect width="{W}" height="{H}" fill="url(#gl)"/>
<path d="M0 {H} L{W*0.42:.0f} {H} L{W*0.18:.0f} 0 L0 0Z" fill="{Y}" opacity=".035"/>
{body}
</svg>'''

def panel(x, y, w, h, r=16, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#panel)" stroke="#34343C" stroke-width="1.5" filter="url(#sh)" {extra}/>'

def bars(x, y, n, w, gap, hs, col=MU):
    return "".join(f'<rect x="{x+i*(w+gap)}" y="{y-h}" width="{w}" height="{h}" rx="3" fill="{col}"/>' for i, h in enumerate(hs[:n]))

def line(x, y, w, h=7, col=MU, r=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{col}"/>'

def icon(path, x, y, s=1, col=K, sw=2):
    return f'<g transform="translate({x} {y}) scale({s})" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{path}</g>'

ART = {}

# ---------- Data Analysis: messy records -> clean chart -> insight ----------
random.seed(3)
rows = ""
for r in range(6):
    for c in range(4):
        w = random.choice([34, 46, 58, 28])
        col = "#FF6B5B" if (r, c) in [(1, 2), (4, 1)] else MU
        rows += line(150 + c * 70, 132 + r * 30, w, 8, col)
ART["data-analysis"] = base(f'''
{panel(130, 92, 300, 230)}<rect x="130" y="92" width="300" height="30" rx="16" fill="#25252B"/>{line(150,104,60,7,"#55555E")}{line(220,104,40,7,"#55555E")}
{rows}
<g stroke="{Y}" stroke-width="3" fill="none" stroke-linecap="round" stroke-dasharray="2 10"><path d="M445 207 H520"/></g><path d="M516 197 L532 207 L516 217Z" fill="{Y}"/>
{panel(545, 60, 470, 290)}
{line(570,84,120,9,WH)}{line(570,102,80,7,"#55555E")}
<g>{bars(575, 300, 8, 34, 16, [70, 95, 82, 120, 108, 150, 172, 205], "#2E2E35")}</g>
<rect x="925" y="95" width="34" height="205" rx="3" fill="url(#gy)"/>
<path d="M592 260 L642 238 L692 248 L742 205 L792 214 L842 168 L892 150 L942 104" fill="none" stroke="{WH}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<g fill="{K}" stroke="{WH}" stroke-width="3">{"".join(f'<circle cx="{x}" cy="{y}" r="5"/>' for x,y in [(592,260),(642,238),(692,248),(742,205),(792,214),(842,168),(892,150)])}</g>
<circle cx="942" cy="104" r="9" fill="{Y}" filter="url(#gw)"/>
<g filter="url(#sh)"><rect x="830" y="22" width="170" height="54" rx="12" fill="url(#gy)"/>{icon('<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>', 846, 37, 1, K)}{line(880,38,90,8,K)}{line(880,54,60,7,"#5a4106")}</g>
''', (780, 200))

# ---------- Cybersecurity: network, detection, containment ----------
nodes = [(220, 110), (180, 270), (330, 200), (450, 90), (470, 310), (850, 110), (900, 300), (1010, 200), (760, 330)]
links = [(0, 2), (1, 2), (2, 3), (2, 4), (5, 7), (6, 7), (8, 6), (5, 3)]
L = "".join(f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" y2="{nodes[b][1]}" stroke="#34343C" stroke-width="2"/>' for a, b in links)
L += "".join(f'<line x1="{x}" y1="{y}" x2="640" y2="200" stroke="{Y}" stroke-opacity=".55" stroke-width="2" stroke-dasharray="4 7"/>' for x, y in [nodes[3], nodes[4], nodes[5], nodes[6], nodes[2], nodes[7]])
N = ""
for i, (x, y) in enumerate(nodes):
    alert = i == 4
    N += f'<circle cx="{x}" cy="{y}" r="{16 if not alert else 18}" fill="{"#2A1513" if alert else "#1B1B20"}" stroke="{"#FF6B5B" if alert else "#55555E"}" stroke-width="2"/>'
    N += f'<circle cx="{x}" cy="{y}" r="5" fill="{"#FF6B5B" if alert else Y}"/>'
N += '<circle cx="470" cy="310" r="30" fill="none" stroke="#FF6B5B" stroke-opacity=".5" stroke-width="2"/><circle cx="470" cy="310" r="44" fill="none" stroke="#FF6B5B" stroke-opacity=".25" stroke-width="2"/>'
ART["cybersecurity"] = base(f'''
{L}{N}
<circle cx="640" cy="200" r="132" fill="none" stroke="{Y}" stroke-opacity=".12" stroke-width="2"/><circle cx="640" cy="200" r="100" fill="none" stroke="{Y}" stroke-opacity=".22" stroke-width="2" stroke-dasharray="3 8"/>
<g filter="url(#gw)"><path d="M640 92 L718 122 V196 C718 248 684 288 640 306 C596 288 562 248 562 196 V122Z" fill="url(#gy)"/></g>
<path d="M640 116 L698 138 V194 C698 234 672 264 640 278 C608 264 582 234 582 194 V138Z" fill="{K}"/>
<rect x="616" y="186" width="48" height="40" rx="7" fill="none" stroke="{Y}" stroke-width="5"/><path d="M626 186 V172 a14 14 0 0 1 28 0 V186" fill="none" stroke="{Y}" stroke-width="5"/><circle cx="640" cy="205" r="5" fill="{Y}"/>
<g filter="url(#sh)"><rect x="930" y="24" width="190" height="64" rx="12" fill="url(#panel)" stroke="#34343C"/>{icon('<path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>', 946, 42, 1.15, Y)}{line(984,44,110,8,WH)}{line(984,62,76,7,"#55555E")}</g>
''', (640, 200))

# ---------- Graphic Design: artboard, bezier, palette, layers ----------
ART["graphic-design"] = base(f'''
{panel(300, 40, 580, 324, 18)}
<g stroke="#2A2A31" stroke-width="1">{"".join(f'<line x1="{300+i*58}" y1="40" x2="{300+i*58}" y2="364"/>' for i in range(1,10))}{"".join(f'<line x1="300" y1="{40+i*54}" x2="880" y2="{40+i*54}"/>' for i in range(1,6))}</g>
<circle cx="520" cy="200" r="92" fill="url(#gy)"/>
<rect x="560" y="150" width="170" height="170" rx="26" fill="none" stroke="{WH}" stroke-width="5" transform="rotate(12 645 235)"/>
<path d="M360 300 C430 120 600 330 700 150 S820 100 840 90" fill="none" stroke="{WH}" stroke-width="4" stroke-linecap="round"/>
<g stroke="{Y}" stroke-width="2"><line x1="700" y1="150" x2="640" y2="250"/><line x1="700" y1="150" x2="760" y2="50"/></g>
<g fill="{K}" stroke="{Y}" stroke-width="3"><rect x="692" y="142" width="16" height="16"/><circle cx="640" cy="250" r="7"/><circle cx="760" cy="50" r="7"/><rect x="352" y="292" width="16" height="16"/><rect x="832" y="82" width="16" height="16"/></g>
<rect x="430" y="108" width="190" height="190" fill="none" stroke="#5B9BE6" stroke-width="1.5" stroke-dasharray="6 5"/>
<g filter="url(#sh)"><rect x="120" y="70" width="140" height="250" rx="14" fill="url(#panel)" stroke="#34343C"/>
{"".join(f'<rect x="138" y="{94+i*44}" width="104" height="32" rx="8" fill="{"#2B2B32" if i!=1 else "rgba(243,174,18,.15)"}" stroke="{"#34343C" if i!=1 else Y}"/>{line(178,106+i*44,50,7,"#66666F" if i!=1 else Y)}<rect x="148" y="{102+i*44}" width="18" height="16" rx="3" fill="{["#F5F5F2",Y,"#5B9BE6","#4FBF8B","#FF8A3D"][i]}"/>' for i in range(5))}</g>
<g filter="url(#sh)"><rect x="920" y="110" width="150" height="190" rx="14" fill="url(#panel)" stroke="#34343C"/>
{"".join(f'<circle cx="{955+(i%3)*40}" cy="{148+(i//3)*44}" r="15" fill="{c}"/>' for i,c in enumerate([Y,Y2,"#F5F5F2","#0B0B0B","#5B9BE6","#4FBF8B"]))}<circle cx="955" cy="148" r="20" fill="none" stroke="{WH}" stroke-width="2"/>{line(940,250,110,8,"#3A3A42")}{line(940,250,70,8,Y)}{line(940,272,110,8,"#3A3A42")}{line(940,272,40,8,WH)}</g>
''', (560, 200))

# ---------- Learning & Development: gap -> learn -> practice -> assess -> grow ----------
steps = [(170, 300), (380, 250), (590, 200), (800, 150), (1010, 95)]
icons = ['<circle cx="12" cy="12" r="9"/><path d="M12 7v5M12 16h.01"/>',
         '<path d="M2 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H2z"/><path d="M22 4h-7a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h8z"/>',
         '<path d="M14.7 6.3a4 4 0 0 0 5.4 5.4L21 13l-8 8-2.6-2.6"/><path d="M14.7 6.3L13 4.6a2 2 0 0 0-2.8 0L3 11.8"/><path d="M7 15l-4 4 2 2 4-4"/>',
         '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 14l2 2 4-4"/>',
         '<path d="M22 7l-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>']
path = "M" + " L".join(f"{x} {y}" for x, y in steps)
S = ""
for i, (x, y) in enumerate(steps):
    last = i == 4
    S += f'<rect x="{x-60}" y="{y}" width="120" height="{H-y}" fill="{"url(#gy)" if last else "#1C1C21"}" stroke="{"none" if last else "#2E2E35"}" opacity="{1 if last else .9}"/>'
    S += f'<circle cx="{x}" cy="{y}" r="{30 if last else 26}" fill="{Y if i>0 else "#1B1B20"}" stroke="{Y}" stroke-width="3" {"filter=\"url(#gw)\"" if last else ""}/>'
    S += icon(icons[i], x - 13, y - 13, 1.1, K if i > 0 else Y)
ART["learning-development"] = base(f'''
{S}
<path d="{path}" fill="none" stroke="{WH}" stroke-width="3" stroke-dasharray="3 9" stroke-linecap="round" opacity=".7"/>
<g filter="url(#sh)"><rect x="110" y="40" width="250" height="80" rx="14" fill="url(#panel)" stroke="#34343C"/>{line(132,62,120,8,WH)}{line(132,84,206,10,"#2E2E35",5)}{line(132,84,140,10,Y,5)}{line(132,102,60,7,"#55555E")}</g>
''', (1000, 120))

# ---------- Performance Management: goals, KPI gauge, coaching, results ----------
ang = lambda a: (math.cos(math.radians(a)), math.sin(math.radians(a)))
cx, cy, R = 590, 270, 150
arc = lambda a0, a1, r: f"M{cx+r*ang(a0)[0]:.1f} {cy+r*ang(a0)[1]:.1f} A{r} {r} 0 0 1 {cx+r*ang(a1)[0]:.1f} {cy+r*ang(a1)[1]:.1f}"
ART["performance-management"] = base(f'''
<path d="{arc(180,360,R)}" fill="none" stroke="#26262C" stroke-width="30" stroke-linecap="round"/>
<path d="{arc(180,318,R)}" fill="none" stroke="url(#gy)" stroke-width="30" stroke-linecap="round" filter="url(#gw)"/>
<g stroke="#3A3A42" stroke-width="3">{"".join(f'<line x1="{cx+112*ang(a)[0]:.1f}" y1="{cy+112*ang(a)[1]:.1f}" x2="{cx+124*ang(a)[0]:.1f}" y2="{cy+124*ang(a)[1]:.1f}"/>' for a in range(180,361,20))}</g>
<line x1="{cx}" y1="{cy}" x2="{cx+100*ang(318)[0]:.1f}" y2="{cy+100*ang(318)[1]:.1f}" stroke="{WH}" stroke-width="6" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="14" fill="{WH}"/><circle cx="{cx}" cy="{cy}" r="6" fill="{K}"/>
<g filter="url(#sh)">{panel(110, 60, 250, 280)}
{"".join(f'<rect x="132" y="{86+i*62}" width="206" height="48" rx="10" fill="#1A1A1F" stroke="#2E2E35"/><circle cx="156" cy="{110+i*62}" r="11" fill="{Y if i<2 else "none"}" stroke="{Y}" stroke-width="2.5"/>{"<path d=\"M150 %d l4 4 8-8\" fill=\"none\" stroke=\"#0B0B0B\" stroke-width=\"2.5\" stroke-linecap=\"round\"/>" % (110+i*62) if i<2 else ""}{line(178,102+i*62,[120,100,130,90][i],7,WH if i<2 else "#66666F")}{line(178,116+i*62,[70,90,60,80][i],6,"#4A4A52")}' for i in range(4))}</g>
<g filter="url(#sh)"><rect x="820" y="70" width="250" height="100" rx="16" fill="url(#panel)" stroke="#34343C"/><circle cx="858" cy="108" r="20" fill="#2B2B32"/>{icon('<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0 1 14 0v1"/>', 846, 96, 1, WH)}{line(892,96,150,8,WH)}{line(892,114,120,7,"#55555E")}{line(892,130,140,7,"#55555E")}</g>
<g filter="url(#sh)"><rect x="860" y="200" width="250" height="110" rx="16" fill="url(#gy)"/>{bars(884, 290, 6, 22, 12, [26, 34, 30, 46, 54, 66], "#0B0B0B")}<path d="M884 250 L920 238 L956 244 L992 222 L1028 210 L1064 188" fill="none" stroke="{K}" stroke-width="3" stroke-linecap="round"/></g>
''', (590, 240))

# ---------- Healthcare Facility Management: patient flow through a hospital ----------
flow = [(250, 300, '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a7 7 0 0 1 14 0v1"/>'), (450, 300, '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M9 14l2 2 4-4"/>'),
        (650, 300, '<path d="M12 5v14M5 12h14"/>'), (850, 300, '<path d="M2 20h20M4 20V10l8-6 8 6v10M10 20v-5h4v5"/>')]
F = ""
for i, (x, y, p) in enumerate(flow):
    F += f'<circle cx="{x}" cy="{y}" r="32" fill="{Y if i in (0,3) else "#1B1B20"}" stroke="{Y}" stroke-width="3"/>' + icon(p, x - 14, y - 14, 1.17, K if i in (0, 3) else Y)
F += "".join(f'<path d="M{flow[i][0]+40} 300 H{flow[i+1][0]-46}" stroke="{WH}" stroke-width="3" stroke-dasharray="3 8" stroke-linecap="round" opacity=".7"/><path d="M{flow[i+1][0]-50} 292 l10 8 -10 8" fill="none" stroke="{WH}" stroke-width="3" stroke-linecap="round"/>' for i in range(3))
ART["healthcare-facilities"] = base(f'''
<g filter="url(#sh)"><path d="M380 230 V90 H560 V60 H740 V90 H920 V230" fill="url(#panel)" stroke="#34343C" stroke-width="2"/></g>
{"".join(f'<rect x="{400+c*42}" y="{110+r*40}" width="26" height="24" rx="4" fill="{"#2E2E35" if (r,c)!=(1,1) else Y}"/>' for r in range(3) for c in range(4))}
{"".join(f'<rect x="{772+c*42}" y="{110+r*40}" width="26" height="24" rx="4" fill="{"#2E2E35" if (r,c)!=(0,2) else Y}"/>' for r in range(3) for c in range(4))}
<rect x="610" y="78" width="80" height="80" rx="16" fill="url(#gy)"/><path d="M650 96 V140 M628 118 H672" stroke="{K}" stroke-width="10" stroke-linecap="round"/>
<rect x="615" y="180" width="70" height="50" rx="6" fill="#2E2E35"/>
<line x1="150" y1="230" x2="1030" y2="230" stroke="#34343C" stroke-width="2"/>
{F}
<g filter="url(#sh)"><circle cx="1010" cy="120" r="56" fill="url(#panel)" stroke="#34343C" stroke-width="2"/><circle cx="1010" cy="120" r="42" fill="none" stroke="#2E2E35" stroke-width="6"/><path d="M1010 78 A42 42 0 0 1 1050 132" fill="none" stroke="{Y}" stroke-width="6" stroke-linecap="round"/><path d="M1010 96 V120 L1026 130" fill="none" stroke="{WH}" stroke-width="4" stroke-linecap="round"/></g>
''', (650, 200))

# ---------- Digital Marketing: audience -> content -> funnel -> metric ----------
fun = ""
for i in range(4):
    w = 300 - i * 62; x = 560 - w / 2; y = 70 + i * 66
    fun += f'<path d="M{x} {y} H{x+w} L{x+w-31} {y+56} H{x+31}Z" fill="{"url(#gy)" if i%2==0 else Y2}" opacity="{1-i*.08:.2f}"/>'
    fun += line(x + 40, y + 24, w - 80 - 30, 8, K)
ART["digital-marketing"] = base(f'''
<g filter="url(#sh)">{panel(110, 60, 220, 290, 18)}<rect x="126" y="76" width="188" height="150" rx="10" fill="#2B2B32"/>
<circle cx="220" cy="150" r="40" fill="url(#gy)"/><path d="M210 132 L238 150 L210 168Z" fill="{K}"/>
{line(130,244,150,8,WH)}{line(130,262,110,7,"#55555E")}<rect x="130" y="290" width="100" height="34" rx="9" fill="url(#gy)"/>{line(146,303,68,8,K)}
<g transform="translate(250 290)">{icon('<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21.2l8.8-8.8a5.5 5.5 0 0 0 0-7.8z"/>', 0, 4, 1.15, "#FF6B5B")}</g></g>
{fun}
<path d="M345 205 H395" stroke="{WH}" stroke-width="3" stroke-dasharray="3 8" stroke-linecap="round" opacity=".7"/>
<path d="M725 205 H780" stroke="{WH}" stroke-width="3" stroke-dasharray="3 8" stroke-linecap="round" opacity=".7"/>
<g filter="url(#sh)">{panel(795, 70, 290, 270, 18)}{line(820,96,110,9,WH)}
<path d="M820 300 L870 270 L920 280 L970 220 L1020 200 L1060 140" fill="none" stroke="{Y}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#gw)"/>
<path d="M820 300 L870 270 L920 280 L970 220 L1020 200 L1060 140 V316 H820Z" fill="{Y}" opacity=".12"/>
{icon('<path d="M3 11v2a1 1 0 0 0 1 1h3l6 4V6L7 10H4a1 1 0 0 0-1 1z"/><path d="M17 8a5 5 0 0 1 0 8M19.5 5.5a8.5 8.5 0 0 1 0 13"/>', 1030, 88, 1.3, Y)}</g>
''', (560, 200))

# ---------- Networking & IT: topology with packets ----------
dev = {"r": (590, 110), "s1": (380, 230), "s2": (800, 230), "srv": (590, 330),
       "p1": (200, 140), "p2": (180, 320), "p3": (1000, 130), "p4": (1010, 320)}
links = [("r", "s1"), ("r", "s2"), ("s1", "srv"), ("s2", "srv"), ("s1", "p1"), ("s1", "p2"), ("s2", "p3"), ("s2", "p4")]
NL = "".join(f'<line x1="{dev[a][0]}" y1="{dev[a][1]}" x2="{dev[b][0]}" y2="{dev[b][1]}" stroke="#3A3A42" stroke-width="3"/>' for a, b in links)
pk = ""
for a, b, t in [("r", "s1", .4), ("s2", "p3", .55), ("s1", "srv", .6), ("r", "s2", .7), ("s1", "p2", .35)]:
    (x1, y1), (x2, y2) = dev[a], dev[b]
    pk += f'<circle cx="{x1+(x2-x1)*t:.0f}" cy="{y1+(y2-y1)*t:.0f}" r="7" fill="{Y}" filter="url(#gw)"/>'
def box(k, w, h, fill, ic, icc):
    x, y = dev[k]
    return f'<g filter="url(#sh)"><rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="#34343C" stroke-width="1.5"/></g>' + icon(ic, x - 14, y - 14, 1.17, icc)
router = '<rect x="2" y="13" width="20" height="8" rx="2"/><path d="M6 17h.01M10 17h.01M15 9a5 5 0 0 0-6 0M18 6a9 9 0 0 0-12 0"/>'
switch = '<rect x="2" y="7" width="20" height="10" rx="2"/><path d="M6 12h.01M10 12h.01M14 12h.01M18 12h.01"/>'
server = '<rect x="3" y="3" width="18" height="7" rx="2"/><rect x="3" y="14" width="18" height="7" rx="2"/><path d="M7 6.5h.01M7 17.5h.01"/>'
pc = '<rect x="2" y="4" width="20" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>'
ART["networks"] = base(f'''
{NL}{pk}
<circle cx="590" cy="110" r="60" fill="none" stroke="{Y}" stroke-opacity=".25" stroke-width="2" stroke-dasharray="3 7"/>
{box("r", 96, 64, "url(#gy)", router, K)}{box("s1", 110, 56, "url(#panel)", switch, Y)}{box("s2", 110, 56, "url(#panel)", switch, Y)}
{box("srv", 110, 62, "url(#panel)", server, WH)}
{box("p1", 80, 60, "url(#panel)", pc, WH)}{box("p2", 80, 60, "url(#panel)", pc, WH)}{box("p3", 80, 60, "url(#panel)", pc, WH)}{box("p4", 80, 60, "url(#panel)", pc, WH)}
''', (590, 200))

# ---------- Infection Control: hand hygiene, protection, monitoring ----------
chk = "".join(f'<rect x="842" y="{96+i*52}" width="210" height="40" rx="10" fill="#1A1A1F" stroke="#2E2E35"/><circle cx="864" cy="{116+i*52}" r="11" fill="{"#4FBF8B" if i<3 else "none"}" stroke="#4FBF8B" stroke-width="2.5"/>{"<path d=\"M858 %d l4 4 8-8\" fill=\"none\" stroke=\"#0B0B0B\" stroke-width=\"2.5\" stroke-linecap=\"round\"/>" % (116+i*52) if i<3 else ""}{line(886,112+i*52,[120,96,130,104][i],8,WH if i<3 else "#66666F")}' for i in range(4))
drops = "".join(f'<path d="M{x} {y} c-7 10 -11 16 -11 22 a11 11 0 0 0 22 0 c0 -6 -4 -12 -11 -22z" fill="{c}" opacity="{o}"/>' for x, y, c, o in [(470, 70, "#5B9BE6", .9), (520, 40, "#5B9BE6", .6), (700, 60, "#5B9BE6", .75)])
ART["infection-control"] = base(f'''
<circle cx="590" cy="210" r="150" fill="none" stroke="#4FBF8B" stroke-opacity=".14" stroke-width="2"/><circle cx="590" cy="210" r="118" fill="none" stroke="{Y}" stroke-opacity=".22" stroke-width="2" stroke-dasharray="3 8"/>
<g filter="url(#gw)"><path d="M590 88 L676 120 V200 C676 258 638 302 590 322 C542 302 504 258 504 200 V120Z" fill="url(#gy)"/></g>
<g transform="translate(546 150) scale(3.6)" fill="none" stroke="{K}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M18 11V6a2 2 0 0 0-4 0v5"/><path d="M14 10V4a2 2 0 0 0-4 0v6"/><path d="M10 10.5V6a2 2 0 0 0-4 0v8"/><path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.96-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/></g>
{drops}
<g filter="url(#sh)">{panel(820, 72, 254, 248, 18)}</g>{chk}
<g filter="url(#sh)">{panel(110, 90, 250, 220, 18)}</g>
<g transform="translate(150 120)">{"".join(f'<g transform="translate({(i%2)*92} {(i//2)*86})"><rect width="76" height="70" rx="14" fill="#1A1A1F" stroke="#2E2E35"/>' + icon(p, 22, 17, 1.35, c) + '</g>' for i,(p,c) in enumerate([('<path d="M12 2l8 3v6c0 5-3.5 9-8 11-4.5-2-8-6-8-11V5z"/>', Y), ('<path d="M9 2v6l-5 9a3 3 0 0 0 2.6 4.5h10.8A3 3 0 0 0 20 17l-5-9V2M8 2h8M7 14h10"/>', "#5B9BE6"), ('<path d="M3 6h18M8 6V4h8v2M6 6l1 15h10l1-15"/>', WH), ('<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>', "#4FBF8B")]))}</g>
''', (590, 210), "#4FBF8B")

if __name__ == "__main__":
    for k, v in ART.items():
        open(f"{k}.svg", "w").write(v)
        print(k, len(v))
