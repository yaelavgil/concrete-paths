# -*- coding: utf-8 -*-
"""אשל 57 — מחולל גיליונות תוכנית החצר.
מסגרת קואורדינטות: X מזרחה, Y צפונה, ס״מ, ראשית = פינת המגרש הדרום־מערבית.
מקורות: גרמושקה 2.1.24 (מפה מצבית 1:250 + קומת קרקע 1:100) · העמדה קומת קרקע 21.08.26 (נופר צבר צבי).
python3 tools/sheets.py  ->  sheet1.svg, sheet2.svg, preview1.html, preview2.html
"""
import math, re, random

# ---------------------------------------------------------------- geometry (cm)
PLOT_W, PLOT_L = 1670, 2700                 # PRINTED (survey) 16.70 x 27.00
FENCE_IN = 13
HX_W, HX_SW, HX_E = 300.0, 470.1, 1240.6    # north-wing west face / south-wing west face / east face
HY_S, HY_N, HY_DOOR = 483.0, 1993.9, 1203.5
WALL = 20.0
STUB_Y = 400.0                              # PRINTED 400
COL = (300.0, 933.2, 320.0, 993.4)          # existing column
DOOR = (345.4, 445.4)
WIN_BR2 = (853.2, 933.2)
GATE_P = (115.0, 130.0, 231.0, 246.0)
CAR_GATE = (1190.0, 1670.0)
# design
SP0, SP1 = 103.0, 253.0
AX = 178.0
R = [279.0, 447.0, 615.0, 783.0]            # R4 = column south face - 150
ARM = (253.0, 285.0, 1190.0, 400.0)
MANHOLE_SW = (201.0, 247.0)
G_LVL, S, RISE = 49.08, 22.0/770.0, 0.16

def lv_path():
    pts = [(FENCE_IN, G_LVL)]
    z = G_LVL + S*(R[0]-FENCE_IN)/100; pts.append((R[0], z))
    for i in range(3):
        z += RISE; pts.append((R[i], z))
        z += S*(R[i+1]-R[i])/100; pts.append((R[i+1], z))
    z += RISE; pts.append((R[3], z))
    return pts
LV = lv_path()
def z_land(Y): return 50.00 - 0.015*(HY_DOOR - Y)/100

SURVEY = [
    ((0,0),'49.06',1),((PLOT_W,0),'49.41',1),((0,PLOT_L),'49.68',1),((PLOT_W,PLOT_L),'49.63',1),
    ((376,202),'49.14',0),((206,471),'49.34',0),((47,524),'49.22',0),((196,725),'49.30',0),
    ((217,940),'49.87',0),((237,1108),'49.95',0),((38,1031),'49.61',0),((560,416),'49.24',0),
    ((1261,484),'49.54',0),((1331,1325),'49.82',0),((1344,1645),'49.83',0),((1529,1879),'49.73',0),
    ((105,-63),'49.01',0),((317,-46),'49.10',0),((1011,-106),'49.15',0),((1161,-48),'49.23',0),
]
MANHOLES = [((201,247),'T.L 49.18'),((1431,281),'T.L 49.41'),((1451,1094),'T.L 49.77')]
HEB = re.compile('[֐-׿]')
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ---------------------------------------------------------------- kernel
class Sheet:
    def __init__(s, pfx, T): s.p, s.T, s.o = pfx, T, []
    def P(s, X, Y): return s.T(X, Y)
    def add(s, x): s.o.append(x)
    def pts(s, L): return ' '.join('%.1f,%.1f' % s.P(*q) for q in L)
    def poly(s, L, cls, extra=''): s.add('<polygon class="%s" points="%s" %s/>' % (cls, s.pts(L), extra))
    def pline(s, L, cls, extra=''): s.add('<polyline class="%s" points="%s" %s/>' % (cls, s.pts(L), extra))
    def rect(s, x0, y0, x1, y1, cls, extra=''): s.poly([(x0,y0),(x1,y0),(x1,y1),(x0,y1)], cls, extra)
    def line(s, a, b, cls): s.pline([a, b], cls)
    def circ(s, c, r, cls):
        x, y = s.P(*c); s.add('<circle class="%s" cx="%.1f" cy="%.1f" r="%.1f"/>' % (cls, x, y, r))
    def raw_text(s, x, y, t, cls, ang=0, anchor='middle'):
        d = ' direction="rtl"' if HEB.search(t) else ''
        tr = ' transform="rotate(%.1f %.1f %.1f)"' % (ang, x, y) if ang else ''
        s.add('<text class="%s" x="%.1f" y="%.1f" text-anchor="%s"%s%s>%s</text>' % (cls, x, y, anchor, d, tr, esc(t)))
    def text(s, X, Y, t, cls, ang=0, anchor='middle', dx=0, dy=0):
        x, y = s.P(X, Y); s.raw_text(x+dx, y+dy, t, cls, ang, anchor)
    def dim(s, a, b, off, t, cls='k-dim', tcls='k-dt', ext=True, gap=6):
        A = s.P(a[0]+off[0], a[1]+off[1]); B = s.P(b[0]+off[0], b[1]+off[1])
        a0, b0 = s.P(*a), s.P(*b)
        if ext:
            for p, q in ((a0, A), (b0, B)):
                vx, vy = q[0]-p[0], q[1]-p[1]; L = math.hypot(vx, vy) or 1
                ux, uy = vx/L, vy/L
                s.add('<line class="k-ext" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (p[0]+ux*gap, p[1]+uy*gap, q[0]+ux*gap*1.4, q[1]+uy*gap*1.4))
        s.add('<line class="%s" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (cls, A[0], A[1], B[0], B[1]))
        ang = math.degrees(math.atan2(B[1]-A[1], B[0]-A[0]))
        for p in (A, B):
            r = math.radians(ang+45); k = s.tick
            s.add('<line class="k-tick" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (p[0]-k*math.cos(r), p[1]-k*math.sin(r), p[0]+k*math.cos(r), p[1]+k*math.sin(r)))
        if ang > 90.1 or ang < -89.9: ang += 180
        mx, my = (A[0]+B[0])/2, (A[1]+B[1])/2
        n = math.radians(ang-90)
        s.raw_text(mx+math.cos(n)*s.tick*1.1, my+math.sin(n)*s.tick*1.1, t, tcls, ang)
    def svg(s, w, h, title, defs, style):
        return ('<svg class="%s" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img" aria-label="%s">'
                '<style>%s</style><defs>%s</defs>%s</svg>') % (s.p, w, h, esc(title), style, defs, '\n'.join(s.o))

def style(root, k):
    c = {'ink':'#2b2824','house':'#d8d1c6','hl':'#5f584e','conc':'#d3c9b8','acc':'#8a5a2b','sv':'#6a635a','sew':'#2f6690','red':'#b3382c'}
    return ('.{r}{{background:#fff}} .{r} text{{font-family:"Heebo","Assistant","Arial Hebrew",Arial,sans-serif;fill:{ink}}}'
    ' .{r} .k-paper{{fill:#fff;stroke:none}} .{r} .k-frame{{fill:none;stroke:{ink};stroke-width:{a}}}'
    ' .{r} .k-plot{{fill:none;stroke:{ink};stroke-width:{c};stroke-dasharray:{d1} {d2} {d3} {d2}}}'
    ' .{r} .k-fence{{fill:#8c857a;stroke:{ink};stroke-width:{t}}}'
    ' .{r} .k-house{{fill:{house};stroke:none}} .{r} .k-wall{{fill:url(#{r}-hatch);stroke:{hl};stroke-width:{m}}}'
    ' .{r} .k-open{{fill:#fff;stroke:none}} .{r} .k-hl{{fill:none;stroke:{hl};stroke-width:{t}}}'
    ' .{r} .k-conc{{fill:url(#{r}-conc);stroke:{ink};stroke-width:{m}}} .{r} .k-concS{{fill:url(#{r}-concS);stroke:{ink};stroke-width:{m}}}'
    ' .{r} .k-undec{{fill:url(#{r}-undec);stroke:{hl};stroke-width:{t}}} .{r} .k-plant{{fill:url(#{r}-plant);stroke:{hl};stroke-width:{t}}}'
    ' .{r} .k-lawn{{fill:url(#{r}-lawn);stroke:none}} .{r} .k-stone{{fill:#c9c0b0;stroke:{hl};stroke-width:{t}}}'
    ' .{r} .k-nose{{stroke:{acc};stroke-width:{n};fill:none;stroke-linecap:butt}}'
    ' .{r} .k-roof{{fill:none;stroke:{ink};stroke-width:{t};stroke-dasharray:{d1} {d2}}}'
    ' .{r} .k-demo{{fill:none;stroke:{red};stroke-width:{t};stroke-dasharray:{d2} {d2}}}'
    ' .{r} .k-sew{{fill:none;stroke:{sew};stroke-width:{t};stroke-dasharray:{d1} {d2} {d3} {d2}}} .{r} .k-mh{{fill:#fff;stroke:{sew};stroke-width:{m}}}'
    ' .{r} .k-col{{fill:{ink};stroke:none}} .{r} .k-thin{{fill:none;stroke:{hl};stroke-width:{t}}} .{r} .k-med{{fill:none;stroke:{ink};stroke-width:{m}}}'
    ' .{r} .k-dim,.{r} .k-ext{{stroke:{ink};stroke-width:{t};fill:none}} .{r} .k-ext{{stroke:{sv}}} .{r} .k-tick{{stroke:{ink};stroke-width:{m}}}'
    ' .{r} .k-dt{{font-size:{fs}px;font-weight:500}}'
    ' .{r} .k-lab{{font-size:{fl}px;font-weight:600}} .{r} .k-labs{{font-size:{fs}px;fill:{sv}}} .{r} .k-labb{{font-size:{fb}px;font-weight:800}}'
    ' .{r} .k-lvl{{font-size:{fs}px;font-weight:700;fill:{acc}}} .{r} .k-lvlbox{{fill:#fff;stroke:{acc};stroke-width:{t}}}'
    ' .{r} .k-sv{{font-size:{fss}px;fill:{sv};font-style:italic}} .{r} .k-svx{{stroke:{sv};stroke-width:{t}}}'
    ' .{r} .k-acc{{fill:{acc}}} .{r} .k-sewt{{fill:{sew};font-size:{fss}px}}'
    ' .{r} .k-cut{{stroke:{ink};stroke-width:{m};stroke-dasharray:{d1} {d2} {d3} {d2};fill:none}} .{r} .k-cutT{{font-size:{fb}px;font-weight:800}}'
    ' .{r} .k-arrow{{stroke:{acc};stroke-width:{m};fill:none}} .{r} .k-fall{{stroke:{ink};stroke-width:{t};fill:none}}'
    ' .{r} .k-tb{{fill:#fff;stroke:{ink};stroke-width:{m}}} .{r} .k-tbl{{stroke:{ink};stroke-width:{t}}}'
    ' .{r} .k-soil{{fill:url(#{r}-soil);stroke:none}} .{r} .k-fill{{fill:url(#{r}-fill);stroke:none}}'
    ' .{r} .k-gnd{{fill:none;stroke:{sv};stroke-width:{m};stroke-dasharray:{d2} {d3}}} .{r} .k-bg{{fill:#efebe4;stroke:{hl};stroke-width:{t}}}'
    ' .{r} .k-h2{{font-size:{fh2}px;font-weight:800}} .{r} .k-note2{{font-size:{fn2}px}} .{r} .k-note{{font-size:{fs}px}} .{r} .k-h{{font-size:{fl}px;font-weight:800}}'
    ).format(r=root, a=6*k, c=2.2*k, d1=24*k, d2=7*k, d3=3*k, t=1.1*k, m=2.2*k, n=6*k,
             fn2=round(17*k), fh2=round(20*k), fs=round(21*k), fss=round(18*k), fl=round(25*k), fb=round(34*k), **c)

def defs(r, k):
    return ('<pattern id="{r}-hatch" width="{h}" height="{h}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="{h}" height="{h}" fill="#e6e0d6"/><line x1="0" y1="0" x2="0" y2="{h}" stroke="#5f584e" stroke-width="{t}"/></pattern>'
     '<pattern id="{r}-conc" width="{c}" height="{c}" patternUnits="userSpaceOnUse"><rect width="{c}" height="{c}" fill="#d3c9b8"/><circle cx="{c1}" cy="{c2}" r="{d}" fill="#8f8574"/><circle cx="{c3}" cy="{c4}" r="{d}" fill="#8f8574"/><path d="M{t1},{t2} l{u},0 l-{hu},-{u} z" fill="#a39884"/></pattern>'
     '<pattern id="{r}-concS" width="{c}" height="{c}" patternUnits="userSpaceOnUse"><rect width="{c}" height="{c}" fill="#e3dccf"/><circle cx="{c1}" cy="{c2}" r="{d}" fill="#a39884"/><circle cx="{c3}" cy="{c4}" r="{d}" fill="#a39884"/></pattern>'
     '<pattern id="{r}-undec" width="{g}" height="{g}" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="{g}" height="{g}" fill="#f4f0e9"/><line x1="0" y1="{hg}" x2="{g}" y2="{hg}" stroke="#b6ab99" stroke-width="{t}" stroke-dasharray="{dd} {dd}"/></pattern>'
     '<pattern id="{r}-plant" width="{p}" height="{p}" patternUnits="userSpaceOnUse"><rect width="{p}" height="{p}" fill="#e3ecd8"/><circle cx="{p1}" cy="{p1}" r="{pr}" fill="none" stroke="#7d9a5d" stroke-width="{t}"/><circle cx="{p2}" cy="{p3}" r="{pr2}" fill="none" stroke="#7d9a5d" stroke-width="{t}"/></pattern>'
     '<pattern id="{r}-lawn" width="{l}" height="{l}" patternUnits="userSpaceOnUse"><rect width="{l}" height="{l}" fill="#edf3e3"/><path d="M{l1},{l2} l{lw},-{lh} M{l3},{l4} l{lw},-{lh}" stroke="#94ad74" stroke-width="{t}"/></pattern>'
     '<pattern id="{r}-soil" width="{s}" height="{s}" patternUnits="userSpaceOnUse"><rect width="{s}" height="{s}" fill="#efe7da"/><circle cx="{s1}" cy="{s1}" r="{d}" fill="#a8998a"/></pattern>'
     '<pattern id="{r}-fill" width="{s}" height="{s}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="{s}" height="{s}" fill="#f1ece3"/><line x1="0" y1="0" x2="0" y2="{s}" stroke="#c7bba8" stroke-width="{t}"/></pattern>'
     '<marker id="{r}-ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{mk}" markerHeight="{mk}" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" fill="#2b2824"/></marker>'
     '<marker id="{r}-aha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{mk}" markerHeight="{mk}" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,0 L10,5 L0,10 z" fill="#8a5a2b"/></marker>'
    ).format(r=r, h=9*k, t=0.9*k, c=26*k, c1=5*k, c2=7*k, c3=17*k, c4=19*k, d=1.3*k, t1=13*k, t2=13*k, u=4*k, hu=2*k,
             g=16*k, hg=8*k, dd=5*k, p=46*k, p1=14*k, pr=8*k, p2=34*k, p3=33*k, pr2=6*k, l=22*k, l1=4*k, l2=12*k, l3=14*k, l4=20*k, lw=3*k, lh=7*k,
             s=10*k, s1=5*k, mk=16*k)

def lvl(sh, X, Y, t, k=1.0):
    x, y = sh.P(X, Y); a = 7*k
    sh.add('<path d="M%.1f,%.1f l%.1f,%.1f l%.1f,0 z" class="k-acc"/>' % (x, y, -a, -a*1.5, 2*a))
    w = 72*k; hh = 26*k; bx = x - w/2; by = y - a*1.5 - hh - 2*k
    sh.add('<rect class="k-lvlbox" x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f"/>' % (bx, by, w, hh, 3*k))
    sh.raw_text(bx+w/2, by+hh*0.76, t, 'k-lvl')

def svlvl(sh, X, Y, t, k=1.0, dx=0, dy=0):
    x, y = sh.P(X, Y); a = 5*k
    sh.add('<path class="k-svx" d="M%.1f,%.1f l%.1f,%.1f M%.1f,%.1f l%.1f,%.1f"/>' % (x-a, y-a, 2*a, 2*a, x-a, y+a, 2*a, -2*a))
    sh.raw_text(x+dx, y-8*k+dy, t, 'k-sv')

def plants(sh, x0, y0, x1, y1, n, seed, rmin, rmax):
    rnd = random.Random(seed)
    for _ in range(n):
        X = rnd.uniform(x0+rmax, x1-rmax); Y = rnd.uniform(y0+rmax, y1-rmax); r = rnd.uniform(rmin, rmax)
        x, y = sh.P(X, Y)
        sh.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#dfe9d2" stroke="#6f8c51" stroke-width="%.1f"/>' % (x, y, r, sh.k*1.0))
        sh.add('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#6f8c51"/>' % (x, y, sh.k*1.6))

def house_parts(sh):
    outline = [(HX_W, HY_N), (HX_E, HY_N), (HX_E, HY_S), (HX_SW, HY_S), (HX_SW, HY_DOOR), (HX_W, HY_DOOR)]
    sh.poly(outline, 'k-house')
    W = WALL
    sh.rect(HX_W, HY_DOOR, HX_W+W, HY_N, 'k-wall')
    sh.rect(HX_W, HY_N-W, HX_E, HY_N, 'k-wall')
    sh.rect(HX_E-W, HY_S, HX_E, HY_N, 'k-wall')
    sh.rect(HX_SW, HY_S, HX_E, HY_S+W, 'k-wall')
    sh.rect(HX_SW, HY_S, HX_SW+W, HY_DOOR+W, 'k-wall')
    sh.rect(HX_W, HY_DOOR, HX_SW+W, HY_DOOR+W, 'k-wall')
    sh.rect(HX_SW, STUB_Y, HX_SW+W, HY_S, 'k-wall')
    sh.rect(HX_E-W, STUB_Y, HX_E, HY_S, 'k-wall')
    sh.rect(DOOR[0], HY_DOOR-1, DOOR[1], HY_DOOR+W+1, 'k-open')
    sh.rect(HX_SW-1, WIN_BR2[0], HX_SW+W+1, WIN_BR2[1], 'k-open')
    sh.line((HX_SW+W/2, WIN_BR2[0]), (HX_SW+W/2, WIN_BR2[1]), 'k-hl')
    sh.line((HX_SW, WIN_BR2[0]), (HX_SW, WIN_BR2[1]), 'k-hl'); sh.line((HX_SW+W, WIN_BR2[0]), (HX_SW+W, WIN_BR2[1]), 'k-hl')
    for y0, y1 in ((1400.1, 1480.1), (1813.1, 1933.1)):
        sh.rect(HX_W-1, y0, HX_W+W+1, y1, 'k-open'); sh.line((HX_W+W/2, y0), (HX_W+W/2, y1), 'k-hl')
        sh.line((HX_W, y0), (HX_W, y1), 'k-hl'); sh.line((HX_W+W, y0), (HX_W+W, y1), 'k-hl')
    for x0, x1 in ((830.0, 902.0), (1085.0, 1215.0)):
        sh.rect(x0, HY_S-1, x1, HY_S+W+1, 'k-open'); sh.line((x0, HY_S+W/2), (x1, HY_S+W/2), 'k-hl')
        sh.line((x0, HY_S), (x1, HY_S), 'k-hl'); sh.line((x0, HY_S+W), (x1, HY_S+W), 'k-hl')
    sh.rect(HX_E-W-1, 1176.0, HX_E+1, 1245.0, 'k-open')
    hx, hy = DOOR[0], HY_DOOR+W
    sh.line((hx, hy), (hx, hy+100), 'k-med')
    a0 = sh.P(hx, hy+100); a1 = sh.P(DOOR[1], hy)
    rr = abs(sh.P(hx, hy)[0]-sh.P(hx+100, hy)[0]) + abs(sh.P(hx, hy)[1]-sh.P(hx+100, hy)[1])
    sh.add('<path class="k-thin" d="M%.1f,%.1f A%.1f,%.1f 0 0 %d %.1f,%.1f"/>' % (a0[0], a0[1], rr, rr, sh.sweep, a1[0], a1[1]))
    sh.rect(COL[0], COL[1], COL[2], COL[3], 'k-col')
    sh.rect(HX_W, COL[1], HX_SW, HY_DOOR, 'k-roof')

def title_block(sh, x, y, w, h, t1, t2, fs):
    sh.add('<rect class="k-tb" x="%d" y="%d" width="%d" height="%d"/>' % (x, y, w, h))
    r = x + w - fs
    rows = [(t1, 1.35, 800, '#2b2824'), (t2, 0.95, 400, '#6a635a'), None,
            ('אשל 57, בת חפר · גוש 8729 חלקה 41', 1, 400, '#2b2824'),
            ('מזמינים: יעל ורועי אבגיל', 1, 400, '#2b2824'),
            ('לתיאום: גל (אותנטיק בטון) · נופר צבר צבי', 1, 400, '#2b2824'),
            ('גרסה ג׳ · 18.09.2026', 1, 700, '#2b2824'),
            ('לתיאום — לא לביצוע לפני מדידת בקרה', 1, 700, '#b3382c'),
            ('הוכן ע״י Claude (AI) עבור יעל · אינה תוכנית חתומה', 0.85, 400, '#6a635a')]
    yy = y + fs*1.9
    for row in rows:
        if row is None:
            sh.add('<line class="k-tbl" x1="%d" y1="%.1f" x2="%d" y2="%.1f"/>' % (x, yy-fs*0.55, x+w, yy-fs*0.55)); yy += fs*0.6; continue
        t, sc, wt, col = row
        sh.add('<text x="%.1f" y="%.1f" text-anchor="start" direction="rtl" style="font-size:%.1fpx;font-weight:%d;fill:%s">%s</text>' % (r, yy, fs*sc, wt, col, esc(t)))
        yy += fs*sc*1.45

def arrow(sh, pts, cls='k-arrow', mk='cpS2-aha', dash=''):
    P = [sh.P(*p) for p in pts]
    sh.add('<polyline class="%s" points="%s" %s marker-end="url(#%s)"/>' % (cls, ' '.join('%.1f,%.1f' % q for q in P), ('stroke-dasharray="%s"' % dash) if dash else '', mk))

# ================================================================ SHEET 1 — site plan 1:100 (A3 portrait)
def sheet1():
    k = 1.9
    OX, OY = 330, 3280
    sh = Sheet('cpS1', lambda X, Y: (OX+X, OY-Y)); sh.k = k; sh.tick = 12*k; sh.sweep = 1
    W, H = 2970, 4200
    sh.add('<rect class="k-paper" x="0" y="0" width="%d" height="%d"/>' % (W, H))
    sh.add('<rect class="k-frame" x="40" y="40" width="%d" height="%d"/>' % (W-80, H-80))
    sh.rect(13, 13, PLOT_W-13, PLOT_L-13, 'k-lawn')
    sh.rect(13, 13, CAR_GATE[0], 285, 'k-undec')
    sh.rect(ARM[0], ARM[1], ARM[2], ARM[3], 'k-undec')
    sh.rect(HX_SW+WALL, STUB_Y, HX_E-WALL, HY_S, 'k-plant')
    sh.rect(SP1, STUB_Y, HX_SW, R[3], 'k-plant')
    sh.rect(13, 13, SP0, HY_N, 'k-plant')
    sh.rect(SP0, COL[1], HX_W, HY_N, 'k-plant')
    sh.rect(CAR_GATE[0], 13, PLOT_W-13, STUB_Y, 'k-concS')
    sh.rect(HX_E, STUB_Y, PLOT_W-13, HY_N-100, 'k-concS')
    sh.rect(SP0, 13, SP1, R[0], 'k-undec')
    for i in range(3): sh.rect(SP0, R[i], SP1, R[i+1], 'k-conc')
    sh.poly([(SP0, R[3]), (HX_SW, R[3]), (HX_SW, HY_DOOR), (HX_W, HY_DOOR), (HX_W, COL[3]), (COL[2], COL[3]), (COL[2], COL[1]), (SP0, COL[1])], 'k-conc')
    for y in R: sh.line((SP0, y), (SP1 if y < R[3] else HX_SW, y), 'k-nose')
    for j in range(14):
        y = 965 + j*65
        if y+45 > HY_N+300: break
        sh.rect(AX-45, y, AX+45, y+45, 'k-stone')
    house_parts(sh)
    sh.rect(-4, -4, PLOT_W+4, 13, 'k-fence')
    sh.rect(GATE_P[1], -6, GATE_P[2], 15, 'k-open'); sh.rect(CAR_GATE[0], -6, CAR_GATE[1]-4, 15, 'k-open')
    sh.line((CAR_GATE[0], 20), (CAR_GATE[1]-4, 20), 'k-thin')
    sh.add('<polygon class="k-plot" fill="none" points="%s"/>' % sh.pts([(0,0),(0,PLOT_L),(PLOT_W,PLOT_L),(PLOT_W,0)]))
    for c in ((0,0),(PLOT_W,0),(0,PLOT_L),(PLOT_W,PLOT_L)): sh.circ(c, 11*k, 'k-med')
    sh.pline([(1451,1094),(1431,281),(201,247),(-108,-394)], 'k-sew')
    for c, t in MANHOLES: sh.circ(c, 30, 'k-mh')
    for y in (803, 835, 868, 901): sh.line((120, y), (301, y), 'k-demo')
    sh.text(835, 1250, 'בית קיים', 'k-labb'); sh.text(835, 1195, 'לפי העמדה 21.08.26', 'k-labs')
    sh.text(835, 1140, '±0.00 = +50.03', 'k-lab')
    sh.text(620, 150, 'חזית — משטח טרם הוחלט', 'k-lab'); sh.text(620, 100, 'אבני מדרך / דשא סינתטי', 'k-labs')
    sh.text(720, 330, 'זרוע מהחנייה ←', 'k-labs')
    sh.text(1430, 205, 'חנייה', 'k-lab'); sh.text(1430, 160, 'בטון — מחוץ לגיליון', 'k-labs')
    sh.text(1455, 1500, 'רצועה מזרחית', 'k-lab', -90); sh.text(1510, 1500, 'בטון — עד 1 מ׳ לפני סוף הבית', 'k-labs', -90)
    sh.text(835, 2350, 'גינה אחורית', 'k-labb'); sh.text(835, 2295, 'דשא · שטח שמור לבריכה אפשרית', 'k-labs')
    sh.text(200, 1600, 'אבני מדרך אל הגינה', 'k-labs', -90)
    sh.text(58, 700, 'ערוגה', 'k-labs', -90)
    sh.text(362, 560, 'ערוגה', 'k-labs', -90)
    sh.text(178, -170, 'פשפש', 'k-lab'); sh.text(1430, -170, 'שער נגרר לרכב', 'k-lab')
    sh.text(835, -330, 'רחוב אלה — מדרכה', 'k-labs')
    sh.text(1262, 1195, 'דלת חוץ שנייה', 'k-labs', 0, 'end')
    sh.text(500, 1000, '← גגון + עמוד קיים', 'k-labs', 0, 'end')
    sh.text(1540, 960, 'ביוב קיים', 'k-sewt')
    for (X, Y), t, corner in SURVEY:
        if Y < -20: continue
        svlvl(sh, X, Y, t, k*0.9, dx=(0 if not corner else (60 if X == 0 else -60)), dy=(-20 if corner and Y > 0 else (40 if corner else 0)))
    lvl(sh, AX, 70, '49.08', k=k*0.9)
    lvl(sh, AX, 800, '49.94', k=k*0.9)
    lvl(sh, 395, 1180, '50.00', k=k*0.9)
    sh.rect(-40, -95, 560, 1330, 'k-roof')
    sh.text(-85, 620, 'גיליון 2 — פרט כניסה 1:50', 'k-lab', -90)
    sh.line((AX, -250), (AX, -110), 'k-cut'); sh.line((AX, 1340), (AX, 1420), 'k-cut')
    sh.text(AX+55, -250, 'א', 'k-cutT'); sh.text(AX+55, 1400, 'א', 'k-cutT')
    sh.dim((0, PLOT_L), (PLOT_W, PLOT_L), (0, 150), '1670 ★')
    sh.dim((0, 0), (0, PLOT_L), (-230, 0), '2700 ★')
    sh.dim((0, HY_N-40), (HX_W, HY_N-40), (0, 0), '300 ★', ext=False)
    sh.dim((HX_E, 700), (PLOT_W, 700), (0, 0), '≈430 ?', ext=False)
    sh.dim((HX_SW, HY_S-230), (HX_E, HY_S-230), (0, 0), '770 ★', ext=False)
    sh.dim((1120, 0), (1120, HY_S), (0, 0), '483 ★', ext=False)
    sh.dim((1010, 0), (1010, STUB_Y), (0, 0), '400 ★', ext=False)
    sh.dim((HX_W, HY_N), (HX_W, PLOT_L), (-120, 0), '≈706', ext=False)
    ch = [0, GATE_P[0], GATE_P[3], CAR_GATE[0], PLOT_W]
    tx = ['115', '130 ★', '943 ★ / 880 ★ ⚠', '480 ★']
    for i in range(4): sh.dim((ch[i], 0), (ch[i+1], 0), (0, -120), tx[i])
    nx, ny = 2380, 3350
    sh.add('<g transform="translate(%d %d) rotate(-15.6)"><circle r="95" fill="none" stroke="#2b2824" stroke-width="3"/><path d="M0,-120 L34,70 L0,40 L-34,70 Z" fill="#2b2824"/></g>' % (nx, ny))
    sh.raw_text(nx-42, ny-150, 'צ', 'k-cutT')
    sh.raw_text(nx, ny+150, 'צפון אמיתי מוטה ≈16°', 'k-labs')
    sx0, sy0 = 2040, 3560
    for i in range(5):
        sh.add('<rect x="%d" y="%d" width="100" height="18" fill="%s" stroke="#2b2824" stroke-width="2"/>' % (sx0+i*100, sy0, '#2b2824' if i % 2 == 0 else '#fff'))
    for i, t in enumerate(['0', '1', '2', '3', '4', '5 מ׳']): sh.raw_text(sx0+i*100, sy0+55, t, 'k-labs')
    sh.raw_text(sx0+250, sy0-25, 'קנ״מ 1:100 בהדפסת A3', 'k-labs')
    lx, ly = 2880, 330
    sh.raw_text(lx, ly, 'מקרא', 'k-h', 0, 'start')
    items = [('k-conc', 'בטון מוחלק — אותנטיק (בגיליון זה)'), ('k-concS', 'בטון — חנייה ורצועה מזרחית'),
             ('k-undec', 'משטח חזית — טרם הוחלט'), ('k-stone', 'אבני מדרך'), ('k-plant', 'ערוגה / שתילה'), ('k-lawn', 'דשא'),
             ('k-wall', 'קיר קיים (העמדה 21.08.26)')]
    for i, (c, t) in enumerate(items):
        y = ly + 60 + i*62
        sh.add('<rect class="%s" x="%d" y="%d" width="80" height="40"/>' % (c, lx-80, y-30))
        sh.raw_text(lx-100, y, t, 'k-note2', 0, 'start')
    y = ly + 60 + len(items)*62
    lines = [('k-nose', 'אף מדרגה (רום 16)'), ('k-roof', 'קו גגון / גבול גיליון 2'), ('k-demo', 'קיים — לפירוק'), ('k-sew', 'קו ביוב קיים (מפה מצבית)'), ('k-cut', 'קו חתך')]
    for i, (c, t) in enumerate(lines):
        yy = y + i*55
        sh.add('<line class="%s" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (c, lx-80, yy-12, lx, yy-12))
        sh.raw_text(lx-100, yy, t, 'k-note2', 0, 'start')
    y += len(lines)*55 + 30
    sh.add('<path class="k-svx" d="M%d,%d l16,16 M%d,%d l16,-16"/>' % (lx-48, y-26, lx-48, y-10))
    sh.raw_text(lx-100, y, 'מפלס קיים — מפה מצבית (מיקום ±20)', 'k-note2', 0, 'start')
    y += 60
    sh.add('<path class="k-acc" d="M%d,%d l-12,-18 l24,0 z"/>' % (lx-40, y-4))
    sh.raw_text(lx-100, y, 'מפלס מתוכנן', 'k-note2', 0, 'start')
    y += 60
    sh.raw_text(lx, y, '★ מודפס במקור · ≈ נמדד בקנ״מ · ? לא נסגר', 'k-note2', 0, 'start')
    y += 55
    sh.raw_text(lx, y, 'כל המידות בס״מ · מפלסים במטרים מעל פני הים', 'k-note2', 0, 'start')
    y += 110
    sh.raw_text(lx, y, 'הערות', 'k-h', 0, 'start')
    notes = ['1. המגרש, השערים והמפלסים — מהגרמושקה 2.1.24',
             '   (מפה מצבית 1:250 + קומת קרקע 1:100).',
             '   הבית — מהעמדה של נופר 21.08.26.',
             '2. הבית הוצב לפי 300 ★ ממערב ו־483 ★ מדרום.',
             '   במזרח המקורות לא נסגרים (≈28 ס״מ) —',
             '   לסמן שם מקיר הבית, לא מהגדר.',
             '3. ⚠ בין השערים 943 בגיליון אחד ו־880 באחר.',
             '   943 סוגר את השרשרת ל־16.70 ★;',
             '   לסמן בכל מקרה מהמשקוף בשטח.',
             '4. צפון התוכנית כלפי מעלה, כמו אצל נופר.',
             '5. מידה שאינה רשומה — לא למדוד מהשרטוט.']
    for i, t in enumerate(notes): sh.raw_text(lx, y+55+i*44, t, 'k-note2', 0, 'start')
    title_block(sh, 1790, 3720, 1140, 440, 'תוכנית פיתוח — חצר ושבילי כניסה', 'גיליון 1 מתוך 2 · קנ״מ 1:100 (A3)', 34)
    return sh.svg(W, H, 'גיליון 1 — תוכנית פיתוח החצר, אשל 57', defs('cpS1', k), style('cpS1', k))

# ================================================================ SHEET 2 — entrance 1:50 + section (A3 landscape)
def sheet2():
    k = 1.0
    sh = Sheet('cpS2', lambda X, Y: (1540 - Y, 690 - X)); sh.k = k; sh.tick = 9; sh.sweep = 0
    W, H = 2100, 1485
    sh.add('<rect class="k-paper" x="0" y="0" width="%d" height="%d"/>' % (W, H))
    sh.add('<rect class="k-frame" x="20" y="20" width="%d" height="%d"/>' % (W-40, H-40))
    sh.add('<clipPath id="cpS2-clip"><rect x="200" y="120" width="1440" height="620"/></clipPath><g clip-path="url(#cpS2-clip)">')
    sh.rect(13, -90, 600, 1400, 'k-lawn')
    sh.rect(13, 13, 600, 285, 'k-undec'); sh.rect(SP1, ARM[1], 600, ARM[3], 'k-undec')
    sh.rect(13, 13, SP0, 1400, 'k-plant'); sh.rect(SP0, COL[1], HX_W, 1400, 'k-plant')
    sh.rect(SP1, STUB_Y, HX_SW, R[3], 'k-plant'); sh.rect(HX_SW+WALL, STUB_Y, 600, HY_S, 'k-plant')
    sh.rect(-90, -120, 600, -4, 'k-bg')
    sh.rect(SP0, 13, SP1, R[0], 'k-undec')
    plants(sh, 13, 30, SP0, 900, 16, 3, 9, 16); plants(sh, SP1+10, STUB_Y+10, HX_SW-10, R[3]-10, 12, 5, 10, 20)
    plants(sh, 13, COL[1]+10, SP0+20, 1400, 6, 7, 9, 15); plants(sh, AX+55, COL[1]+60, HX_W, 1400, 5, 9, 8, 13)
    for i in range(3): sh.rect(SP0, R[i], SP1, R[i+1], 'k-conc')
    sh.poly([(SP0, R[3]), (HX_SW, R[3]), (HX_SW, HY_DOOR), (HX_W, HY_DOOR), (HX_W, COL[3]), (COL[2], COL[3]), (COL[2], COL[1]), (SP0, COL[1])], 'k-conc')
    for j in range(7):
        y = 965 + j*65; sh.rect(AX-45, y, AX+45, y+45, 'k-stone')
    sh.pline([(HX_W, COL[3]+3), (COL[2]+3, COL[3]+3), (COL[2]+3, COL[1]-3), (HX_W-2, COL[1]-3)], 'k-thin')
    sh.line((COL[2], R[3]), (COL[2], COL[1]), 'k-thin')
    house_parts(sh)
    sh.rect(HX_W+WALL, HY_DOOR+WALL, 600, 1400, 'k-house')
    for i, y in enumerate(R): sh.line((SP0, y), (SP1 if i < 3 else HX_SW, y), 'k-nose')
    for y in (803, 835, 868, 901): sh.line((120, y), (301, y), 'k-demo')
    sh.rect(-4, -4, 600, 13, 'k-fence'); sh.rect(-4, -4, 13, 1400, 'k-fence')
    sh.rect(GATE_P[1], -6, GATE_P[2], 15, 'k-open')
    for a, b in ((GATE_P[0], GATE_P[1]), (GATE_P[2], GATE_P[3])): sh.rect(a, -10, b, 17, 'k-col')
    g0 = sh.P(GATE_P[1], 13); g1 = sh.P(GATE_P[1], 13+101); g2 = sh.P(GATE_P[2], 13)
    sh.add('<line class="k-med" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (g0[0], g0[1], g1[0], g1[1]))
    sh.add('<path class="k-thin" d="M%.1f,%.1f A101,101 0 0 1 %.1f,%.1f"/>' % (g1[0], g1[1], g2[0], g2[1]))
    sh.pline([(600, 231), (201, 247), (-60, -150)], 'k-sew'); sh.circ(MANHOLE_SW, 30, 'k-mh'); sh.circ(MANHOLE_SW, 22, 'k-thin')
    sh.add('</g>')
    arrow(sh, [(AX, 50), (AX, R[3]+45)])
    arrow(sh, [(AX, R[3]+45), (395, R[3]+45), (395, HY_DOOR-25)])
    arrow(sh, [(AX, R[3]+45), (AX, 1320)], dash='9 7')
    sh.text(150, 70, 'עולה', 'k-labs')
    arrow(sh, [(445, 1170), (445, 1060)], 'k-fall', 'cpS2-ah'); sh.text(445, 1115, '1.5%', 'k-labs', 0, 'middle', dy=-10)
    arrow(sh, [(125, 925), (125, 845)], 'k-fall', 'cpS2-ah'); sh.text(125, 885, '1.5%', 'k-labs', 0, 'middle', dy=-10)
    arrow(sh, [(230, 250), (230, 120)], 'k-fall', 'cpS2-ah'); sh.text(230, 185, '2.9%', 'k-labs', 0, 'middle', dy=-10)
    for i in range(3):
        ym = (R[i]+R[i+1])/2
        sh.text(215, ym, 'פודסט %d' % (i+1), 'k-lab'); sh.text(180, ym, '150×168 · 2.9%', 'k-labs')
    sh.text(448, 858, 'רחבה עליונה', 'k-lab'); sh.text(420, 858, '367×150 · לפני העמוד', 'k-labs')
    sh.text(360, 1100, 'מבואה מקורה (גגון קיים)', 'k-labs')
    sh.text(272, 1000, '→ עמוד קיים ≈20×60', 'k-lab', 0, 'start', dx=-6)
    sh.text(520, 893, 'חלון קיים', 'k-labs')
    sh.text(560, 1260, 'בית', 'k-labb'); sh.text(395, 1280, 'דלת ≈100', 'k-labs')
    sh.text(122, 175, 'חצר השער', 'k-lab')
    sh.text(420, 170, 'חזית — טרם הוחלט', 'k-labs'); sh.text(560, 342, '→ לחנייה (זרוע)', 'k-labs')
    sh.text(380, 590, 'ערוגה / גינת סלעים', 'k-labs')
    sh.text(58, 360, 'ערוגה מערבית', 'k-labs')
    sh.text(55, 1230, 'אבני מדרך ← לגינה האחורית', 'k-labs')
    sh.text(300, 330, 'שוחת ביוב קיימת 49.18 → 49.15', 'k-sewt')
    sh.text(420, -60, 'מדרכה', 'k-labs')
    sh.text(80, 868, 'מדרגות קיימות', 'k-labs'); sh.text(55, 868, 'לפירוק', 'k-labs')
    lvl(sh, AX+45, 58, '%.2f' % G_LVL, k=0.95)
    for i in range(4): lvl(sh, 120, R[i]+8, '%.2f' % [LV[2][1], LV[4][1], LV[6][1], LV[8][1]][i], k=0.95)
    lvl(sh, 225, COL[1]-8, '%.2f' % z_land(COL[1]), k=0.95)
    lvl(sh, 395, HY_DOOR-12, '50.00', k=0.95)
    for (X, Y), t, corner in SURVEY:
        inpath = (SP0-5 <= X <= HX_SW and FENCE_IN <= Y <= COL[1]+20)
        if -95 < Y < 1330 and X < 560 and not inpath: svlvl(sh, X, Y, t, 0.95)
    for y0, y1 in ((-150, -100), (1330, 1470)):
        a, b = sh.P(AX, y0), sh.P(AX, y1); sh.add('<line class="k-cut" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (a[0], a[1], b[0], b[1]))
    for yy in (-150, 1470):
        x, y = sh.P(AX, yy); sh.add('<path d="M%.1f,%.1f l0,-28 l-9,0 l9,-15 l9,15 l-9,0" fill="#2b2824"/>' % (x, y)); sh.raw_text(x+22, y-16, 'א', 'k-cutT')
    chain = [0, FENCE_IN, R[0], R[1], R[2], R[3], COL[1], COL[3], HY_DOOR]
    names = ['13', '266', '168', '168', '168', '150', '≈60', '≈210']
    for i in range(len(names)): sh.dim((-4, chain[i]), (-4, chain[i+1]), (-80, 0), names[i])
    sh.dim((-4, 0), (-4, COL[1]), (-148, 0), '933 — מגבול המגרש לפאה הדרומית של העמוד')
    xs = [0, FENCE_IN, SP0, SP1]
    for i, t in enumerate(['13', '90', '150']): sh.dim((xs[i], -100), (xs[i+1], -100), (0, -30), t)
    xs2 = [SP0, HX_W, COL[2], HX_SW]
    for i, t in enumerate(['197', '≈20', '≈150']): sh.dim((xs2[i], 1330), (xs2[i+1], 1330), (0, 45), t)
    sh.dim((SP0, 1330), (HX_SW, 1330), (0, 105), '≈367')
    section(sh)
    sh.add('<g transform="translate(1790 235) rotate(-90)"><circle r="44" fill="none" stroke="#2b2824" stroke-width="2"/><path d="M0,-56 L16,32 L0,19 L-16,32 Z" fill="#2b2824"/></g>')
    sh.raw_text(1715, 228, 'צ', 'k-cutT'); sh.raw_text(1790, 310, 'צפון — שמאלה', 'k-labs')
    sh.raw_text(1630, 104, 'תוכנית — כניסה ושביל מערבי · 1:50', 'k-h', 0, 'start')
    sx0, sy0 = 1880, 380
    for i in range(4):
        sh.add('<rect x="%d" y="%d" width="50" height="10" fill="%s" stroke="#2b2824" stroke-width="1.2"/>' % (sx0+i*50, sy0, '#2b2824' if i % 2 == 0 else '#fff'))
    for i, t in enumerate(['0', '0.5', '1', '1.5', '2 מ׳']): sh.raw_text(sx0+i*50, sy0+34, t, 'k-labs')
    sh.raw_text(sx0+100, sy0-12, '1:50 בהדפסת A3', 'k-labs')
    notes2(sh)
    title_block(sh, 1665, 1170, 410, 285, 'פרט כניסה + חתך א–א', 'גיליון 2 מתוך 2 · 1:50 (A3)', 17)
    return sh.svg(W, H, 'גיליון 2 — פרט הכניסה וחתך לאורך השביל, אשל 57', defs('cpS2', k), style('cpS2', k))

def notes2(sh):
    x = 2068; y = 470
    L = [('עקרונות הסימון', 'h'),
         ('• הכול מסומן מהעמוד הקיים, לא מהגדר:', ''),
         ('  R4 = 150 מדרום לפאה הדרומית שלו;', ''),
         ('  R3, R2, R1 — כל 168 ס״מ דרומה.', ''),
         ('• ציר השביל = מרכז הפשפש. רוחב 150.', ''),
         ('• ארבעה רומים זהים, 16 ס״מ — חובה.', ''),
         ('• חזית מדרגה סגורה ואנכית, בלי', ''),
         ('  בסיס נסוג (החלטה); חריץ צל בצדדים.', ''),
         ('• פודסטים 2.9% לכיוון השער;', ''),
         ('  הרחבה 1.5% מהדלת החוצה.', ''),
         ('• מימין לעמוד — ≈150 אל הדלת;', ''),
         ('  משמאלו — 197 ישר לאבני המדרך.', ''),
         ('• ערוגות ממולאות עד 15 ס״מ מתחת', ''),
         ('  לשפת הבטון (לא נפילה חופשית).', ''),
         ('', ''),
         ('לבדוק בשטח לפני יציקה', 'h'),
         ('• מדידת בקרה: שער, 4 אפים, עמוד,', ''),
         ('  סף דלת, מכסה השוחה.', ''),
         ('• מיקום השוחה (±20). קרוב מ־15', ''),
         ('  ס״מ ל־R1 — להזיז את R1 צפונה.', ''),
         ('• קיר חדר שינה 2: ≈150 מהעמוד', ''),
         ('  לפי נופר; 149 כולל עמוד במפה', ''),
         ('  המצבית — מטר אחד בשטח מכריע.', ''),
         ('• רוחב כנף הפשפש (כאן 101).', '')]
    yy = y
    for t, c in L:
        if c == 'h': yy += 8; sh.raw_text(x, yy, t, 'k-h2', 0, 'start'); yy += 30
        else: sh.raw_text(x, yy, t, 'k-note2', 0, 'start'); yy += 27

def section(sh):
    VEX = 2.0
    def zy(z): return 1085 - (z - 50.00)*100*VEX
    def sx(Y): return 1540 - Y
    add = sh.add
    ZT = 50.95; top = zy(ZT)
    for z in (49.00, 49.50, 50.00, 50.50):
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#cfc7ba" stroke-width="0.8" stroke-dasharray="3 6"/>' % (sx(1360), zy(z), sx(-100), zy(z)))
        sh.raw_text(sx(1360)-8, zy(z)+6, '%.2f' % z, 'k-labs', 0, 'end')
    add('<rect class="k-house" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (sx(HY_DOOR), top, sx(HY_S)-sx(HY_DOOR), zy(49.30)-top))
    for y in WIN_BR2:
        add('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#5f584e" stroke-width="1.1" stroke-dasharray="6 4"/>' % (sx(y), top, sx(y), zy(50.05)))
    sh.raw_text((sx(WIN_BR2[0])+sx(WIN_BR2[1]))/2+10, zy(50.75), 'חלון', 'k-labs')
    sh.raw_text((sx(WIN_BR2[0])+sx(WIN_BR2[1]))/2+10, zy(50.75)+22, 'גובה לא ידוע', 'k-labs')
    sh.raw_text(sx(HY_S)-10, top+24, 'ברקע: קיר חדר שינה 2, במבט מזרחה', 'k-labs', 0, 'end')
    add('<rect class="k-col" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (sx(COL[3]), top, sx(COL[1])-sx(COL[3]), zy(z_land(COL[1]))-top))
    sh.raw_text(sx(COL[3])-10, top+24, 'עמוד קיים', 'k-lab', 0, 'start')
    sh.raw_text(sx(COL[3])-10, top+48, 'גובה — לא בשרטוט', 'k-labs', 0, 'start')
    add('<rect class="k-wall" x="%.1f" y="%.1f" width="%.1f" height="%.1f"/>' % (sx(HY_DOOR+WALL), top, WALL, zy(50.03)-top))
    x0, x1 = sx(HY_DOOR+WALL)-6, sx(HY_S)+6
    add('<path d="M%.1f,%.1f L%.1f,%.1f l10,-9 l10,18 l10,-9 L%.1f,%.1f" fill="none" stroke="#5f584e" stroke-width="1.2"/>' % (x0, top, (x0+x1)/2-15, top, x1, top))
    exist = [(-100, 49.01), (13, 49.06), (118, 49.07), (247, 49.18), (471, 49.34), (725, 49.30), (803, 49.30), (803, 49.44), (835, 49.44), (835, 49.58), (868, 49.58), (868, 49.73), (901, 49.73), (901, 49.87), (940, 49.87), (1108, 49.95), (1360, 49.93)]
    bot = zy(48.85)
    add('<polygon class="k-soil" points="%s %.1f,%.1f %.1f,%.1f"/>' % (' '.join('%.1f,%.1f' % (sx(y), zy(z)) for y, z in exist), sx(1360), bot, sx(-100), bot))
    def ex(y):
        for (y0, z0), (y1, z1) in zip(exist, exist[1:]):
            if y0 <= y <= y1 and y1 > y0: return z0 + (z1-z0)*(y-y0)/(y1-y0)
        return exist[-1][1]
    prof = [(y, z) for y, z in LV] + [(COL[1], z_land(COL[1]))]
    poly = ['%.1f,%.1f' % (sx(y), zy(z-0.15)) for y, z in prof]
    poly += ['%.1f,%.1f' % (sx(y), zy(min(ex(y), z-0.15))) for y, z in reversed(prof)]
    add('<polygon class="k-fill" points="%s"/>' % ' '.join(poly))
    for a, b in [(R[0], R[1]), (R[1], R[2]), (R[2], R[3]), (R[3], COL[1])]:
        za = [z for y, z in LV if y == a][-1]
        zb = [z for y, z in LV if y == b][0] if b != COL[1] else z_land(COL[1])
        add('<polygon class="k-conc" points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f"/>' % (sx(a), zy(za), sx(b), zy(zb), sx(b), zy(zb-0.15), sx(a), zy(za-0.15)))
    add('<polygon class="k-undec" points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f"/>' % (sx(FENCE_IN), zy(LV[0][1]), sx(R[0]), zy(LV[1][1]), sx(R[0]), zy(LV[1][1]-0.08), sx(FENCE_IN), zy(LV[0][1]-0.08)))
    for j in range(6):
        y = 965 + j*65; z = 49.955 - 0.0003*(y-965)
        add('<rect class="k-stone" x="%.1f" y="%.1f" width="45" height="%.1f"/>' % (sx(y+45), zy(z), 0.06*100*VEX))
    add('<polyline class="k-med" points="%s"/>' % ' '.join('%.1f,%.1f' % (sx(y), zy(z)) for y, z in [(-100, 49.03), (13, 49.05)] + prof))
    add('<polyline class="k-gnd" points="%s"/>' % ' '.join('%.1f,%.1f' % (sx(y), zy(z)) for y, z in exist))
    sh.raw_text(sx(600), zy(49.22)+30, 'קרקע קיימת — מפה מצבית', 'k-sv')
    sh.raw_text(sx(850), zy(49.30)+30, 'מדרגות קיימות (לפירוק)', 'k-sv')
    sh.raw_text(sx(700), zy(49.47), 'מילוי מהודק', 'k-labs')
    add('<rect class="k-wall" x="%.1f" y="%.1f" width="17" height="%.1f"/>' % (sx(13), zy(50.05), zy(48.95)-zy(50.05)))
    sh.raw_text(sx(13)+8, zy(50.05)-10, 'גדר 50.05', 'k-sv', 0, 'end')
    add('<rect x="%.1f" y="%.1f" width="60" height="%.1f" fill="none" stroke="#2f6690" stroke-width="1.6" stroke-dasharray="6 4"/>' % (sx(277), zy(49.15), zy(48.88)-zy(49.15)))
    sh.raw_text(sx(247), zy(48.88)+20, 'שוחה', 'k-sewt')
    tags = [(40, G_LVL, 'סף שער'), (R[0], LV[2][1], 'R1'), (R[1], LV[4][1], 'R2'), (R[2], LV[6][1], 'R3'), (R[3], LV[8][1], 'R4'), (COL[1]-40, z_land(COL[1]-40), 'רחבה')]
    for y, z, n in tags:
        x0 = sx(y); y0 = zy(z)
        add('<line class="k-thin" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (x0, y0-5, x0, y0-62))
        add('<rect class="k-lvlbox" x="%.1f" y="%.1f" width="66" height="23" rx="3"/>' % (x0-33, y0-86))
        sh.raw_text(x0, y0-69, '%.2f' % z, 'k-lvl')
        sh.raw_text(x0, y0-93, n, 'k-labs')
    for i in range(4):
        z = [zz for yy, zz in LV if yy == R[i]][-1]
        sh.raw_text(sx(R[i])+8, zy(z)+30, '16', 'k-dt', 0, 'start')
    add('<line class="k-thin" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (sx(HY_DOOR), zy(50.00), sx(HY_DOOR)+60, zy(50.00)))
    sh.raw_text(sx(HY_DOOR+WALL)+WALL+8, zy(50.00)-60, 'סף דלת 50.00', 'k-lvl', 0, 'end')
    sh.raw_text(sx(HY_DOOR+WALL)+WALL+8, zy(50.00)-36, 'רצפה ±0.00 = 50.03', 'k-labs', 0, 'end')
    yb = bot + 40
    ch = [FENCE_IN, R[0], R[1], R[2], R[3], COL[1]]
    for a, b in zip(ch, ch[1:]):
        A, B = sx(a), sx(b)
        add('<line class="k-dim" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (A, yb, B, yb))
        for p in (A, B): add('<line class="k-tick" x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f"/>' % (p-7, yb+7, p+7, yb-7))
        sh.raw_text((A+B)/2, yb-8, '%d' % round(b-a), 'k-dt')
    sh.raw_text(1630, yb+62, 'חתך א–א לאורך ציר השביל, במבט מזרחה · אופקי 1:50 · אנכי ×2', 'k-h', 0, 'start')

if __name__ == '__main__':
    import os
    d = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    s1, s2 = sheet1(), sheet2()
    hdr = '<?xml version="1.0" encoding="UTF-8"?>\n'
    open(os.path.join(d, 'sheet1.svg'), 'w').write(hdr + s1)
    open(os.path.join(d, 'sheet2.svg'), 'w').write(hdr + s2)
    html = ('<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;500;600;700;800&display=swap" rel="stylesheet">'
            '<style>body{margin:0;background:#8a8a8a}svg{display:block;width:%dpx;height:auto;margin:0 auto 20px}</style>%s')
    open(os.path.join(d, 'tools/preview1.html'), 'w').write(html % (1485, s1))
    open(os.path.join(d, 'tools/preview2.html'), 'w').write(html % (2100, s2))
    print('R=%.2f  levels: %s' % (LV[-1][1]-G_LVL, [(y, round(z, 3)) for y, z in LV]))
