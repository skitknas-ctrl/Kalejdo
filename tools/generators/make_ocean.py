# -*- coding: utf-8 -*-
"""Ocean-paketet för Kalejdo, version 2: ritat från grunden efter verkliga havsdjur.
Form och material ges av toningar (userSpaceOnUse), speglingar och egenskuggor. Inga konturer,
inga slagskuggor, ingen bakgrund. Ett djur per fil, utom fiskstim, tång, sjögräs och korall
som till sin natur är flera. Kör: python tools/generators/make_ocean.py store-src/ocean"""
import os, sys, math, random

OUT = sys.argv[1] if len(sys.argv) > 1 else 'ocean_svg'
os.makedirs(OUT, exist_ok=True)
random.seed(7)

def hexrgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def rgbhex(c):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(round(v)))) for v in c)
def sh(h, f):
    r, g, b = hexrgb(h)
    if f >= 0: return rgbhex((r + (255 - r) * f, g + (255 - g) * f, b + (255 - b) * f))
    return rgbhex((r * (1 + f), g * (1 + f), b * (1 + f)))
def mix(a, b, t):
    A, B = hexrgb(a), hexrgb(b); return rgbhex(tuple(A[i] + (B[i] - A[i]) * t for i in range(3)))
def f1(v): return f'{v:.1f}'.replace('.0', '') if abs(v - round(v)) < 0.05 else f'{v:.1f}'

def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0],
            u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1])

def tapered(p0, p1, p2, p3, w0, w1, n=18, tip='round'):
    """Sluten bana runt en kubisk kurva med bredd w0 vid start och w1 vid slut."""
    pts, L, R = [], [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(p0, p1, p2, p3, t)
        e = 1e-3
        xa, ya = bez(p0, p1, p2, p3, max(0, t - e)); xb, yb = bez(p0, p1, p2, p3, min(1, t + e))
        dx, dy = xb - xa, yb - ya; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        w = (w0 + (w1 - w0) * t) / 2
        L.append((x + nx * w, y + ny * w)); R.append((x - nx * w, y - ny * w))
    d = 'M' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in L)
    if tip == 'round' and w1 > 0.3:
        d += f' A{f1(w1/2)} {f1(w1/2)} 0 0 1 {f1(R[-1][0])} {f1(R[-1][1])}'
    d += ' L' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in reversed(R)) + 'Z'
    return d

def polar(cx, cy, r, deg):
    a = math.radians(deg); return (cx + r * math.cos(a), cy + r * math.sin(a))

class D:
    def __init__(self, rot=0):
        self.defs, self.body, self.n, self.rot = [], [], 0, rot
    def _id(self):
        self.n += 1; return f'g{self.n}'
    def g(self, stops, x1, y1, x2, y2):
        i = self._id()
        s = ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else '') + '/>' for o, c, *rest in stops for a in [rest[0] if rest else None])
        self.defs.append(f'<linearGradient id="{i}" gradientUnits="userSpaceOnUse" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>')
        return f'url(#{i})'
    def rg(self, stops, cx, cy, r, fx=None, fy=None):
        i = self._id()
        s = ''.join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else '') + '/>' for o, c, *rest in stops for a in [rest[0] if rest else None])
        f = f' fx="{fx}" fy="{fy}"' if fx is not None else ''
        self.defs.append(f'<radialGradient id="{i}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>')
        return f'url(#{i})'
    def clip(self, d):
        i = self._id(); self.defs.append(f'<clipPath id="{i}"><path d="{d}"/></clipPath>'); return i
    def open(self, clip=None, extra=''):
        self.body.append('<g' + (f' clip-path="url(#{clip})"' if clip else '') + extra + '>')
    def close(self): self.body.append('</g>')
    def p(self, d, fill, extra=''):
        self.body.append(f'<path d="{d}" fill="{fill}"{extra}/>')
    def c(self, cx, cy, r, fill, extra=''):
        self.body.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}" fill="{fill}"{extra}/>')
    def e(self, cx, cy, rx, ry, fill, rot=0, extra=''):
        t = f' transform="rotate({rot} {f1(cx)} {f1(cy)})"' if rot else ''
        self.body.append(f'<ellipse cx="{f1(cx)}" cy="{f1(cy)}" rx="{f1(rx)}" ry="{f1(ry)}" fill="{fill}"{t}{extra}/>')
    def line(self, d, col, w, op=1, cap='round', blur=False, extra=''):
        self.body.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-opacity="{op}" stroke-linecap="{cap}"' + (' filter="url(#bl)"' if blur is True else (f' filter="url(#{blur})"' if blur else '')) + extra + '/>')
    def spec(self, d, w=0.9, op=0.7, blur=False): self.line(d, '#ffffff', w, op, blur=blur)
    def dark(self, d, w=1.2, op=0.35, blur=True): self.line(d, '#000000', w, op, blur=blur)
    def soft(self, d, fill, op, blur='bl2'):
        """mjuk skuggning/ljus inne i formen (använd inom clip)"""
        self.body.append(f'<path d="{d}" fill="{fill}" fill-opacity="{op}" filter="url(#{blur})"/>')
    def eye(self, cx, cy, r, iris='#2a2420', ring='#d9c59a', ringw=0.35):
        self.c(cx, cy, r, ring)
        self.c(cx, cy, r * (1 - ringw), self.rg([(0, '#4a403a'), (0.6, iris), (1, '#050505')], cx, cy, r))
        self.c(cx - r * 0.3, cy - r * 0.3, r * 0.28, '#ffffff', ' fill-opacity="0.9"')
        self.c(cx + r * 0.25, cy + r * 0.3, r * 0.12, '#ffffff', ' fill-opacity="0.4"')
    def svg(self):
        defs = ('<defs><filter id="bl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="0.8"/></filter>'
                '<filter id="bl2" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="2.2"/></filter>'
                + ''.join(self.defs) + '</defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">{defs}'
                f'<g transform="rotate({self.rot} 50 50)">{"".join(self.body)}</g></svg>')

F = {}

def scales(d, clipid, x0, x1, y0, y1, step, col, op=0.25, w=0.4):
    """fjällmönster: rader av små bågar inne i en clip"""
    d.open(clipid)
    r = step * 0.55
    row = 0
    y = y0
    while y < y1 + step:
        x = x0 + (step / 2 if row % 2 else 0)
        segs = []
        while x < x1 + step:
            segs.append(f'M{f1(x-r)} {f1(y)}a{f1(r)} {f1(r*0.8)} 0 0 0 {f1(2*r)} 0')
            x += step
        d.line(''.join(segs), col, w, op)
        y += step * 0.8; row += 1
    d.close()

def fin(d, path, base, edge, rays, rayw=0.45, rayop=0.4, op=0.92):
    """fena med toning från bas till kant och fenstrålar"""
    d.p(path, d.g([(0, base), (1, edge)], *rays[0]), f' fill-opacity="{op}"')
    for r in rays[1]:
        d.line(r, sh(base, -0.45), rayw, rayop)

# ============================================================ CLOWNFISH (Amphiprion ocellaris)
d = D(-8)
BODY = 'M11 50C13 37 29 28 50 28C66 28 77 35 81 45L82 50L81 55C77 65 66 72 50 72C29 72 13 63 11 50Z'
cb = d.clip(BODY)
# fenor bakom kroppen
fin(d, 'M30 33C40 17 62 15 76 32C70 29 60 28 50 28C40 28 34 30 30 33Z', '#ff7a1a', '#ffb168', ((0, 30, 0, 16), ['M38 30C42 24 46 20 48 18', 'M46 29C50 23 54 19 56 17', 'M54 28C58 23 62 20 66 20', 'M62 29C66 26 70 25 72 27']))
d.line('M30 33C40 17 62 15 76 32', '#1a1a1a', 1.1, 0.55)
fin(d, 'M38 70C42 81 54 83 58 70C52 72 44 72 38 70Z', '#ff7a1a', '#ffb168', ((0, 70, 0, 83), ['M44 71L44 79', 'M49 72L50 81', 'M54 71L55 78']))
d.line('M38 70C42 81 54 83 58 70', '#1a1a1a', 1.0, 0.5)
fin(d, 'M64 67C68 77 76 76 78 62C74 65 70 67 64 67Z', '#ff7a1a', '#ffb168', ((0, 66, 0, 77), ['M68 68L70 75', 'M73 66L75 72']))
d.line('M64 67C68 77 76 76 78 62', '#1a1a1a', 1.0, 0.5)
# stjärt
fin(d, 'M79 46C86 40 92 36 97 34C94 42 94 58 97 66C92 64 86 60 79 54Z', '#ff7a1a', '#ffb168', ((80, 0, 97, 0), ['M82 48L94 40', 'M83 50L95 48', 'M83 52L95 56', 'M82 53L94 62']))
d.line('M79 46C86 40 92 36 97 34M97 66C92 64 86 60 79 54', '#1a1a1a', 1.1, 0.6)
d.line('M94 37C92 45 92 55 94 63', '#ffffff', 2.2, 0.7)
# kropp
d.p(BODY, d.g([(0, '#c84a0c'), (0.25, '#f06f14'), (0.5, '#ff8a2e'), (0.75, '#ffa85a'), (1, '#d8661a')], 0, 28, 0, 72))
d.open(cb)
d.soft('M20 34C40 24 70 26 80 38C70 36 40 36 20 44Z', '#ffffff', 0.25)
d.soft('M14 56C30 66 60 70 80 58C70 72 30 74 14 62Z', '#5a1e00', 0.35)
# vita band med mörka kanter
for band in ('M27 27C33 27 36 50 33 73L26 73C22 50 22 27 27 27Z', 'M48 27C60 29 65 46 59 73L51 73C46 50 44 36 48 27Z', 'M75 33C80 40 82 50 80 62L75 67C73 56 73 44 75 33Z'):
    d.p(band, d.g([(0, '#d8dde2'), (0.3, '#ffffff'), (0.8, '#f4f6f8'), (1, '#c9cfd6')], 0, 28, 0, 72))
for edge in ('M27 27C33 27 36 50 33 73', 'M27 27C22 50 22 73 26 73', 'M48 27C60 29 65 46 59 73', 'M48 27C44 36 46 50 51 73', 'M75 33C80 40 82 50 80 62', 'M75 33C73 44 73 56 75 67'):
    d.line(edge, '#1a1a1a', 1.0, 0.75)
scales(d, cb, 11, 82, 28, 72, 3.2, '#8a3a00', 0.18, 0.35)
d.close()
d.line('M11 50C14 45 17 43 19 42', '#5a1e00', 0.7, 0.5)                     # mun
d.eye(21, 45, 3.6, '#1a1612', '#f7c27a', 0.3)
d.line('M18 56C22 59 27 60 31 59', '#ffffff', 0.6, 0.3)                    # gälöppning
F['clownfish'] = d.svg()

# ============================================================ BLUE TANG (Paracanthurus hepatus)
d = D(-6)
BODY = 'M10 50C13 34 30 25 52 25C70 25 81 34 84 46L84 54C81 66 70 75 52 75C30 75 13 66 10 50Z'
cb = d.clip(BODY)
fin(d, 'M22 32C40 10 70 10 82 36C72 28 60 25 52 25C40 25 30 27 22 32Z', '#143a9a', '#2a62d8', ((0, 10, 0, 32), [f'M{x} {y}C{x+2} {y-6} {x+4} {y-10} {x+5} {y-14}' for x, y in ((32, 28), (40, 26), (48, 25), (56, 25), (64, 26), (72, 29))]))
d.line('M22 32C40 10 70 10 82 36', '#0a1430', 1.1, 0.6)
fin(d, 'M24 68C40 92 72 90 82 64C72 72 60 75 52 75C40 75 30 73 24 68Z', '#143a9a', '#2a62d8', ((0, 68, 0, 92), [f'M{x} {y}C{x+1} {y+5} {x+2} {y+9} {x+3} {y+12}' for x, y in ((34, 72), (42, 74), (50, 75), (58, 75), (66, 73))]))
d.line('M24 68C40 92 72 90 82 64', '#0a1430', 1.1, 0.6)
fin(d, 'M82 44C88 38 94 34 98 33C95 42 95 58 98 67C94 66 88 62 82 56Z', '#f0b400', '#ffd84a', ((82, 0, 98, 0), ['M84 46L94 38', 'M85 50L96 50', 'M84 54L94 62']))
d.line('M82 44C88 38 94 34 98 33M98 67C94 66 88 62 82 56', '#0a1430', 1.0, 0.65)
d.p(BODY, d.g([(0, '#0e2e8a'), (0.3, '#1d55c8'), (0.55, '#2f72e8'), (0.8, '#2a66d4'), (1, '#143a9a')], 0, 25, 0, 75))
d.open(cb)
d.soft('M16 40C36 28 68 30 82 44C68 40 36 42 16 50Z', '#8ab8ff', 0.3)
d.soft('M12 58C30 70 68 72 84 58C70 76 30 78 12 64Z', '#020a30', 0.4)
# palettmärket (svart)
d.p('M24 46C40 32 66 32 78 44L80 52C70 44 48 44 36 54C32 56 28 54 26 50Z', d.g([(0, '#0a0c14'), (1, '#1a2238')], 0, 32, 0, 56))
d.p('M70 40C78 44 80 54 72 62L66 60C72 54 72 48 66 42Z', '#0a0c14')
scales(d, cb, 10, 84, 25, 75, 3.4, '#061a50', 0.2, 0.35)
d.close()
fin(d, 'M36 52C44 50 54 56 50 64C44 64 38 60 36 52Z', '#2f72e8', '#8ab8ff', ((36, 0, 52, 0), ['M38 53L48 60', 'M40 56L46 62']), op=0.75)
d.line('M10 50C13 48 15 47 17 47', '#061a50', 0.7, 0.5)
d.eye(21, 45, 3.4, '#0a0a0a', '#e8d8a0', 0.3)
F['blue_tang'] = d.svg()

# ============================================================ FISH SCHOOL (sardiner, tillåtet flertal)
d = D(-18)
def small_fish(cx, cy, s, flip=False):
    sx = -1 if flip else 1
    def X(x): return cx + sx * (x - 50) * s
    def Y(y): return cy + (y - 50) * s
    body = f'M{f1(X(30))} {f1(Y(50))}C{f1(X(34))} {f1(Y(44))} {f1(X(46))} {f1(Y(41))} {f1(X(58))} {f1(Y(43))}C{f1(X(66))} {f1(Y(44))} {f1(X(70))} {f1(Y(48))} {f1(X(70))} {f1(Y(50))}C{f1(X(70))} {f1(Y(52))} {f1(X(66))} {f1(Y(56))} {f1(X(58))} {f1(Y(57))}C{f1(X(46))} {f1(Y(59))} {f1(X(34))} {f1(Y(56))} {f1(X(30))} {f1(Y(50))}Z'
    tail = f'M{f1(X(69))} {f1(Y(48))}C{f1(X(73))} {f1(Y(44))} {f1(X(76))} {f1(Y(42))} {f1(X(78))} {f1(Y(41))}C{f1(X(76))} {f1(Y(47))} {f1(X(76))} {f1(Y(53))} {f1(X(78))} {f1(Y(59))}C{f1(X(76))} {f1(Y(58))} {f1(X(73))} {f1(Y(56))} {f1(X(69))} {f1(Y(52))}Z'
    d.p(tail, d.g([(0, '#6f8aa6'), (1, '#b8c9d8')], X(69), 0, X(78), 0), ' fill-opacity="0.85"')
    d.p(body, d.g([(0, '#2f4f73'), (0.3, '#6d8ea8'), (0.5, '#dfe9f1'), (0.75, '#f7fafc'), (1, '#b8c6d2')], 0, Y(41), 0, Y(57)))
    d.line(f'M{f1(X(36))} {f1(Y(49))}L{f1(X(66))} {f1(Y(49.5))}', '#1e3550', 0.6 * s, 0.35)
    d.line(f'M{f1(X(40))} {f1(Y(44.5))}C{f1(X(48))} {f1(Y(43))} {f1(X(58))} {f1(Y(43.5))} {f1(X(64))} {f1(Y(45))}', '#ffffff', 0.7 * s, 0.6)
    d.p(f'M{f1(X(46))} {f1(Y(43))}C{f1(X(50))} {f1(Y(38))} {f1(X(54))} {f1(Y(38))} {f1(X(56))} {f1(Y(43))}Z', '#5a7a98', ' fill-opacity="0.8"')
    d.c(X(36), Y(48), 1.5 * s, '#e8eef2'); d.c(X(36.3), Y(48), 0.9 * s, '#0a0a0a'); d.c(X(35.9), Y(47.6), 0.3 * s, '#ffffff')
for cx, cy, s in ((22, 22, 0.42), (46, 16, 0.38), (70, 24, 0.44), (34, 40, 0.48), (62, 44, 0.5), (86, 42, 0.4), (24, 62, 0.46), (50, 66, 0.52), (78, 66, 0.46), (40, 86, 0.4), (66, 86, 0.44)):
    small_fish(cx, cy, s)
F['fish_school'] = d.svg()

# ============================================================ SEAHORSE (Hippocampus)
d = D(0)
C = '#e0a030'
# bakfena (ryggfena) bakom kroppen
d.p('M58 44C68 42 74 52 68 64C64 60 60 56 58 56Z', d.g([(0, '#f0c060'), (1, '#f7e0a8')], 58, 0, 74, 0), ' fill-opacity="0.8"')
for i in range(5):
    d.line(f'M{59+i*0.6} {46+i*2.4}L{66+i*1.2} {47+i*3}', sh(C, -0.4), 0.45, 0.4)
# kropp: nos, huvud, hals, buk, svans (kurvor tecknade som en sluten bana)
BODY = ('M22 23C21 21 23 19.5 25.5 20L40 22.5C42 17 48 13 54 14C61 15 65 22 64 30C63.5 36 60 41 58 47'
        'C56 53 60 58 60 64C60 72 56 78 50 82C45 85 40 88 38 94C37 96 34.5 96 34 94C33 88 36 83 40 79C45 75 50 72 50 66'
        'C50 60 46 55 46 48C46 42 48 36 46 32C45 29 42 27 39 27.5L25.5 25.5C23 25.5 22.5 24.5 22 23Z')
cb = d.clip(BODY)
d.p(BODY, d.g([(0, sh(C, -0.4)), (0.2, sh(C, 0.1)), (0.45, sh(C, 0.45)), (0.7, C), (1, sh(C, -0.55))], 30, 0, 66, 0))
d.open(cb)
d.soft('M48 16C58 16 64 24 62 34C58 24 52 20 48 16Z', '#ffffff', 0.35)
d.soft('M40 30C46 40 46 56 54 68C48 70 44 60 40 50Z', '#6a3a00', 0.3)
# kroppsringar (hudplattor)
for i, (x1, y1, x2, y2) in enumerate(((46, 34, 63, 32), (46, 40, 61, 40), (46, 46, 58, 48), (46, 52, 58, 54), (48, 58, 60, 60), (50, 64, 60, 66), (49, 70, 58, 72), (46, 76, 54, 78), (42, 81, 50, 83), (38, 86, 46, 88), (36, 90, 42, 92))):
    d.line(f'M{x1} {y1}Q{(x1+x2)/2} {(y1+y2)/2+1.5} {x2} {y2}', '#7a4400', 0.6, 0.45)
    d.line(f'M{x1} {y1-1}Q{(x1+x2)/2} {(y1+y2)/2+0.5} {x2} {y2-1}', '#ffffff', 0.5, 0.35)
# knölar längs ryggen och mottling
for x, y in ((63, 26), (62.5, 33), (60.5, 40), (58.5, 46), (59, 54), (60, 60), (59, 68), (55, 76)):
    d.c(x, y, 1.2, sh(C, 0.35), ' fill-opacity="0.8"')
for _ in range(26):
    d.c(random.uniform(40, 62), random.uniform(20, 88), random.uniform(0.4, 1.0), '#8a4a00', ' fill-opacity="0.25"')
d.close()
# krona
d.p('M48 14.5C50 10 54 9 57 11C55 13 53 14 52 15.5Z', d.g([(0, sh(C, 0.2)), (1, sh(C, -0.4))], 48, 0, 57, 0))
# nosöppning, öga, bröstfena
d.line('M22 23L25 23.2', '#5a2a00', 0.9, 0.7)
d.eye(50, 24, 2.7, '#0a0a0a', '#f7e0a8', 0.3)
d.p('M60 34C64 32 66 36 63 40C61 38 60 36 60 34Z', '#f7e0a8', ' fill-opacity="0.75"')
F['seahorse'] = d.svg()

# ============================================================ PUFFERFISH (uppblåst blåsfisk)
d = D(-4)
BODY = 'M14 50C14 32 30 20 48 20C68 20 82 34 82 50C82 66 68 78 48 78C30 78 14 68 14 50Z'
cb = d.clip(BODY)
# taggar runt kroppen (del av djuret)
for a in range(0, 360, 11):
    if 60 < a < 120: continue           # buken slät nertill
    x0, y0 = polar(48, 49, 29.5, a); x1, y1 = polar(48, 49, 33.5 + (a * 7 % 3), a)
    d.line(f'M{f1(x0)} {f1(y0)}L{f1(x1)} {f1(y1)}', '#c9b07a' if 180 < a < 360 or a < 20 else '#e8d8b0', 1.1, 0.95, 'round')
    d.line(f'M{f1(x0)} {f1(y0)}L{f1(x1)} {f1(y1)}', '#6a5020', 0.4, 0.5, 'round')
# stjärt och fenor
fin(d, 'M80 44C86 40 92 36 96 36C94 42 94 58 96 64C92 64 86 60 80 56Z', '#c9a84a', '#efe2b4', ((80, 0, 96, 0), ['M82 46L92 40', 'M83 50L94 50', 'M82 54L92 60']), op=0.85)
fin(d, 'M52 20C56 10 64 8 68 14C62 14 58 17 54 21Z', '#c9a84a', '#efe2b4', ((0, 8, 0, 21), ['M56 18L60 12', 'M60 17L64 13']), op=0.85)
fin(d, 'M58 76C62 86 70 88 72 82C66 82 62 79 58 76Z', '#c9a84a', '#efe2b4', ((0, 76, 0, 88), ['M62 78L64 84']), op=0.85)
d.p(BODY, d.rg([(0, '#f3e6c6'), (0.45, '#d9c07a'), (0.8, '#a8843a'), (1, '#6a5020')], 40, 40, 44, 36, 34))
d.open(cb)
d.p('M14 54C24 66 40 76 60 76C72 76 80 66 82 56C70 70 50 72 30 66Z', d.g([(0, '#fbf6ea'), (1, '#e8dcc0')], 0, 54, 0, 78))   # ljus buk
d.soft('M16 52C30 60 50 64 78 56C60 68 30 66 16 56Z', '#8a6a30', 0.25)
for cx, cy, r in ((36, 30, 2.6), (48, 26, 2.2), (60, 30, 2.8), (30, 40, 2.0), (42, 38, 2.4), (56, 40, 2.0), (68, 40, 2.4), (72, 50, 2.0), (26, 52, 1.8), (50, 50, 2.4), (62, 52, 1.8), (36, 48, 1.6)):
    d.c(cx, cy, r, '#5a3a14', ' fill-opacity="0.75"')
    d.c(cx - r * 0.3, cy - r * 0.3, r * 0.45, '#7a5424', ' fill-opacity="0.6"')
d.close()
fin(d, 'M40 56C48 54 56 60 50 68C44 66 40 62 40 56Z', '#d9c07a', '#efe2b4', ((40, 0, 56, 0), ['M43 58L50 64']), op=0.7)
d.eye(26, 40, 5, '#0a0a0a', '#e8c070', 0.35)
d.line('M14 50C16 52 20 53 24 52', '#5a3a14', 0.9, 0.6)                    # mun
d.p('M14.5 49.5C16 50.5 19 51 22 50.5L22 52C19 52.5 16 52 14.5 51Z', '#f6efdc')   # näbbtand
F['pufferfish'] = d.svg()

# ============================================================ ANGLERFISH (djuphavsmarulk)
d = D(-5)
BODY = 'M12 56C10 44 22 32 40 30C56 28 70 36 74 50C76 58 72 68 62 72C48 76 26 74 16 66C13 63 12 60 12 56Z'
cb = d.clip(BODY)
# stjärt och fenor (trasiga, halvgenomskinliga)
fin(d, 'M72 52C80 46 88 44 96 46C90 52 90 62 94 70C86 68 78 62 70 60Z', '#3a2a30', '#6a4a56', ((72, 0, 96, 0), ['M76 52L90 48', 'M78 56L92 58', 'M76 60L90 66']), op=0.85)
fin(d, 'M40 31C44 18 54 14 62 20C56 22 50 26 46 32Z', '#3a2a30', '#6a4a56', ((0, 14, 0, 32), ['M46 28L50 20', 'M52 26L56 20']), op=0.85)
fin(d, 'M44 74C46 84 54 88 60 84C54 82 50 78 48 74Z', '#3a2a30', '#6a4a56', ((0, 74, 0, 88), ['M50 76L52 84']), op=0.85)
d.p(BODY, d.rg([(0, '#6a4e58'), (0.4, '#3d2b36'), (0.8, '#1e141c'), (1, '#120a10')], 40, 42, 44, 34, 36))
d.open(cb)
d.soft('M24 36C40 28 60 32 70 44C56 36 36 36 24 42Z', '#b08aa0', 0.22)
d.soft('M14 60C30 72 56 76 72 64C60 80 30 80 14 66Z', '#000000', 0.5)
for _ in range(40):
    d.c(random.uniform(16, 72), random.uniform(32, 72), random.uniform(0.3, 0.8), '#c8a0b8', ' fill-opacity="0.18"')
d.close()
# gapet med tänder (underkäken skjuter fram)
d.p('M12 54C18 58 30 61 44 60C38 66 24 66 14 62Z', d.g([(0, '#2a0a14'), (1, '#4a1a28')], 0, 54, 0, 66))
for x, l in ((18, 5), (22, 7), (26, 5), (30, 8), (34, 6), (38, 7), (42, 5)):
    d.p(f'M{x} 54.5L{x+0.9} {54.5+l}L{x+1.8} 54.5Z', d.g([(0, '#f7f2e8'), (1, '#c8bca8')], 0, 54, 0, 62))
for x, l in ((20, 4), (25, 6), (30, 4), (35, 5), (40, 4)):
    d.p(f'M{x} 63L{x+0.8} {63-l}L{x+1.6} 63Z', '#efe8da')
d.p('M12 56C16 52 24 50 34 50C30 53 20 55 14 58Z', d.g([(0, '#1e141c'), (1, '#4a3040')], 0, 50, 0, 58))   # överkäke
d.eye(30, 42, 3, '#102030', '#9fb8c8', 0.4)
# lysspröt
d.line('M36 30C32 20 24 14 18 16', '#5a4050', 1.1, 0.9)
d.c(17, 17, 4.5, d.rg([(0, '#eaffff', 0.55), (1, '#8ae0ff', 0)], 17, 17, 4.5))
d.c(17, 17, 2.4, d.rg([(0, '#ffffff'), (0.5, '#c8f4ff'), (1, '#4ab8e8')], 16.4, 16.4, 2.6))
F['anglerfish'] = d.svg()

# ============================================================ REEF SHARK (gråhaj)
d = D(-10)
BODY = 'M5 51C9 44 22 38 40 36C56 34 70 38 80 44L84 50L80 55C70 61 56 65 40 64C22 63 9 59 5 51Z'
cb = d.clip(BODY)
TOP = [(0, '#3a4855'), (0.3, '#6d7e8b'), (0.52, '#9aa8b3'), (0.68, '#d5dce1'), (1, '#f6f8f9')]
# ryggfena, andra ryggfena, bukfenor bakom kroppen
d.p('M42 37C46 26 54 21 60 23C57 29 56 34 60 38Z', d.g(TOP[:3] + [(1, '#9aa8b2')], 0, 21, 0, 38))
d.p('M66 40C68 35 72 33 74 34C72 37 72 40 74 42Z', d.g([(0, '#6d7e8b'), (1, '#43525f')], 0, 33, 0, 42))
d.p('M58 62C60 68 64 70 66 68C63 66 63 63 64 60Z', '#c6d0d7')
d.p('M64 60C66 66 70 67 72 65C69 63 69 61 70 58Z', '#8d9ca7')
# stjärtfena (övre lob längre)
d.p('M78 46C84 38 90 28 97 18C95 30 92 40 91 47L84 50L90 53C91 58 92 63 94 68C89 63 84 58 78 54Z', d.g([(0, '#3e4d5a'), (0.5, '#6d7e8b'), (1, '#9aa8b3')], 0, 18, 0, 68))
d.line('M84 44C88 38 92 30 95 24', '#2a3640', 0.5, 0.35); d.line('M85 54C88 58 90 62 92 66', '#2a3640', 0.5, 0.35)
d.p(BODY, d.g(TOP, 0, 36, 0, 64))
d.open(cb)
d.soft('M8 52C24 56 50 58 80 52C60 62 24 62 8 56Z', '#ffffff', 0.5)
d.soft('M10 46C24 40 50 38 78 44C60 46 30 48 10 52Z', '#1e2a34', 0.25)
for x in (28, 31, 34, 37, 40):
    d.line(f'M{x} 46C{x-0.6} 49 {x-0.6} 52 {x} 55', '#2a3640', 0.6, 0.55)      # gälspringor
d.close()
d.p('M30 56C28 66 24 72 20 76C26 68 28 62 29 57Z', d.g([(0, '#8d9ca7'), (1, '#e8edf0')], 20, 0, 32, 0))     # bröstfena
d.line('M5 51C9 54 14 55 20 55', '#2a3640', 0.8, 0.5)                                            # mun
d.eye(17, 46, 1.9, '#0a0a0a', '#c8d0d6', 0.3)
d.c(10, 48, 0.6, '#2a3640', ' fill-opacity="0.6"')                                                # näsborre
F['reef_shark'] = d.svg()

# ============================================================ MANTA RAY (ovanifrån)
d = D(-22)
BODY = 'M6 48C18 32 38 24 50 24C62 24 82 32 94 48C80 52 66 56 58 62L54 66L50 70L46 66L42 62C34 56 20 52 6 48Z'
cb = d.clip(BODY)
d.line('M50 68C52 78 56 86 62 96', '#2a333c', 1.3, 0.9)                                         # svans
d.p(BODY, d.g([(0, '#0f161c'), (0.35, '#2a3640'), (0.55, '#45535f'), (0.75, '#2a3640'), (1, '#0f161c')], 6, 0, 94, 0))
d.open(cb)
d.soft('M30 30C40 26 60 26 70 30C62 36 38 36 30 30Z', '#8a98a4', 0.35)
d.p('M34 29C40 27 45 28 48 32C44 36 38 38 32 34Z', '#d8dfe4', ' fill-opacity="0.85"')             # vita skulderfläckar
d.p('M66 29C60 27 55 28 52 32C56 36 62 38 68 34Z', '#d8dfe4', ' fill-opacity="0.85"')
d.soft('M8 48C24 50 40 56 48 66C36 60 20 56 8 52Z', '#000000', 0.45)
d.soft('M92 48C76 50 60 56 52 66C64 60 80 56 92 52Z', '#000000', 0.45)
d.line('M50 30C50 40 50 50 50 64', '#6a7884', 0.8, 0.35)
d.close()
# huvudflikar (cephaliska fenor)
d.p('M43 26C40 18 41 12 44 8C46 14 47 20 50 26Z', d.g([(0, '#1a232b'), (1, '#45535f')], 40, 0, 50, 0))
d.p('M57 26C60 18 59 12 56 8C54 14 53 20 50 26Z', d.g([(0, '#45535f'), (1, '#1a232b')], 50, 0, 60, 0))
d.c(45, 28, 1.2, '#0a0a0a'); d.c(55, 28, 1.2, '#0a0a0a')
F['manta_ray'] = d.svg()

# ============================================================ SEA TURTLE (grön havssköldpadda, ovanifrån)
d = D(-14)
SK = '#5a6a2e'
# fenor och huvud under skölden
def flipper(path, g):
    d.p(path, g)
FL = [(0, '#8a9448'), (0.4, '#6f7a3a'), (1, '#3e4820')]
d.p('M30 44C22 40 10 32 4 18C3 14 7 12 11 14C20 18 30 28 40 34Z', d.g(FL, 4, 0, 40, 0))
d.p('M70 44C78 40 90 32 96 18C97 14 93 12 89 14C80 18 70 28 60 34Z', d.g(FL, 96, 0, 60, 0))
d.p('M36 74C30 80 22 88 14 90C12 88 16 82 22 78C28 74 32 70 38 68Z', d.g(FL, 14, 0, 38, 0))
d.p('M64 74C70 80 78 88 86 90C88 88 84 82 78 78C72 74 68 70 62 68Z', d.g(FL, 86, 0, 62, 0))
for pth in ('M8 18C16 22 26 30 34 36', 'M92 18C84 22 74 30 66 36', 'M16 88C22 82 28 76 34 72', 'M84 88C78 82 72 76 66 72'):
    d.line(pth, '#2a3010', 0.6, 0.35)
for cx, cy in ((12, 20), (18, 24), (24, 28), (30, 32), (88, 20), (82, 24), (76, 28), (70, 32), (20, 84), (26, 78), (80, 84), (74, 78)):
    d.c(cx, cy, 1.3, '#9aa450', ' fill-opacity="0.45"')
for px, py in ((8, 12), (92, 12), (21, 85), (79, 85)):
    pass
d.e(50, 20, 8, 9, d.rg([(0, '#8a9448'), (0.6, '#5f6a2e'), (1, '#3a4418')], 47, 16, 10))
d.c(45, 18, 1.4, '#0a0a0a'); d.c(55, 18, 1.4, '#0a0a0a'); d.c(44.6, 17.6, 0.5, '#ffffff'); d.c(54.6, 17.6, 0.5, '#ffffff')
d.line('M46 25C48 26 52 26 54 25', '#2a3010', 0.6, 0.6)
# hud: små fjäll
for px, py in ((12, 18), (18, 24), (24, 28), (82, 24), (88, 18), (76, 28), (26, 78), (74, 78)):
    d.c(px, py, 1.1, '#8a9448', ' fill-opacity="0.5"')
# sköld
SHELL = 'M50 26C66 26 76 38 76 54C76 70 66 80 50 80C34 80 24 70 24 54C24 38 34 26 50 26Z'
cs = d.clip(SHELL)
d.p(SHELL, d.rg([(0, '#9a7a3a'), (0.5, '#6a5a24'), (1, '#3a3010')], 44, 44, 36, 40, 40))
d.open(cs)
# plattor: mittrad + sidor
def scute(path, c):
    d.p(path, d.g([(0, sh(c, 0.3)), (0.5, c), (1, sh(c, -0.4))], 36, 30, 64, 76))
    d.line(path, '#2a2008', 0.9, 0.7)
    d.line(path, '#d8c080', 0.35, 0.35)
scute('M44 29L56 29L58 38L50 40L42 38Z', '#8a6a2a')
scute('M42 38L50 40L58 38L60 50L50 52L40 50Z', '#7a5a22')
scute('M40 50L50 52L60 50L60 62L50 64L40 62Z', '#8a6a2a')
scute('M40 62L50 64L60 62L58 74L50 76L42 74Z', '#7a5a22')
scute('M30 36L44 29L42 38L40 50L28 48Z', '#6a4a1a')
scute('M28 48L40 50L40 62L28 62Z', '#7a5a22')
scute('M28 62L40 62L42 74L32 76Z', '#6a4a1a')
scute('M70 36L56 29L58 38L60 50L72 48Z', '#6a4a1a')
scute('M72 48L60 50L60 62L72 62Z', '#7a5a22')
scute('M72 62L60 62L58 74L68 76Z', '#6a4a1a')
d.soft('M30 34C40 28 60 28 70 34C60 32 40 32 30 38Z', '#ffffff', 0.3)
d.soft('M26 60C34 76 66 76 74 60C66 82 34 82 26 66Z', '#000000', 0.4)
d.close()
d.line(SHELL, '#c8b070', 0.6, 0.35)
F['sea_turtle'] = d.svg()

# ============================================================ OCTOPUS
d = D(0)
OC = '#a84e2c'
def arm(p0, p1, p2, p3, w0, w1=0.8, suck=True):
    d.p(tapered(p0, p1, p2, p3, w0, w1), d.g([(0, sh(OC, -0.1)), (1, sh(OC, -0.45))], p0[0], p0[1], p3[0], p3[1]))
    if suck:
        for i in range(2, 13):
            t = i / 14
            x, y = bez(p0, p1, p2, p3, t)
            r = (w0 * (1 - t) + w1 * t) * 0.22
            d.c(x, y, r, '#f0d8c0', ' fill-opacity="0.75"')
arms = [((38, 48), (20, 50), (8, 66), (10, 86), 9), ((44, 50), (30, 62), (18, 78), (28, 92), 8.5), ((50, 52), (46, 66), (40, 82), (46, 96), 8),
        ((56, 52), (58, 68), (66, 80), (80, 90), 8), ((62, 50), (74, 60), (86, 72), (94, 86), 8.5), ((64, 46), (80, 44), (92, 56), (90, 72), 8),
        ((42, 50), (36, 72), (54, 78), (64, 70), 7), ((60, 50), (72, 50), (80, 36), (72, 30), 7)]
for a in arms[6:]:
    arm(*a[:4], a[4], 0.8, suck=False)
for a in arms[:6]:
    arm(*a[:4], a[4])
# mantel (huvud)
HEAD = 'M30 42C26 24 36 10 50 10C64 10 74 24 70 42C68 50 60 54 50 54C40 54 32 50 30 42Z'
ch = d.clip(HEAD)
d.p(HEAD, d.rg([(0, sh(OC, 0.35)), (0.45, OC), (0.8, sh(OC, -0.35)), (1, sh(OC, -0.6))], 44, 26, 30, 40, 22))
d.open(ch)
for _ in range(60):
    x, y = random.uniform(28, 72), random.uniform(10, 54)
    d.c(x, y, random.uniform(0.5, 1.6), sh(OC, -0.4) if random.random() < 0.5 else sh(OC, 0.25), ' fill-opacity="0.3"')
d.soft('M34 48C44 56 56 56 66 48C58 60 42 60 34 52Z', '#000000', 0.4)
d.close()
d.eye(36, 40, 3.4, '#3a2a10', '#e8c070', 0.4); d.eye(64, 40, 3.4, '#3a2a10', '#e8c070', 0.4)
d.e(36, 40, 2.0, 0.7, '#0a0a0a'); d.e(64, 40, 2.0, 0.7, '#0a0a0a')                    # horisontella pupiller
F['octopus'] = d.svg()

# ============================================================ JELLYFISH (manet)
d = D(-8)
# tentakler och munarmar först (hänger under)
for i, (x0, dx) in enumerate(((22, -6), (28, -2), (34, -4), (40, 2), (46, -3), (54, 3), (60, -2), (66, 4), (72, 2), (78, 6))):
    d.line(f'M{x0} 50C{x0+dx} 62 {x0-dx} 76 {x0+dx*1.5} {88+i%3*3}', '#d9b8e8', 0.7, 0.55)
for x0, dx in ((36, -4), (44, 2), (56, -2), (64, 4)):
    d.p(tapered((x0, 52), (x0 + dx * 2, 64), (x0 - dx * 2, 76), (x0 + dx * 3, 86), 4.5, 1.2), d.g([(0, '#f0c8e8', 0.85), (1, '#e8a8d8', 0.4)], 0, 52, 0, 86))
    d.line(f'M{x0-1} 54C{x0+dx*2-1} 64 {x0-dx*2-1} 76 {x0+dx*3-1} 85', '#ffffff', 0.4, 0.4)
# klocka
BELL = 'M16 46C16 24 32 12 50 12C68 12 84 24 84 46C74 51 62 54 50 54C38 54 26 51 16 46Z'
cb = d.clip(BELL)
d.p(BELL, d.rg([(0, '#ffffff', 0.55), (0.45, '#e8d0f4', 0.5), (0.8, '#c8a0e0', 0.55), (1, '#9a70c8', 0.75)], 44, 30, 38, 40, 24))
d.open(cb)
d.e(50, 42, 20, 6, '#b890d8', extra=' fill-opacity="0.45"')
for cx, cy in ((42, 32), (58, 32), (42, 42), (58, 42)):
    d.e(cx, cy, 5.5, 4, d.rg([(0, '#ff9ad0', 0.85), (1, '#d060a0', 0.6)], cx - 1, cy - 1, 6))
d.soft('M24 24C34 14 60 12 76 24C60 20 40 20 24 30Z', '#ffffff', 0.6)
d.close()
d.line('M20 44C30 50 70 50 80 44', '#ffffff', 1.3, 0.75)
d.line('M16 46C26 51 38 54 50 54C62 54 74 51 84 46', '#8a60b8', 1.0, 0.5)
d.spec('M28 22C36 16 44 14 50 14', 1.4, 0.8, True)
F['jellyfish'] = d.svg()

# ============================================================ STARFISH (sjöstjärna)
d = D(12)
def star_path(cx, cy, R, r, n=5, rot=-90):
    pts = []
    for i in range(n):
        a0 = rot + i * 360 / n; a1 = a0 + 180 / n
        pts.append((polar(cx, cy, R, a0), polar(cx, cy, r, a1)))
    d0 = f'M{f1(pts[0][0][0])} {f1(pts[0][0][1])}'
    for i in range(n):
        tip = pts[i][0]; val = pts[i][1]; nxt = pts[(i + 1) % n][0]
        # tip -> val -> next tip med mjuka kurvor
        c1 = polar(cx, cy, R * 0.55, rot + i * 360 / n + 10); c2 = polar(cx, cy, r * 1.05, rot + i * 360 / n + 180 / n - 14)
        c3 = polar(cx, cy, r * 1.05, rot + i * 360 / n + 180 / n + 14); c4 = polar(cx, cy, R * 0.55, rot + (i + 1) * 360 / n - 10)
        d0 += f'C{f1(c1[0])} {f1(c1[1])} {f1(c2[0])} {f1(c2[1])} {f1(val[0])} {f1(val[1])}C{f1(c3[0])} {f1(c3[1])} {f1(c4[0])} {f1(c4[1])} {f1(nxt[0])} {f1(nxt[1])}'
    return d0 + 'Z'
SP = star_path(50, 52, 44, 15)
cs = d.clip(SP)
SC = '#e06a2a'
d.p(SP, d.rg([(0, sh(SC, 0.3)), (0.4, SC), (0.8, sh(SC, -0.3)), (1, sh(SC, -0.55))], 46, 46, 44, 44, 40))
d.open(cs)
for i in range(5):
    a = -90 + i * 72
    for k in range(1, 9):
        rr = 8 + k * 4.3
        x, y = polar(50, 52, rr, a)
        rad = 2.1 - k * 0.17
        d.c(x, y, rad, sh(SC, 0.4), ' fill-opacity="0.75"')
        d.c(x - rad * 0.3, y - rad * 0.3, rad * 0.45, '#ffffff', ' fill-opacity="0.5"')
        for s in (-1, 1):
            xx, yy = polar(50, 52, rr - 1, a + s * (16 - k * 1.5))
            if k < 7: d.c(xx, yy, rad * 0.6, sh(SC, 0.25), ' fill-opacity="0.6"')
    x, y = polar(50, 52, 24, a)
    d.soft(f'M{f1(x-6)} {f1(y)}L{f1(x+6)} {f1(y)}L{f1(x+1)} {f1(y+10)}Z', '#000000', 0.2)
for _ in range(80):
    a, rr = random.uniform(0, 360), random.uniform(2, 36)
    x, y = polar(50, 52, rr, a)
    d.c(x, y, random.uniform(0.3, 0.8), sh(SC, -0.5), ' fill-opacity="0.3"')
d.close()
d.c(50, 52, 3.5, d.rg([(0, sh(SC, 0.4)), (1, sh(SC, -0.2))], 49, 51, 4))
F['starfish'] = d.svg()

# ============================================================ CRAB (strandkrabba/krabbtaska, ovanifrån)
d = D(-6)
CC = '#b8451c'
def seg(p0, p1, p2, p3, w0, w1):
    d.p(tapered(p0, p1, p2, p3, w0, w1), d.g([(0, sh(CC, 0.1)), (0.5, sh(CC, -0.2)), (1, sh(CC, -0.5))], 0, min(p0[1], p3[1]) - 2, 0, max(p0[1], p3[1]) + 6))
# ben: fyra par
for s in (-1, 1):
    X = lambda x: 50 + s * (x - 50)
    seg((X(28), 48), (X(16), 44), (X(8), 40), (X(4), 30), 4.5, 1.6)
    seg((X(28), 54), (X(16), 56), (X(8), 58), (X(4), 66), 4.5, 1.6)
    seg((X(30), 60), (X(20), 66), (X(14), 74), (X(12), 84), 4.2, 1.5)
    seg((X(36), 64), (X(32), 74), (X(28), 82), (X(26), 92), 3.8, 1.4)
    # klo: arm + två fingrar
    seg((X(34), 42), (X(26), 36), (X(20), 30), (X(18), 22), 6, 5)
    d.p(f'M{f1(X(18))} 26C{f1(X(12))} 24 {f1(X(8))} 18 {f1(X(6))} 10C{f1(X(10))} 12 {f1(X(14))} 16 {f1(X(18))} 20Z', d.g([(0, sh(CC, -0.4)), (1, sh(CC, 0.1))], X(6), 0, X(18), 0))   # rörligt finger
    d.p(f'M{f1(X(18))} 20C{f1(X(16))} 14 {f1(X(18))} 8 {f1(X(22))} 4C{f1(X(22))} 10 {f1(X(22))} 16 {f1(X(21))} 22Z', d.g([(0, sh(CC, 0.3)), (1, sh(CC, -0.3))], X(16), 0, X(23), 0))   # fast finger
    d.p(f'M{f1(X(13))} 20C{f1(X(10))} 24 {f1(X(14))} 28 {f1(X(20))} 26C{f1(X(23))} 24 {f1(X(23))} 18 {f1(X(20))} 16Z', d.rg([(0, sh(CC, 0.35)), (0.6, CC), (1, sh(CC, -0.45))], X(16), 21, 6))   # klons hand
    d.c(X(21), 14, 0.6, '#f0d8c0', ' fill-opacity="0.7"')
# ryggskölden
CAR = 'M24 50C22 38 34 28 50 28C66 28 78 38 76 50C75 59 66 68 50 68C34 68 25 59 24 50Z'
cc = d.clip(CAR)
d.p(CAR, d.rg([(0, sh(CC, 0.45)), (0.4, sh(CC, 0.1)), (0.8, sh(CC, -0.3)), (1, sh(CC, -0.6))], 44, 42, 32, 40, 36))
d.open(cc)
for _ in range(90):
    x, y = random.uniform(24, 76), random.uniform(28, 68)
    d.c(x, y, random.uniform(0.3, 1.1), '#5a1a08' if random.random() < 0.6 else '#f0c080', ' fill-opacity="0.3"')
d.soft('M26 58C36 70 64 70 74 58C66 76 34 76 26 62Z', '#000000', 0.45)
d.line('M34 44C42 40 58 40 66 44', '#6a2008', 1.0, 0.4)
d.line('M30 56C40 52 60 52 70 56', '#6a2008', 0.8, 0.3)
d.close()
# sågtandad framkant
for x in (28, 33, 38):
    d.p(f'M{x} {40-(x-28)*0.7}l2.5 -3l2.5 3Z', sh(CC, 0.2)); d.p(f'M{100-x} {40-(x-28)*0.7}l-2.5 -3l-2.5 3Z', sh(CC, 0.2))
# ögon på skaft
for ex in (44, 56):
    d.line(f'M{ex} 30L{ex} 25', sh(CC, -0.3), 1.6, 1)
    d.c(ex, 24, 2, d.rg([(0, '#5a4a40'), (0.6, '#1a1210'), (1, '#000000')], ex - 0.6, 23.4, 2))
    d.c(ex - 0.6, 23.4, 0.6, '#ffffff', ' fill-opacity="0.8"')
F['crab'] = d.svg()

# ============================================================ LOBSTER (hummer, ovanifrån)
d = D(-8)
LC = '#1f2f62'
LG = [(0, sh(LC, 0.5)), (0.3, sh(LC, 0.15)), (0.6, LC), (1, sh(LC, -0.5))]
def lseg(p0, p1, p2, p3, w0, w1):
    d.p(tapered(p0, p1, p2, p3, w0, w1), d.g(LG, p0[0] - 3, 0, p0[0] + 3, 0) if abs(p3[0] - p0[0]) < 6 else d.g(LG, 0, min(p0[1], p3[1]) - 2, 0, max(p0[1], p3[1]) + 4))
# antenner
for s in (-1, 1):
    X = lambda x: 50 + s * (x - 50)
    d.line(f'M{f1(X(46))} 22C{f1(X(40))} 14 {f1(X(34))} 6 {f1(X(28))} 1', '#8a4a2a', 1.1, 0.9)
    d.line(f'M{f1(X(47))} 24C{f1(X(44))} 20 {f1(X(42))} 16 {f1(X(40))} 14', '#8a4a2a', 0.7, 0.8)
# ben
for s in (-1, 1):
    X = lambda x: 50 + s * (x - 50)
    lseg((X(42), 36), (X(32), 36), (X(26), 42), (X(22), 50), 3.2, 1.2)
    lseg((X(42), 42), (X(32), 44), (X(26), 50), (X(24), 58), 3.0, 1.2)
    lseg((X(42), 48), (X(34), 52), (X(30), 58), (X(30), 64), 2.8, 1.1)
    lseg((X(43), 54), (X(38), 60), (X(36), 66), (X(36), 70), 2.6, 1.0)
    # klo-armar och klor
    lseg((X(42), 34), (X(34), 34), (X(28), 32), (X(24), 28), 5.5, 5)
    claw = f'M{f1(X(26))} 32C{f1(X(16))} 34 {f1(X(6))} 26 {f1(X(4))} 12C{f1(X(12))} 12 {f1(X(22))} 16 {f1(X(30))} 18C{f1(X(34))} 22 {f1(X(34))} 30 {f1(X(26))} 32Z'
    d.p(claw, d.rg([(0, sh(LC, 0.6)), (0.5, sh(LC, 0.1)), (1, sh(LC, -0.5))], X(18), 24, 16))
    d.p(f'M{f1(X(20))} 16C{f1(X(18))} 10 {f1(X(22))} 4 {f1(X(30))} 2C{f1(X(30))} 10 {f1(X(32))} 16 {f1(X(30))} 18Z', d.g([(0, sh(LC, 0.4)), (1, sh(LC, -0.3))], X(18), 0, X(32), 0))
    d.line(f'M{f1(X(6))} 14C{f1(X(12))} 20 {f1(X(20))} 24 {f1(X(26))} 28', '#c86a2a', 0.6, 0.5)
    d.line(f'M{f1(X(5))} 13L{f1(X(20))} 16', '#e8c8a0', 0.7, 0.5)
    for k in range(4):
        d.c(X(8 + k * 4), 15 + k * 1.2, 0.7, '#e8c8a0', ' fill-opacity="0.6"')
# ryggsköld
CAR = 'M38 24C40 16 46 12 50 12C54 12 60 16 62 24L63 48C62 52 58 56 50 56C42 56 38 52 37 48Z'
cl = d.clip(CAR)
d.p(CAR, d.g([(0, sh(LC, -0.3)), (0.25, sh(LC, 0.35)), (0.5, sh(LC, 0.6)), (0.75, sh(LC, 0.1)), (1, sh(LC, -0.5))], 36, 0, 64, 0))
d.open(cl)
for _ in range(70):
    d.c(random.uniform(38, 62), random.uniform(13, 56), random.uniform(0.3, 1.0), '#d87a30' if random.random() < 0.5 else '#eadcc8', ' fill-opacity="0.35"')
d.line('M38 40C44 38 56 38 62 40', '#0a1030', 0.9, 0.6)
d.soft('M38 46C44 56 56 56 62 46C58 60 42 60 38 50Z', '#000000', 0.4)
d.close()
d.p('M48 12L50 6L52 12Z', sh(LC, 0.3))   # rostrum
d.c(45, 18, 1.5, '#0a0a0a'); d.c(55, 18, 1.5, '#0a0a0a')
# stjärtsegment
for i in range(6):
    y0 = 56 + i * 5.4; w = 13 - i * 0.9
    seg_p = f'M{f1(50-w)} {f1(y0)}C{f1(50-w-1)} {f1(y0+3)} {f1(50-w)} {f1(y0+6)} {f1(50-w+1.2)} {f1(y0+6.4)}L{f1(50+w-1.2)} {f1(y0+6.4)}C{f1(50+w)} {f1(y0+6)} {f1(50+w+1)} {f1(y0+3)} {f1(50+w)} {f1(y0)}Z'
    d.p(seg_p, d.g([(0, sh(LC, -0.3)), (0.3, sh(LC, 0.4)), (0.5, sh(LC, 0.55)), (0.75, sh(LC, 0.05)), (1, sh(LC, -0.5))], 50 - w, 0, 50 + w, 0))
    d.line(f'M{f1(50-w+1)} {f1(y0+0.6)}L{f1(50+w-1)} {f1(y0+0.6)}', '#ffffff', 0.5, 0.3)
    d.dark(f'M{f1(50-w+1)} {f1(y0+6)}L{f1(50+w-1)} {f1(y0+6)}', 1.0, 0.4)
    d.c(random.uniform(42, 58), y0 + 3, 0.6, '#d87a30', ' fill-opacity="0.5"')
# stjärtfjäder (fem flikar)
for k, (dx, w) in enumerate(((-8, 5), (-4, 5), (0, 5.5), (4, 5), (8, 5))):
    d.p(f'M{f1(50+dx-w/2)} 88C{f1(50+dx-w/2)} 94 {f1(50+dx)} 98 {f1(50+dx)} 98C{f1(50+dx)} 98 {f1(50+dx+w/2)} 94 {f1(50+dx+w/2)} 88Z', d.g([(0, sh(LC, 0.4)), (1, '#b8602a')], 0, 88, 0, 98))
    d.line(f'M{f1(50+dx-w/2+1)} 90C{f1(50+dx-w/2+1)} 93 {f1(50+dx)} 95 {f1(50+dx)} 96', '#ffffff', 0.4, 0.3)
F['lobster'] = d.svg()

# ============================================================ SHRIMP (räka, sidovy: huvudsköld + böjd bakkropp i ett)
d = D(0)
SC2 = '#e3a08a'
SG = [(0, sh(SC2, -0.3)), (0.2, sh(SC2, 0.3)), (0.45, sh(SC2, 0.55)), (0.75, SC2), (1, sh(SC2, -0.45))]
P0, P1, P2, P3 = (40, 40), (64, 36), (80, 52), (74, 76)
# antenner och ben först (ligger bakom)
d.line('M16 36C10 28 8 16 10 4', '#c88070', 0.9, 0.8)
d.line('M18 34C16 24 20 12 28 6', '#c88070', 0.7, 0.8)
d.line('M14 44C10 48 6 56 4 66', '#c88070', 0.6, 0.6)
for x, y in ((22, 56), (27, 58), (32, 60), (37, 61), (42, 62)):
    d.p(tapered((x, y), (x - 2, y + 5), (x - 4, y + 9), (x - 6, y + 13), 1.6, 0.6), '#d89080')
for t in (0.3, 0.45, 0.6, 0.75):
    x, y = bez(P0, P1, P2, P3, t)
    d.p(tapered((x, y + 5), (x - 2, y + 10), (x - 5, y + 13), (x - 7, y + 15), 3.6, 1.2), '#e8b0a0', ' fill-opacity="0.75"')
# bakkropp: avsmalnande böjd kropp
AB = tapered(P0, P1, P2, P3, 18, 8, 30)
cab = d.clip(AB)
d.p(AB, d.g(SG, 0, 28, 0, 62), ' fill-opacity="0.97"')
d.open(cab)
d.soft('M44 32C60 26 76 36 82 50C72 40 60 34 44 36Z', '#ffffff', 0.4)
d.soft('M48 50C62 54 78 64 80 80C74 68 62 58 48 54Z', '#7a3020', 0.35)
# segmentgränser: tvärs över kroppen, varje segment skjuter över nästa
for t in (0.17, 0.32, 0.47, 0.62, 0.76, 0.9):
    x, y = bez(P0, P1, P2, P3, t)
    xa, ya = bez(P0, P1, P2, P3, t - 0.01); xb, yb = bez(P0, P1, P2, P3, t + 0.01)
    dx, dy = xb - xa, yb - ya; l = math.hypot(dx, dy); nx, ny = -dy / l, dx / l
    w = (18 + (8 - 18) * t) * 0.55
    seg_l = f'M{f1(x+nx*w)} {f1(y+ny*w)}Q{f1(x+dx/l*2.5)} {f1(y+dy/l*2.5)} {f1(x-nx*w)} {f1(y-ny*w)}'
    d.dark(seg_l, 1.3, 0.4)
    d.line(f'M{f1(x+nx*w+dx/l*1.4)} {f1(y+ny*w+dy/l*1.4)}Q{f1(x+dx/l*3.9)} {f1(y+dy/l*3.9)} {f1(x-nx*w+dx/l*1.4)} {f1(y-ny*w+dy/l*1.4)}', '#ffffff', 0.6, 0.5)
    d.line(seg_l, '#b85a48', 0.5, 0.3)
d.close()
# stjärtfjäder
for pth in ('M74 76C82 74 90 78 94 86C88 82 80 82 74 84Z', 'M72 78C76 84 78 90 76 96C72 92 68 88 66 82Z', 'M68 78C74 80 80 86 82 94C76 90 70 86 66 84Z'):
    d.p(pth, d.g([(0, sh(SC2, -0.1)), (1, '#f4d4c8')], 66, 76, 94, 96), ' fill-opacity="0.9"')
    d.line(pth.split('C')[0] + 'C' + pth.split('C')[1], '#ffffff', 0.4, 0.3)
# huvudsköld (carapax) med rostrum, ligger över första segmentet
CAR = 'M12 40C12 30 22 24 34 25C46 26 52 36 50 48C48 58 36 62 26 60C16 58 12 50 12 40Z'
cc = d.clip(CAR)
d.p(CAR, d.rg([(0, sh(SC2, 0.55)), (0.5, SC2), (0.85, sh(SC2, -0.3)), (1, sh(SC2, -0.5))], 28, 36, 24, 24, 32), ' fill-opacity="0.97"')
d.open(cc)
d.soft('M14 50C24 60 40 60 50 50C42 64 22 64 14 54Z', '#7a3020', 0.4)
for k in range(5):
    d.line(f'M{18+k*6} 30C{18+k*6-2} 40 {18+k*6-3} 50 {18+k*6-2} 58', '#c87060', 0.5, 0.2)
d.close()
d.line('M24 25C30 23 40 24 48 32', '#ffffff', 0.8, 0.5)
d.p('M18 30C14 24 8 18 2 14C8 15 14 20 22 28Z', d.g([(0, sh(SC2, 0.3)), (1, sh(SC2, -0.3))], 2, 0, 22, 0))   # rostrum
for k in range(4):
    d.p(f'M{8+k*3} {18+k*2.6}l-0.6 -2.2l2.2 1.4Z', sh(SC2, -0.2))
d.eye(18, 36, 2.4, '#0a0a0a', '#8a4a40', 0.25)
F['shrimp'] = d.svg()

# ============================================================ SCALLOP (kammussla)
d = D(0)
SHELLC = '#d9825f'
HX, HY = 50, 86
FAN = 'M38 84L62 84L74 70C78 60 78 44 72 32C66 20 58 14 50 14C42 14 34 20 28 32C22 44 22 60 26 70Z'
cf = d.clip(FAN)
d.p(FAN, d.rg([(0, sh(SHELLC, 0.5)), (0.5, SHELLC), (0.85, sh(SHELLC, -0.3)), (1, sh(SHELLC, -0.55))], 44, 40, 48, 42, 30))
d.open(cf)
for i in range(16):
    a = -90 - 62 + i * 124 / 15
    x1, y1 = polar(HX, HY, 80, a)
    ang = a
    # ås: ljus sida vänster, mörk sida höger
    x0, y0 = HX, HY
    xl, yl = polar(HX, HY, 80, a - 1.9); xr, yr = polar(HX, HY, 80, a + 1.9)
    d.p(f'M{f1(x0)} {f1(y0)}L{f1(xl)} {f1(yl)}L{f1(x1)} {f1(y1)}Z', '#ffffff', ' fill-opacity="0.35"')
    d.p(f'M{f1(x0)} {f1(y0)}L{f1(x1)} {f1(y1)}L{f1(xr)} {f1(yr)}Z', '#5a2010', ' fill-opacity="0.35"')
for rr in (18, 28, 38, 48, 58, 66):
    d.line(f'M{f1(HX-rr*0.9)} {f1(HY-rr*0.45)}A{rr} {rr} 0 0 1 {f1(HX+rr*0.9)} {f1(HY-rr*0.45)}', '#7a3018', 0.55, 0.4)
d.soft('M28 30C36 18 64 18 72 30C64 30 36 30 28 36Z', '#ffffff', 0.4)
d.soft('M26 72C38 84 62 84 74 72C62 90 38 90 26 78Z', '#000000', 0.4)
d.close()
# öron och skalkant
d.p('M38 84L30 84C28 84 28 88 30 88L62 88C64 88 64 84 62 84L38 84Z', d.g([(0, sh(SHELLC, 0.2)), (1, sh(SHELLC, -0.4))], 0, 84, 0, 88))
d.line('M30 85H62', '#ffffff', 0.5, 0.4)
F['scallop'] = d.svg()

# ============================================================ MUSSEL (blåmussla)
d = D(-32)
MC = '#1b2440'
BODY = 'M50 8C58 8 66 20 68 40C70 60 66 80 56 92C52 96 44 94 40 88C34 76 30 56 32 36C34 20 42 8 50 8Z'
cm = d.clip(BODY)
d.p(BODY, d.g([(0, '#0e1326'), (0.25, '#2a3a6a'), (0.45, '#6a86b8'), (0.6, '#3a4a7a'), (0.8, '#15203c'), (1, '#070a14')], 30, 0, 70, 0))
d.open(cm)
# tillväxtlinjer från umbo (toppen)
for k in range(1, 12):
    r = 8 + k * 7.2
    d.line(f'M{f1(50-18*k/11)} {f1(8+r*0.92)}Q50 {f1(8+r*1.02)} {f1(50+18*k/11)} {f1(8+r*0.92)}', '#8aa0c8' if k % 2 else '#050810', 0.5, 0.35)
d.soft('M48 12C44 30 42 56 44 84C40 60 40 36 46 12Z', '#b0c8ff', 0.35)
d.soft('M58 20C66 40 68 64 60 88C70 64 70 40 58 20Z', '#000000', 0.5)
d.p('M62 30C66 44 66 58 64 70', '#ffffff', ' fill-opacity="0"')
d.close()
d.spec('M46 14C42 30 41 50 43 72', 1.2, 0.5, True)
d.line('M50 8C54 10 58 16 61 24', '#c8a070', 0.9, 0.5)                      # periostracum-kanten vid umbo
F['mussel'] = d.svg()

# ============================================================ CONCH (snäcka: konisk spira, kroppsvarv, rosa läpp)
d = D(-18)
CO = '#e8c9a0'
# spira (kon) med sömmar mellan varven
SP = 'M49 6C56 14 66 28 72 44L28 44C34 28 42 14 49 6Z'
cs = d.clip(SP)
d.p(SP, d.g([(0, sh(CO, -0.4)), (0.25, sh(CO, 0.15)), (0.5, sh(CO, 0.5)), (0.75, CO), (1, sh(CO, -0.5))], 28, 0, 72, 0))
d.open(cs)
for k, y in enumerate((14, 22, 31, 40)):
    hw = 4 + k * 5.5
    d.p(f'M{f1(49-hw)} {y}Q49 {y+4} {f1(49+hw)} {y}L{f1(49+hw+1)} {y+1}Q49 {y+6} {f1(49-hw-1)} {y+1}Z', '#000000', ' fill-opacity="0.3"')
    d.line(f'M{f1(49-hw)} {y}Q49 {y+4} {f1(49+hw)} {y}', '#ffffff', 0.6, 0.5)
    for i in range(k + 2):
        x = 49 - hw + (i + 0.5) * 2 * hw / (k + 2)
        d.p(f'M{f1(x-1.4)} {y}L{f1(x)} {y-2.6}L{f1(x+1.4)} {y}Z', sh(CO, 0.3))
d.close()
# kroppsvarv
BODY = 'M28 44C22 54 22 72 32 86C40 96 56 98 66 90C74 84 76 70 74 56C73 50 72 46 72 44Z'
cb = d.clip(BODY)
d.p(BODY, d.rg([(0, sh(CO, 0.45)), (0.45, CO), (0.8, sh(CO, -0.3)), (1, sh(CO, -0.6))], 44, 58, 36, 40, 54))
d.open(cb)
for _ in range(16):
    x, y = random.uniform(28, 72), random.uniform(46, 90)
    d.line(f'M{f1(x)} {f1(y)}C{f1(x+2)} {f1(y+4)} {f1(x-1)} {f1(y+8)} {f1(x+1)} {f1(y+12)}', '#9a6a3a', random.uniform(0.6, 1.6), 0.3)
for k in range(7):
    d.line(f'M26 {52+k*6}C40 {50+k*6} 60 {50+k*6} 76 {54+k*6}', '#7a4a20', 0.5, 0.22)
d.soft('M28 46C40 40 64 40 72 48C60 46 40 48 28 54Z', '#ffffff', 0.4)
d.soft('M30 84C40 94 58 96 68 88C56 100 36 98 30 90Z', '#000000', 0.4)
d.close()
# knölar på skuldran (sista varvet)
for k in range(6):
    x = 31 + k * 8
    d.p(f'M{f1(x-2.6)} 45C{f1(x-1.2)} 40 {f1(x+1.2)} 40 {f1(x+2.6)} 45Z', d.g([(0, sh(CO, 0.4)), (1, sh(CO, -0.4))], x - 2.6, 0, x + 2.6, 0))
# utbredd ytterläpp och mynning (höger sida)
d.p('M72 48C80 52 84 66 80 84C78 90 70 94 64 92C68 84 70 70 68 56C68 52 70 48 72 48Z', d.g([(0, sh(CO, 0.3)), (0.5, '#f0c8c0'), (1, sh(CO, -0.4))], 64, 0, 84, 0))
d.p('M66 54C70 60 72 74 68 88C64 90 62 88 62 84C64 74 64 62 62 54C62 50 64 50 66 54Z', d.g([(0, '#f7c5cc'), (0.35, '#f29bb0'), (0.7, '#c85a7a'), (1, '#5a1a30')], 60, 0, 70, 0))
d.spec('M75 52C80 62 80 76 77 86', 1.0, 0.6, True)
F['conch'] = d.svg()

# ============================================================ PEARL OYSTER (öppen pärlmussla)
d = D(-8)
# övre skal (utsida, rest upp), grov yta
UP = 'M20 42C18 24 32 10 50 10C68 10 82 24 80 42C72 38 60 36 50 36C40 36 28 38 20 42Z'
cu = d.clip(UP)
d.p(UP, d.g([(0, '#6a5a44'), (0.3, '#9a8a70'), (0.6, '#6c5c48'), (1, '#3a3024')], 0, 10, 0, 42))
d.open(cu)
for k in range(1, 9):
    r = k * 4
    d.line(f'M{f1(50-r*1.9)} {f1(42-r*0.3)}Q50 {f1(44-r*2.2)} {f1(50+r*1.9)} {f1(42-r*0.3)}', '#2a2018' if k % 2 else '#c8b898', 0.9, 0.4)
for _ in range(50):
    d.c(random.uniform(22, 78), random.uniform(12, 40), random.uniform(0.3, 1.2), '#2a2018' if random.random() < 0.5 else '#d8c8a8', ' fill-opacity="0.35"')
d.close()
# undre skal: insidan med pärlemor
LOW = 'M18 44C22 40 36 38 50 38C64 38 78 40 82 44C84 60 70 78 50 80C30 78 16 60 18 44Z'
cl = d.clip(LOW)
d.p(LOW, d.g([(0, '#f7f3ec'), (0.2, '#e4e0f0'), (0.4, '#f6e8e2'), (0.6, '#dfeee8'), (0.8, '#f3eef6'), (1, '#c8c0c8')], 20, 44, 80, 80))
d.open(cl)
d.soft('M20 46C34 40 66 40 80 46C68 56 32 56 20 50Z', '#8a7a9a', 0.35)
d.soft('M22 58C34 74 66 74 78 58C70 84 30 84 22 64Z', '#000000', 0.25)
for k in range(5):
    d.line(f'M{22+k*2} {46+k*7}C{40} {48+k*7} {60} {48+k*7} {78-k*2} {46+k*7}', '#b8a8c8', 0.6, 0.25)
d.close()
d.line('M18 44C22 40 36 38 50 38C64 38 78 40 82 44', '#5a4a3a', 1.4, 0.7)         # skalkanten vid gångjärnet
# pärlan
d.c(50, 58, 9, d.rg([(0, '#ffffff'), (0.5, '#f4f0ea'), (0.8, '#d8d2cc'), (1, '#9a9490')], 47, 55, 10))
d.c(46.5, 54.5, 2.6, '#ffffff', ' fill-opacity="0.9"')
d.e(52, 64, 5, 1.6, '#f0c8d8', extra=' fill-opacity="0.35"')
F['pearl_oyster'] = d.svg()

# ============================================================ SEA URCHIN (sjöborre)
d = D(0)
UC = '#3b1a5a'
for a in range(0, 360, 6):
    L = 36 + (a * 13 % 7) - 3
    x0, y0 = polar(50, 50, 20, a); x1, y1 = polar(50, 50, L, a + (a % 12 - 6) * 0.25)
    d.line(f'M{f1(x0)} {f1(y0)}L{f1(x1)} {f1(y1)}', sh(UC, -0.2), 1.4, 0.95, 'round')
    d.line(f'M{f1(x0)} {f1(y0)}L{f1(x1)} {f1(y1)}', sh(UC, 0.45) if 180 < a < 330 else sh(UC, 0.15), 0.5, 0.6, 'round')
d.c(50, 50, 24, d.rg([(0, sh(UC, 0.4)), (0.5, UC), (0.85, sh(UC, -0.4)), (1, sh(UC, -0.7))], 42, 42, 26))
for a in range(0, 360, 30):
    for rr in (6, 12, 18):
        x, y = polar(50, 50, rr, a + rr)
        d.c(x, y, 1.1, sh(UC, 0.6), ' fill-opacity="0.85"'); d.c(x - 0.3, y - 0.3, 0.4, '#ffffff', ' fill-opacity="0.6"')
F['sea_urchin'] = d.svg()

# ============================================================ SEA ANEMONE (havsanemon)
d = D(0)
AC = '#c86a4a'
TC = '#e8a8a0'
# bakre tentakler
def tent(x0, y0, x3, y3, w, col, op=1):
    mx, my = (x0 + x3) / 2 + random.uniform(-6, 6), (y0 + y3) / 2 - 6
    d.p(tapered((x0, y0), (x0 + (mx - x0) * 0.6, y0 - 8), (mx, my), (x3, y3), w, w * 0.45), d.g([(0, sh(col, -0.1)), (0.6, col), (1, '#f4d8c8')], 0, y3, 0, y0), f' fill-opacity="{op}"')
random.seed(11)
for i in range(16):
    a = 200 + i * 8.75
    x3, y3 = polar(50, 46, 42 + random.uniform(-4, 6), a)
    tent(50 + (a - 270) * 0.22, 46, x3, max(4, y3), 4.2, sh(TC, -0.25), 0.9)
# fot/kolonn
COL = 'M30 96C30 80 34 60 36 48C40 46 60 46 64 48C66 60 70 80 70 96Z'
cc = d.clip(COL)
d.p(COL, d.g([(0, sh(AC, -0.45)), (0.2, sh(AC, 0.1)), (0.42, sh(AC, 0.4)), (0.7, AC), (1, sh(AC, -0.55))], 30, 0, 70, 0))
d.open(cc)
for k in range(9):
    d.line(f'M{34+k*0.3} {52+k*5}C44 {53+k*5} 56 {53+k*5} {66-k*0.3} {52+k*5}', '#7a3020', 0.5, 0.25)
for x in range(32, 70, 4):
    d.line(f'M{x} 50C{x-1} 66 {x+1} 82 {x} 96', '#7a3020', 0.6, 0.18)
d.close()
# munskiva
d.e(50, 47, 16, 5, d.rg([(0, sh(AC, 0.5)), (0.7, AC), (1, sh(AC, -0.3))], 48, 46, 16))
d.e(50, 47.5, 5, 1.8, '#5a1a10', extra=' fill-opacity="0.8"')
# främre tentakler
for i in range(22):
    a = 190 + i * 7.5 + random.uniform(-2, 2)
    L = 30 + random.uniform(-4, 8)
    x3, y3 = polar(50, 46, L, a)
    tent(50 + (a - 272) * 0.18, 47, x3, max(10, y3 + 4), 4.6, TC, 0.97)
F['sea_anemone'] = d.svg()

# ============================================================ CORAL (staghorn, förgrenad – tillåtet flertal)
d = D(0)
KC = '#e3785a'
random.seed(5)
def branch(p0, ang, L, w, depth):
    a = math.radians(ang)
    p3 = (p0[0] + math.cos(a) * L, p0[1] + math.sin(a) * L)
    bend = random.uniform(-14, 14)
    p1 = (p0[0] + math.cos(a + math.radians(bend)) * L * 0.33, p0[1] + math.sin(a + math.radians(bend)) * L * 0.33)
    p2 = (p0[0] + math.cos(a - math.radians(bend)) * L * 0.66, p0[1] + math.sin(a - math.radians(bend)) * L * 0.66)
    d.p(tapered(p0, p1, p2, p3, w, w * 0.6), d.g([(0, sh(KC, -0.45)), (0.3, sh(KC, 0.05)), (0.5, sh(KC, 0.45)), (0.75, KC), (1, sh(KC, -0.4))], p0[0] - w, p0[1], p0[0] + w, p0[1]) if abs(math.cos(a)) < 0.6 else d.g([(0, sh(KC, 0.4)), (0.6, KC), (1, sh(KC, -0.45))], 0, p0[1] - w, 0, p0[1] + w))
    # porer
    for i in range(3, int(L / 2.6)):
        t = i * 2.6 / L
        x, y = bez(p0, p1, p2, p3, t)
        d.c(x + random.uniform(-w * 0.3, w * 0.3), y, 0.35, '#7a2a18', ' fill-opacity="0.45"')
    d.c(p3[0], p3[1], w * 0.32, '#f8d8c8', ' fill-opacity="0.9"')   # ljus tillväxtspets
    if depth > 0:
        n = 2 if depth > 1 else random.choice((1, 2))
        for k in range(n):
            branch(bez(p0, p1, p2, p3, random.uniform(0.55, 0.95)), ang + random.choice((-1, 1)) * random.uniform(18, 40), L * random.uniform(0.55, 0.75), w * 0.72, depth - 1)
branch((50, 96), -90, 30, 9, 0)
branch((50, 70), -116, 26, 7.5, 2)
branch((50, 68), -64, 26, 7.5, 2)
branch((50, 66), -90, 26, 7, 2)
F['coral'] = d.svg()

# ============================================================ KELP (tång – tillåtet flertal blad)
d = D(0)
random.seed(3)
G1, G2 = '#6a6a22', '#a88a3a'
def blade(p0, p1, p2, p3, w):
    # vågig kant: två sidor med egen vågrörelse
    n = 26; L, R = [], []
    for i in range(n + 1):
        t = i / n
        x, y = bez(p0, p1, p2, p3, t)
        e = 1e-3
        xa, ya = bez(p0, p1, p2, p3, max(0, t - e)); xb, yb = bez(p0, p1, p2, p3, min(1, t + e))
        dx, dy = xb - xa, yb - ya; l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        ww = w * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * (1 + 0.28 * math.sin(t * 22 + 1))
        ww2 = w * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * (1 + 0.28 * math.sin(t * 22 + 3.5))
        L.append((x + nx * ww / 2, y + ny * ww / 2)); R.append((x - nx * ww2 / 2, y - ny * ww2 / 2))
    path = 'M' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in L) + ' L' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in reversed(R)) + 'Z'
    d.p(path, d.g([(0, sh(G1, -0.35)), (0.3, G2), (0.5, sh(G2, 0.25)), (0.7, G1), (1, sh(G1, -0.5))], min(p0[0], p3[0]) - 4, 0, max(p0[0], p3[0]) + 4, 0))
    mid = 'M' + ' L'.join(f'{f1((a[0]+b[0])/2)} {f1((a[1]+b[1])/2)}' for a, b in zip(L[1:-1], R[1:-1]))
    d.line(mid, '#4a4a14', 0.7, 0.45)
    for i in range(3, n - 2, 3):
        x, y = (L[i][0] + R[i][0]) / 2, (L[i][1] + R[i][1]) / 2
        d.line(f'M{f1(x)} {f1(y)}L{f1(L[i+1][0])} {f1(L[i+1][1])}M{f1(x)} {f1(y)}L{f1(R[i+1][0])} {f1(R[i+1][1])}', '#4a4a14', 0.35, 0.3)
# stipe (stam)
d.p(tapered((50, 98), (48, 80), (52, 60), (50, 40), 3.2, 1.6), d.g([(0, '#4a4a14'), (0.4, '#8a7a30'), (1, '#3a3a10')], 47, 0, 53, 0))
blade((50, 46), (40, 36), (26, 30), (12, 14), 12)
blade((50, 40), (54, 28), (56, 16), (52, 4), 11)
blade((50, 52), (62, 44), (78, 36), (92, 22), 12)
blade((50, 66), (40, 58), (30, 52), (20, 44), 9)
blade((50, 74), (60, 68), (72, 64), (84, 58), 9)
# flytblåsor vid bladbaserna
for x, y in ((50, 46), (50, 40), (50, 52), (50, 66), (50, 74)):
    d.e(x, y, 2.6, 2.0, d.rg([(0, '#d8c070'), (0.6, '#a88a3a'), (1, '#5a4a14')], x - 0.8, y - 0.6, 3))
F['kelp'] = d.svg()

# ============================================================ SEAGRASS (sjögräs – tillåtet flertal blad)
d = D(0)
random.seed(9)
def gblade(x0, x3, h, w, c):
    p0, p1, p2, p3 = (x0, 96), (x0 + (x3 - x0) * 0.1, 96 - h * 0.4), (x0 + (x3 - x0) * 0.6, 96 - h * 0.75), (x3, 96 - h)
    d.p(tapered(p0, p1, p2, p3, w, w * 0.45), d.g([(0, sh(c, -0.4)), (0.3, sh(c, 0.15)), (0.5, sh(c, 0.4)), (0.75, c), (1, sh(c, -0.5))], min(x0, x3) - 3, 0, max(x0, x3) + 3, 0))
    pts = [bez(p0, p1, p2, p3, i / 12) for i in range(1, 12)]
    d.line('M' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in pts), sh(c, -0.5), 0.5, 0.4)
    d.line('M' + ' L'.join(f'{f1(x-w*0.22)} {f1(y)}' for x, y in pts[1:-2]), '#ffffff', 0.4, 0.3)
for x0, x3, h, w, c in ((50, 30, 88, 5.5, '#4e8a2e'), (48, 64, 92, 5, '#3f7a26'), (52, 44, 80, 4.6, '#5a9a38'), (46, 18, 70, 4.4, '#447e2a'), (54, 80, 76, 4.6, '#4a8a30'), (50, 56, 60, 4, '#5f9e3c'), (49, 36, 52, 3.8, '#3a7024')):
    gblade(x0, x3, h, w, c)
# fäste
d.e(50, 95, 8, 3, d.g([(0, '#2a4a14'), (0.5, '#4a6a24'), (1, '#1a3010')], 0, 92, 0, 98))
F['seagrass'] = d.svg()

# ============================================================ BUBBLE (en luftbubbla)
d = D(0)
d.c(50, 50, 32, d.rg([(0, '#ffffff', 0.04), (0.7, '#cfe8ff', 0.12), (0.9, '#9fd0ff', 0.35), (1, '#e8f6ff', 0.85)], 50, 50, 32))
d.line('M50 18A32 32 0 1 1 18 50', '#ffffff', 1.0, 0.25)
d.e(38, 36, 7.5, 5, d.rg([(0, '#ffffff', 0.95), (1, '#ffffff', 0)], 38, 36, 7.5), -40)
d.e(62, 68, 6, 2.6, d.rg([(0, '#ffffff', 0.55), (1, '#ffffff', 0)], 62, 68, 6), -40)
d.line('M24 62A28 28 0 0 0 58 78', '#ffffff', 1.6, 0.5, blur=True)
d.line('M34 24A26 26 0 0 1 56 22', '#ffffff', 2.2, 0.85, blur=True)
F['bubble'] = d.svg()

# ============================================================ SAND DOLLAR
d = D(0)
DC = '#d9cdb0'
d.c(50, 50, 36, d.rg([(0, sh(DC, 0.3)), (0.55, DC), (0.88, sh(DC, -0.2)), (1, sh(DC, -0.5))], 44, 44, 38))
d.c(50, 50, 36, d.rg([(0, '#000000', 0), (0.8, '#000000', 0), (1, '#000000', 0.25)], 50, 50, 36))
# fem blomblad av porer
for i in range(5):
    a = -90 + i * 72
    pa = math.radians(a)
    tipx, tipy = polar(50, 50, 24, a)
    for s in (-1, 1):
        pts = []
        for k in range(1, 9):
            r = 4 + k * 2.6
            w = 3.2 * math.sin(math.pi * k / 9.5)
            x, y = polar(50, 50, r, a + s * math.degrees(math.atan2(w, r)))
            pts.append((x, y))
            d.c(x, y, 0.42, '#6a5a3a', ' fill-opacity="0.75"')
        d.line('M' + ' L'.join(f'{f1(x)} {f1(y)}' for x, y in pts), '#8a7a58', 0.35, 0.5)
    d.line(f'M50 50L{f1(tipx)} {f1(tipy)}', '#b8a888', 0.5, 0.45)
    hx, hy = polar(50, 50, 14, a + 36)
    d.e(hx, hy, 1.4, 0.7, '#6a5a3a', a + 36 + 90, ' fill-opacity="0.6"')     # lunula (springa)
# central stjärna (apikala plattor)
for i in range(5):
    x, y = polar(50, 50, 2.4, -90 + i * 72)
    d.c(x, y, 0.55, '#7a6a48', ' fill-opacity="0.8"')
for _ in range(120):
    a, rr = random.uniform(0, 360), random.uniform(0, 35)
    x, y = polar(50, 50, rr, a)
    d.c(x, y, random.uniform(0.2, 0.5), '#8a7a58' if random.random() < 0.5 else '#ffffff', ' fill-opacity="0.22"')
F['sand_dollar'] = d.svg()

# ============================================================ TREASURE CHEST (ekkista med mässingsbeslag)
d = D(-10)
WD = '#8a5a2a'
WOOD = [(0, sh(WD, -0.35)), (0.2, sh(WD, 0.25)), (0.4, WD), (0.7, sh(WD, -0.15)), (0.9, sh(WD, -0.5)), (1, sh(WD, -0.3))]
BR = [(0, '#8a6a2a'), (0.2, '#e9cf86'), (0.4, '#f7e9b8'), (0.65, '#c9a24c'), (1, '#6e4f14')]
# låda
BOX = 'M14 50H86V88C86 90 84 92 82 92H18C16 92 14 90 14 88Z'
d.p(BOX, d.g(WOOD, 0, 50, 0, 92))
cbx = d.clip(BOX)
d.open(cbx)
for y in (58, 66, 74, 82):
    d.line(f'M14 {y}C30 {y+0.6} 60 {y-0.6} 86 {y}', '#3a2008', 0.9, 0.55)
    d.line(f'M14 {y+1}C30 {y+1.6} 60 {y+0.4} 86 {y+1}', '#d8a060', 0.5, 0.35)
for x, y in ((24, 54), (48, 62), (70, 70), (34, 78), (60, 86)):
    d.line(f'M{x} {y}C{x+6} {y+0.4} {x+12} {y-0.2} {x+18} {y+0.2}', '#3a2008', 0.4, 0.4)
d.soft('M14 84C40 90 60 90 86 84L86 92L14 92Z', '#000000', 0.5)
d.close()
# lock (välvt)
LID = 'M14 50C14 36 30 28 50 28C70 28 86 36 86 50Z'
d.p(LID, d.g([(0, sh(WD, -0.45)), (0.3, sh(WD, 0.3)), (0.55, sh(WD, 0.05)), (0.8, sh(WD, -0.3)), (1, sh(WD, -0.6))], 14, 0, 86, 0))
cl = d.clip(LID)
d.open(cl)
for k in range(1, 6):
    y = 50 - k * 4
    d.line(f'M14 50C24 {y+2} 40 {y-6+k} 50 {y-6+k}C60 {y-6+k} 76 {y+2} 86 50', '#3a2008', 0.7, 0.4)
d.soft('M30 32C40 28 60 28 70 32C60 36 40 36 30 36Z', '#ffffff', 0.3)
d.close()
d.dark('M14 50.5H86', 1.6, 0.6)
# mässingsband (två vertikala) över lock och låda
for x in (30, 70):
    d.p(f'M{x-3.5} 92V50C{x-3.5} 36 {x-2} 30 {x} 29C{x+2} 30 {x+3.5} 36 {x+3.5} 50V92Z', d.g(BR, x - 3.5, 0, x + 3.5, 0))
    for y in (34, 44, 54, 66, 78, 88):
        d.c(x, y, 0.9, d.rg([(0, '#fff6d8'), (0.6, '#c9a24c'), (1, '#6e4f14')], x - 0.3, y - 0.3, 1))
# kantbeslag
d.p('M14 50H86V53H14Z', d.g(BR, 0, 50, 0, 53))
d.p('M14 88H86V92H14Z', d.g(BR, 0, 88, 0, 92))
# låsplåt och hänglås
d.p('M43 50H57V62C57 63.5 56 64.5 54.5 64.5H45.5C44 64.5 43 63.5 43 62Z', d.g(BR, 43, 0, 57, 0))
d.p('M46 44C46 38 54 38 54 44V50H52V44.5C52 40.5 48 40.5 48 44.5V50H46Z', d.g([(0, '#5a5a60'), (0.4, '#c8ccd2'), (1, '#3a3a40')], 46, 0, 54, 0))
d.c(50, 56, 1.6, '#2a1a08'); d.p('M49.3 56.5H50.7V60H49.3Z', '#2a1a08')
d.spec('M44 51V63', 0.6, 0.6)
F['treasure_chest'] = d.svg()

for n, s in F.items():
    with open(os.path.join(OUT, n + '.svg'), 'w', encoding='utf-8') as fh:
        fh.write(s)
print(len(F), 'prylar ->', OUT)
