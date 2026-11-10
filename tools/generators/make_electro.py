# Historik: det här skriptet ritade de inbyggda prylarna i props/. SVG-filerna i props/ är källan nu.
# Kör inte rakt av, eftersom det skriver över befintliga filer. Använd det som mall för nya prylar i samma stil.
# Användning: python tools/generators/make_electro.py <utmapp>
"""Electro category for Kalejdo -> <repo>/props/electro/<name>.svg"""
import math, os, sys

OUT = os.path.join(sys.argv[1], "props", "electro")
P = {}
FONT = 'font-family="Arial,Helvetica,sans-serif"'


def add(name, body, defs=""):
    d = f"<defs>{defs}</defs>" if defs else ""
    P[name] = ('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
               f"{d}{body}</svg>\n")


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


# ---------------------------------------------------------------- shared gradients
def lin(id_, stops, x2=0, y2=1):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"{f" stop-opacity={chr(34)}{a}{chr(34)}" if a is not None else ""}/>' for o, c, a in stops)
    return f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def cyl(id_, light, mid, dark, horizontal_axis=True):
    """Cylinder shading. horizontal_axis=True -> shading varies top/bottom."""
    st = [(0, dark, None), (.22, light, None), (.5, mid, None), (.85, dark, None), (1, dark, None)]
    return lin(id_, st, 0, 1) if horizontal_axis else lin(id_, st, 1, 0)


SILVER = cyl("ag", "#ffffff", "#c9ced6", "#7d858f")
SILVER_V = cyl("agv", "#ffffff", "#c9ced6", "#7d858f", False)
COPPER_V = cyl("cu", "#ffd9b0", "#d9823c", "#7a3a10", False)
COPPER_H = cyl("cuh", "#ffd9b0", "#d9823c", "#7a3a10", True)
GLOSS = lin("gl", [(0, "#fff", .55), (.45, "#fff", 0), (1, "#000", .25)])


def lead(x1, y1, x2, y2, w=3.2):
    return (f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#7d858f" stroke-width="{w + 1.4}" stroke-linecap="round"/>'
            f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#d6dbe1" stroke-width="{w}" stroke-linecap="round"/>')


def leadp(d, w=3.2):
    return (f'<path d="{d}" fill="none" stroke="#7d858f" stroke-width="{w + 1.4}" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" fill="none" stroke="#d6dbe1" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"/>')


# ---------------------------------------------------------------- resistors
DOGBONE = ("M30 37C23 37 21 41 21 50C21 59 23 63 30 63C35 63 37 59 41 59H59C63 59 65 63 70 63"
           "C77 63 79 59 79 50C79 41 77 37 70 37C65 37 63 41 59 41H41C37 41 35 37 30 37Z")
BAND_COL = {"black": "#1a1a1a", "brown": "#7a3f12", "red": "#d91c1c", "orange": "#ff7a00", "yellow": "#ffd400",
            "green": "#1f9e3a", "blue": "#1f5fe0", "violet": "#8a2be2", "grey": "#8a8a8a", "white": "#f4f4f4",
            "gold": "#d4a017", "silver": "#c0c4ca"}


def resistor(name, body, bands, xs):
    defs = (f'<clipPath id="c"><path d="{DOGBONE}"/></clipPath>' + GLOSS)
    b = "".join(f'<rect x="{x}" y="30" width="5" height="40" fill="{BAND_COL[c]}"/>' for c, x in zip(bands, xs))
    add(name, lead(3, 50, 24, 50) + lead(76, 50, 97, 50)
        + f'<path d="{DOGBONE}" fill="{body}"/><g clip-path="url(#c)">{b}<rect x="0" y="30" width="100" height="40" fill="url(#gl)"/></g>'
        f'<path d="{DOGBONE}" fill="none" stroke="#00000055" stroke-width="1.5"/>'
        '<path d="M27 41C30 40 33 40 36 42" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width="2" stroke-linecap="round"/>', defs)


resistor("resistor_4k7", "#e8cf9c", ["yellow", "violet", "red", "gold"], [28, 42, 51, 67])
resistor("resistor_220", "#e8cf9c", ["red", "red", "brown", "gold"], [28, 42, 51, 67])
resistor("resistor_10k_metal", "#5c9be0", ["brown", "black", "black", "red", "brown"], [27, 37, 45, 53, 68])

# ---------------------------------------------------------------- capacitors
add("electrolytic_cap",
    lead(42, 76, 42, 97) + lead(58, 76, 58, 90)
    + '<rect x="27" y="12" width="46" height="66" rx="7" fill="url(#can)"/>'
    '<rect x="57" y="12" width="12" height="66" fill="#c9d3e6" fill-opacity=".85"/>'
    + "".join(f'<rect x="60" y="{y}" width="6" height="2.4" fill="#1b2f6b"/>' for y in (24, 38, 52, 66))
    + '<rect x="27" y="12" width="46" height="66" rx="7" fill="url(#gl2)"/>'
    '<ellipse cx="50" cy="15" rx="22" ry="4.5" fill="url(#top)" stroke="#5a6570" stroke-width="1"/>'
    '<path d="M42 15H58M50 12V18" stroke="#5a6570" stroke-width="1.3"/>'
    '<path d="M27 72H73" stroke="#0d1d4a" stroke-width="1.5" stroke-opacity=".6"/>'
    f'<text x="40" y="50" text-anchor="middle" {FONT} font-weight="700" font-size="8" fill="#e8eefc" transform="rotate(-90 40 50)">470µF 25V</text>',
    lin("can", [(0, "#0f2a6b", None), (.2, "#5c8cf0", None), (.45, "#2a56c9", None), (.9, "#0f2a6b", None), (1, "#0a1d4d", None)], 1, 0)
    + lin("gl2", [(0, "#fff", 0), (.25, "#fff", .35), (.35, "#fff", 0), (1, "#000", 0)], 1, 0)
    + '<radialGradient id="top" cx=".4" cy=".4" r=".7"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#9aa2ad"/></radialGradient>')
add("ceramic_cap",
    leadp("M42 56L40 74L40 97") + leadp("M58 56L60 74L60 97")
    + '<ellipse cx="50" cy="38" rx="30" ry="28" fill="url(#cer)" stroke="#8a4a10" stroke-width="2"/>'
    '<ellipse cx="42" cy="28" rx="12" ry="7" fill="#fff" fill-opacity=".35" transform="rotate(-20 42 28)"/>'
    f'<text x="50" y="45" text-anchor="middle" {FONT} font-weight="700" font-size="15" fill="#5a2a00">104</text>',
    '<radialGradient id="cer" cx=".38" cy=".35" r=".75"><stop offset="0" stop-color="#ffcf7a"/><stop offset=".6" stop-color="#e88a1e"/><stop offset="1" stop-color="#a8560a"/></radialGradient>')
add("tantalum_cap",
    lead(43, 70, 43, 97) + lead(57, 70, 57, 97)
    + '<path d="M50 8C66 8 74 22 74 40C74 60 64 74 50 74C36 74 26 60 26 40C26 22 34 8 50 8Z" fill="url(#ta)" stroke="#a37800" stroke-width="2"/>'
    '<path d="M36 22C40 16 46 14 52 14" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".7"/>'
    '<path d="M60 26V36M55 31H65" stroke="#7a4a00" stroke-width="3"/>'
    f'<text x="50" y="56" text-anchor="middle" {FONT} font-weight="700" font-size="10" fill="#7a4a00">10µ</text>',
    '<radialGradient id="ta" cx=".38" cy=".3" r=".8"><stop offset="0" stop-color="#fff2a6"/><stop offset=".55" stop-color="#f2c21a"/><stop offset="1" stop-color="#b38300"/></radialGradient>')
add("film_cap",
    lead(36, 74, 36, 97) + lead(64, 74, 64, 97)
    + '<rect x="16" y="20" width="68" height="56" rx="6" fill="url(#fc)" stroke="#7a0010" stroke-width="2"/>'
    '<rect x="16" y="20" width="68" height="16" rx="6" fill="#fff" fill-opacity=".18"/>'
    f'<text x="50" y="48" text-anchor="middle" {FONT} font-weight="700" font-size="12" fill="#fff">0.1µF</text>'
    f'<text x="50" y="63" text-anchor="middle" {FONT} font-size="9" fill="#ffd6d6">104J 630V</text>',
    lin("fc", [(0, "#ff5b5b", None), (.5, "#d61c2a", None), (1, "#8a0010", None)]))

# ---------------------------------------------------------------- coils
tor = ""
for i in range(28):
    a = i * 360 / 28
    x1, y1 = polar(50, 50, 16, a)
    x2, y2 = polar(50, 50, 40, a)
    tor += f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="#7a3a10" stroke-width="5.4" stroke-linecap="round"/>'
    tor += f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" stroke="#d9823c" stroke-width="3.6" stroke-linecap="round"/>'
    hx1, hy1 = polar(50, 50, 18, a - 2); hx2, hy2 = polar(50, 50, 38, a - 2)
    tor += f'<path d="M{hx1:.1f} {hy1:.1f}L{hx2:.1f} {hy2:.1f}" stroke="#ffd9b0" stroke-width="1.1" stroke-linecap="round" stroke-opacity=".8"/>'
add("toroid_coil",
    leadp("M30 82L16 96") + leadp("M70 82L84 96")
    + '<circle cx="50" cy="50" r="38" fill="#2b2f36"/><circle cx="50" cy="50" r="17" fill="#15131c"/>' + tor
    + '<circle cx="50" cy="50" r="17" fill="none" stroke="#3c2410" stroke-width="1.5"/>'
    '<ellipse cx="40" cy="30" rx="14" ry="5" fill="#fff" fill-opacity=".25" transform="rotate(-30 40 30)"/>',
    COPPER_V.replace('x1="0" y1="0" x2="1" y2="0"', 'x1="0" y1="0" x2="1" y2="1"'))
coil_back = coil_front = ""
for i in range(9):
    x = 22 + i * 7
    coil_back += f'<path d="M{x} 30Q{x + 5} 50 {x} 70" fill="none" stroke="#8a4512" stroke-width="5" stroke-linecap="round"/>'
    coil_front += (f'<path d="M{x} 70Q{x + 9} 50 {x + 7} 30" fill="none" stroke="#5a2a08" stroke-width="6.5" stroke-linecap="round"/>'
                   f'<path d="M{x} 70Q{x + 9} 50 {x + 7} 30" fill="none" stroke="url(#cuh2)" stroke-width="4.5" stroke-linecap="round"/>')
add("air_coil",
    '<path d="M4 70H22M85 30Q92 30 96 30" fill="none" stroke="#5a2a08" stroke-width="6.5" stroke-linecap="round"/>'
    '<path d="M4 70H22M85 30H96" fill="none" stroke="#e8a060" stroke-width="4.5" stroke-linecap="round"/>'
    + coil_back + coil_front,
    lin("cuh2", [(0, "#ffe2c0", None), (.4, "#e08a40", None), (1, "#8a4512", None)], 1, 0))
add("inductor_axial",
    lead(3, 50, 26, 50) + lead(74, 50, 97, 50)
    + '<rect x="22" y="36" width="56" height="28" rx="12" fill="#2fa651" stroke="#0b5a26" stroke-width="2"/>'
    + "".join(f'<rect x="{x}" y="36" width="5" height="28" fill="{c}"/>' for x, c in ((32, "#7a3f12"), (42, "#1a1a1a"), (52, "#d91c1c"), (66, "#d4a017")))
    + '<rect x="22" y="36" width="56" height="28" rx="12" fill="url(#gl)"/>', GLOSS)

# ---------------------------------------------------------------- ICs
def dip(name, pins, label, sub, w=48, gap=11):
    h = gap * pins + 6
    x0, y0 = 50 - w / 2, 50 - h / 2
    p = ""
    for i in range(pins):
        y = y0 + 6 + i * gap + gap / 2 - 3
        for side in (-1, 1):
            px = x0 - 9 if side < 0 else x0 + w
            p += (f'<rect x="{px:.1f}" y="{y:.1f}" width="9" height="5" fill="url(#ag)" stroke="#6b737d" stroke-width=".8"/>'
                  f'<rect x="{px + (2 if side < 0 else 4):.1f}" y="{y + 1:.1f}" width="3" height="3" fill="#9aa2ad"/>')
    tx = 50
    add(name, p
        + f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="3" fill="url(#ic)" stroke="#000" stroke-width="1.2"/>'
        f'<path d="M{50 - 6} {y0}A6 6 0 0 0 {50 + 6} {y0}" fill="#0c0c10" stroke="#3a3a44" stroke-width="1"/>'
        f'<circle cx="{x0 + 7}" cy="{y0 + 9}" r="2.6" fill="#0c0c10" stroke="#3a3a44" stroke-width=".8"/>'
        f'<text x="{tx}" y="{50 - 1}" text-anchor="middle" {FONT} font-weight="700" font-size="{9 if len(label) < 7 else 7.5}" fill="#d9dde3" transform="rotate(90 50 50)" dy="0">{label}</text>'
        f'<text x="{tx}" y="{50 + 9}" text-anchor="middle" {FONT} font-size="5.5" fill="#9aa2ad" transform="rotate(90 50 50)">{sub}</text>',
        lin("ic", [(0, "#3a3a44", None), (.5, "#1c1c22", None), (1, "#101014", None)], 1, 1) + SILVER)


dip("ic_555", 4, "NE555", "TEXAS 2236", w=44, gap=14)
dip("ic_dip16", 8, "74HC595", "N  2318A", w=40, gap=10)
# QFP microcontroller
q = ""
for i in range(10):
    t = 24 + i * 5.8
    q += f'<rect x="{t:.1f}" y="12" width="2.6" height="10" fill="url(#ag)"/><rect x="{t:.1f}" y="78" width="2.6" height="10" fill="url(#ag)"/>'
    q += f'<rect x="12" y="{t:.1f}" width="10" height="2.6" fill="url(#agv)"/><rect x="78" y="{t:.1f}" width="10" height="2.6" fill="url(#agv)"/>'
add("ic_qfp", q
    + '<rect x="20" y="20" width="60" height="60" rx="3" fill="url(#ic)" stroke="#000" stroke-width="1.2"/>'
    '<rect x="23" y="23" width="54" height="54" rx="2" fill="none" stroke="#ffffff" stroke-opacity=".08" stroke-width="1"/>'
    '<circle cx="29" cy="29" r="3" fill="#0c0c10" stroke="#3a3a44" stroke-width=".8"/>'
    '<circle cx="66" cy="66" r="6" fill="#16161b" stroke="#2a2a33" stroke-width=".8"/>'
    f'<text x="50" y="49" text-anchor="middle" {FONT} font-weight="700" font-size="8" fill="#d9dde3">ATMEGA</text>'
    f'<text x="50" y="58" text-anchor="middle" {FONT} font-weight="700" font-size="8" fill="#d9dde3">328P-AU</text>'
    f'<text x="44" y="67" text-anchor="middle" {FONT} font-size="5" fill="#8a909a">2347 TW</text>',
    lin("ic", [(0, "#3a3a44", None), (.5, "#1c1c22", None), (1, "#101014", None)], 1, 1) + SILVER + SILVER_V)

# ---------------------------------------------------------------- semiconductors
add("transistor_to92",
    lead(38, 70, 34, 97) + lead(50, 70, 50, 97) + lead(62, 70, 66, 97)
    + '<path d="M26 72V36A24 24 0 0 1 74 36V72Z" fill="url(#to92)" stroke="#000" stroke-width="1.2"/>'
    '<path d="M32 70V38A18 18 0 0 1 46 20" fill="none" stroke="#fff" stroke-opacity=".18" stroke-width="3"/>'
    f'<text x="50" y="44" text-anchor="middle" {FONT} font-weight="700" font-size="8.5" fill="#d9dde3">BC</text>'
    f'<text x="50" y="54" text-anchor="middle" {FONT} font-weight="700" font-size="8.5" fill="#d9dde3">547B</text>'
    f'<text x="50" y="64" text-anchor="middle" {FONT} font-size="5" fill="#8a909a">C 21</text>',
    lin("to92", [(0, "#0e0e12", None), (.3, "#3a3a44", None), (.6, "#1c1c22", None), (1, "#08080a", None)], 1, 0))
add("transistor_to220",
    lead(38, 76, 38, 97) + lead(50, 76, 50, 97) + lead(62, 76, 62, 97)
    + '<path d="M26 4H74V40H26Z" fill="url(#agv)" stroke="#6b737d" stroke-width="1.2"/>'
    '<circle cx="50" cy="18" r="7" fill="#15131c" stroke="#6b737d" stroke-width="1.5"/>'
    '<rect x="24" y="36" width="52" height="42" rx="2" fill="url(#to220)" stroke="#000" stroke-width="1.2"/>'
    f'<text x="50" y="54" text-anchor="middle" {FONT} font-weight="700" font-size="9" fill="#d9dde3">IRF540N</text>'
    f'<text x="50" y="65" text-anchor="middle" {FONT} font-size="6" fill="#8a909a">IR  2219</text>',
    SILVER_V + lin("to220", [(0, "#3a3a44", None), (.5, "#1c1c22", None), (1, "#0c0c10", None)], 1, 1))
add("diode",
    lead(3, 50, 30, 50) + lead(70, 50, 97, 50)
    + '<rect x="26" y="39" width="48" height="22" rx="4" fill="#1c1c22"/>'
    '<rect x="62" y="39" width="7" height="22" fill="#c9ced6"/>'
    '<rect x="26" y="39" width="48" height="22" rx="4" fill="url(#gl)"/>'
    f'<text x="44" y="53" text-anchor="middle" {FONT} font-size="6.5" fill="#9aa2ad">1N4007</text>', GLOSS)
add("zener_diode",
    lead(3, 50, 32, 50) + lead(68, 50, 97, 50)
    + '<rect x="28" y="40" width="44" height="20" rx="9" fill="#ff8a3d" fill-opacity=".75" stroke="#b34700" stroke-width="1.2"/>'
    '<path d="M36 50H64" stroke="#7d858f" stroke-width="2"/><rect x="45" y="45" width="10" height="10" fill="#555"/>'
    '<rect x="60" y="40" width="5" height="20" fill="#1a1a1a"/>'
    '<rect x="28" y="40" width="44" height="20" rx="9" fill="url(#gl)"/>', GLOSS)


def led(name, c_light, c_mid, c_dark, glow):
    add(name,
        f'<circle cx="50" cy="32" r="34" fill="url(#glow)"/>'
        + lead(42, 70, 42, 97) + leadp("M58 70L58 82L62 86L62 92")
        + f'<rect x="28" y="64" width="44" height="8" rx="2" fill="{c_dark}"/>'
        f'<path d="M30 66V34A20 20 0 0 1 70 34V66Z" fill="url(#lens)" stroke="{c_dark}" stroke-width="1.5"/>'
        '<path d="M42 66V48H50L54 44V40H44L40 48" fill="#5a5f66" fill-opacity=".75"/>'
        '<path d="M58 66V44" stroke="#5a5f66" stroke-opacity=".75" stroke-width="3"/>'
        '<path d="M46 44Q52 36 58 44" fill="none" stroke="#c0c4ca" stroke-opacity=".6" stroke-width="1"/>'
        '<path d="M36 60V34A14 14 0 0 1 46 20" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="4" stroke-linecap="round"/>',
        f'<radialGradient id="glow"><stop offset="0" stop-color="{glow}" stop-opacity=".55"/><stop offset="1" stop-color="{glow}" stop-opacity="0"/></radialGradient>'
        + lin("lens", [(0, c_light, None), (.55, c_mid, None), (1, c_dark, None)], 1, 0)
        .replace("<stop", "<stop", 1))


led("led_red", "#ff9a9a", "#e8141e", "#8a000a", "#ff3030")
led("led_green", "#b8ffb8", "#1fc43a", "#0b6e1a", "#40ff60")
led("led_blue", "#bfe0ff", "#1f6fff", "#0a2f8a", "#3fa0ff")
led("led_yellow", "#fff6b0", "#ffd000", "#a37800", "#ffe040")

# 7-segment display showing "8."
SEG = {"a": "M36 22L40 18H60L64 22L60 26H40Z", "b": "M66 24L70 28V46L66 50L62 46V28Z", "c": "M66 54L70 58V76L66 80L62 76V58Z",
       "d": "M36 82L40 78H60L64 82L60 86H40Z", "e": "M34 54L38 58V76L34 80L30 76V58Z", "f": "M34 24L38 28V46L34 50L30 46V28Z",
       "g": "M36 52L40 48H60L64 52L60 56H40Z"}
segs = "".join(f'<path d="{d}" fill="#ff2a1a" transform="skewX(-6) translate(6 0)"/>' for d in SEG.values())
add("seven_segment",
    "".join(f'<rect x="{x}" y="90" width="3" height="10" fill="url(#agv)"/>' for x in (24, 36, 48, 60, 72))
    + '<rect x="14" y="6" width="72" height="86" rx="3" fill="#2a2d33" stroke="#0c0c10" stroke-width="1.5"/>'
    '<rect x="20" y="12" width="60" height="74" rx="2" fill="#141519"/>'
    f'<g filter="url(#bl)" opacity=".8">{segs}</g>{segs}'
    '<circle cx="76" cy="82" r="3.5" fill="#ff2a1a"/>',
    '<filter id="bl" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5"/></filter>' + SILVER_V)
add("crystal",
    lead(38, 74, 38, 97) + lead(62, 74, 62, 97)
    + '<rect x="16" y="22" width="68" height="54" rx="27" fill="url(#xt)" stroke="#6b737d" stroke-width="1.5"/>'
    '<rect x="22" y="28" width="56" height="42" rx="21" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="1"/>'
    f'<text x="50" y="47" text-anchor="middle" {FONT} font-weight="700" font-size="11" fill="#3a4049">16.000</text>'
    f'<text x="50" y="59" text-anchor="middle" {FONT} font-size="7" fill="#5a6570">MHz  KDS</text>',
    lin("xt", [(0, "#ffffff", None), (.3, "#dfe3e8", None), (.7, "#a9b0b9", None), (1, "#7d858f", None)], 0, 1))

# ---------------------------------------------------------------- passives / electromech
knurl = "".join(f'<path d="M{polar(50, 44, 25, a)[0]:.1f} {polar(50, 44, 25, a)[1]:.1f}L{polar(50, 44, 29, a)[0]:.1f} {polar(50, 44, 29, a)[1]:.1f}" stroke="#7d858f" stroke-width="1.6"/>' for a in range(0, 360, 10))
add("potentiometer",
    lead(36, 80, 36, 97) + lead(50, 80, 50, 97) + lead(64, 80, 64, 97)
    + '<rect x="14" y="10" width="72" height="72" rx="6" fill="#1f5fbf" stroke="#0b2a6b" stroke-width="2"/>'
    '<rect x="14" y="10" width="72" height="20" rx="6" fill="#fff" fill-opacity=".12"/>'
    '<circle cx="50" cy="44" r="29" fill="url(#knob)" stroke="#5a6570" stroke-width="1.5"/>' + knurl
    + '<circle cx="50" cy="44" r="22" fill="url(#knob2)"/>'
    '<rect x="47" y="24" width="6" height="40" rx="2" fill="#5a6570" transform="rotate(35 50 44)"/>'
    f'<text x="50" y="79" text-anchor="middle" {FONT} font-weight="700" font-size="6" fill="#cfe0ff">B10K</text>',
    '<radialGradient id="knob" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#c9ced6"/><stop offset="1" stop-color="#7d858f"/></radialGradient>'
    '<radialGradient id="knob2" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#aeb6c0"/></radialGradient>')
add("trimmer",
    lead(30, 76, 30, 96) + lead(70, 76, 70, 96) + lead(50, 76, 50, 90)
    + '<rect x="18" y="18" width="64" height="60" rx="5" fill="#2a7de1" stroke="#0b3a8a" stroke-width="2"/>'
    '<circle cx="50" cy="46" r="20" fill="#f4f5f7" stroke="#9aa2ad" stroke-width="1.5"/>'
    '<path d="M50 30V62M34 46H66" stroke="#9aa2ad" stroke-width="6" stroke-linecap="round" transform="rotate(20 50 46)"/>'
    '<path d="M50 30V62M34 46H66" stroke="#ffffff" stroke-width="3" stroke-linecap="round" transform="rotate(20 50 46)"/>'
    f'<text x="50" y="74" text-anchor="middle" {FONT} font-weight="700" font-size="7" fill="#e8f1ff">103</text>')
add("relay",
    '<rect x="8" y="16" width="84" height="68" rx="4" fill="url(#rl)" stroke="#0b3a8a" stroke-width="2"/>'
    '<rect x="8" y="16" width="84" height="16" rx="4" fill="#fff" fill-opacity=".15"/>'
    f'<text x="50" y="40" text-anchor="middle" {FONT} font-weight="700" font-size="10" fill="#fff">SONGLE</text>'
    f'<text x="50" y="52" text-anchor="middle" {FONT} font-size="7.5" fill="#e8f1ff">SRD-05VDC-SL-C</text>'
    f'<text x="50" y="62" text-anchor="middle" {FONT} font-size="6.5" fill="#e8f1ff">10A 250VAC  10A 30VDC</text>'
    '<rect x="18" y="68" width="16" height="9" rx="1" fill="none" stroke="#e8f1ff" stroke-width="1"/>'
    '<path d="M20 74L24 70L28 74L32 70" fill="none" stroke="#e8f1ff" stroke-width="1"/>'
    '<path d="M44 76H58M46 70L56 72" stroke="#e8f1ff" stroke-width="1.2"/><circle cx="44" cy="76" r="1.5" fill="#e8f1ff"/>',
    lin("rl", [(0, "#4f8ff0", None), (1, "#1a4fb0", None)]))
add("fuse",
    '<rect x="6" y="36" width="20" height="28" rx="3" fill="url(#ag)" stroke="#6b737d" stroke-width="1.2"/>'
    '<rect x="74" y="36" width="20" height="28" rx="3" fill="url(#ag)" stroke="#6b737d" stroke-width="1.2"/>'
    '<rect x="24" y="38" width="52" height="24" fill="#e6f4ff" fill-opacity=".45" stroke="#9fc4e0" stroke-width="1.2"/>'
    '<path d="M24 50C34 44 40 56 50 50S66 44 76 50" fill="none" stroke="#7d858f" stroke-width="1.6"/>'
    '<rect x="24" y="40" width="52" height="5" fill="#fff" fill-opacity=".7"/>'
    '<path d="M10 42H22M78 42H90" stroke="#fff" stroke-width="2" stroke-opacity=".8"/>'
    f'<text x="16" y="70" text-anchor="middle" {FONT} font-size="5" fill="#9aa2ad">T2A</text>', SILVER)
add("battery_9v",
    '<rect x="30" y="6" width="14" height="10" rx="2" fill="url(#agv)" stroke="#6b737d" stroke-width="1"/>'
    '<path d="M58 6H72L74 9V13L72 16H58L56 13V9Z" fill="url(#agv)" stroke="#6b737d" stroke-width="1"/>'
    '<rect x="20" y="14" width="60" height="82" rx="4" fill="#1c1c22"/>'
    '<rect x="20" y="14" width="60" height="36" rx="4" fill="#ff8a00"/><rect x="20" y="44" width="60" height="6" fill="#ff8a00"/>'
    '<rect x="20" y="14" width="60" height="82" rx="4" fill="url(#bt)"/>'
    f'<text x="50" y="40" text-anchor="middle" {FONT} font-weight="900" font-size="18" fill="#1c1c22">9V</text>'
    f'<text x="50" y="70" text-anchor="middle" {FONT} font-weight="700" font-size="9" fill="#ff8a00">ALKALINE</text>'
    '<path d="M28 80H72" stroke="#ff8a00" stroke-width="1.5"/>',
    SILVER_V + lin("bt", [(0, "#000", .35), (.2, "#fff", .2), (.35, "#fff", 0), (1, "#000", .3)], 1, 0))
add("battery_aa",
    '<rect x="86" y="42" width="8" height="16" rx="2" fill="url(#ag)" stroke="#6b737d" stroke-width="1"/>'
    '<rect x="6" y="32" width="82" height="36" rx="5" fill="url(#aa1)"/>'
    '<rect x="56" y="32" width="32" height="36" rx="0" fill="url(#aa2)"/>'
    '<rect x="6" y="32" width="82" height="36" rx="5" fill="none" stroke="#3a2a10" stroke-width="1"/>'
    f'<text x="32" y="55" text-anchor="middle" {FONT} font-weight="900" font-size="11" fill="#d4a017">1.5V</text>'
    f'<text x="72" y="55" text-anchor="middle" {FONT} font-weight="900" font-size="11" fill="#1c1c22">AA</text>'
    '<path d="M60 38V44M57 41H63" stroke="#1c1c22" stroke-width="1.8"/>',
    lin("aa1", [(0, "#0c0c10", None), (.25, "#55555f", None), (.5, "#1c1c22", None), (1, "#08080a", None)])
    + lin("aa2", [(0, "#7a4a08", None), (.25, "#ffd27a", None), (.5, "#d48a1a", None), (1, "#7a4a08", None)]) + SILVER)
add("tactile_switch",
    leadp("M18 30H6V22") + leadp("M18 70H6V78") + leadp("M82 30H94V22") + leadp("M82 70H94V78")
    + '<rect x="16" y="16" width="68" height="68" rx="4" fill="url(#ts)" stroke="#5a6570" stroke-width="1.5"/>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#2a2d33" stroke="#9aa2ad" stroke-width="1"/>' for x, y in ((24, 24), (76, 24), (24, 76), (76, 76)))
    + '<circle cx="50" cy="50" r="22" fill="#5a6570"/><circle cx="50" cy="50" r="19" fill="url(#btn)"/>'
    '<ellipse cx="44" cy="43" rx="8" ry="5" fill="#fff" fill-opacity=".25" transform="rotate(-30 44 43)"/>',
    lin("ts", [(0, "#ffffff", None), (.5, "#c9ced6", None), (1, "#8a929c", None)], 1, 1)
    + '<radialGradient id="btn" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#5a5f6a"/><stop offset="1" stop-color="#0c0c10"/></radialGradient>')
add("toggle_switch",
    '<path d="M50 50L70 10" stroke="#5a6570" stroke-width="10" stroke-linecap="round"/>'
    '<path d="M50 50L70 10" stroke="url(#agv)" stroke-width="7" stroke-linecap="round"/>'
    '<circle cx="71" cy="8" r="6" fill="url(#knob)"/>'
    '<polygon points="22,50 36,26 64,26 78,50 64,74 36,74" fill="url(#nut)" stroke="#5a6570" stroke-width="1.5"/>'
    '<circle cx="50" cy="50" r="15" fill="#c9ced6" stroke="#5a6570" stroke-width="1.5"/><circle cx="50" cy="50" r="9" fill="#7d858f"/>'
    f'<text x="50" y="88" text-anchor="middle" {FONT} font-weight="700" font-size="9" fill="#7d858f">ON  ·  OFF</text>',
    SILVER_V + lin("nut", [(0, "#ffffff", None), (.5, "#b5bcc4", None), (1, "#7d858f", None)], 1, 1)
    + '<radialGradient id="knob" cx=".4" cy=".35" r=".8"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#8a929c"/></radialGradient>')
lam = "".join(f'<path d="M10 {y}H90" stroke="#4a5058" stroke-width=".6" stroke-opacity=".7"/>' for y in range(14, 88, 3))
wind = "".join(f'<path d="M{x} 30V70" stroke="#7a3a10" stroke-width="2.4"/><path d="M{x} 30V70" stroke="#d9823c" stroke-width="1.6"/><path d="M{x - .4:.1f} 30V70" stroke="#ffd9b0" stroke-width=".5"/>' for x in range(32, 70, 2))
add("transformer",
    '<rect x="10" y="12" width="80" height="76" rx="2" fill="url(#fe)" stroke="#3a3f46" stroke-width="1.5"/>' + lam
    + '<rect x="22" y="26" width="16" height="48" fill="#15131c"/><rect x="62" y="26" width="16" height="48" fill="#15131c"/>'
    '<rect x="28" y="26" width="44" height="48" rx="3" fill="#b8692a"/>' + wind
    + '<rect x="28" y="26" width="44" height="48" rx="3" fill="none" stroke="#5a2a08" stroke-width="1.5"/>'
    '<rect x="28" y="46" width="44" height="8" fill="#f2e6c8" fill-opacity=".9"/>'
    f'<text x="50" y="52.5" text-anchor="middle" {FONT} font-weight="700" font-size="5.5" fill="#5a2a08">230V/12V</text>'
    + leadp("M34 88V96") + leadp("M44 88V96") + leadp("M56 88V96") + leadp("M66 88V96"),
    lin("fe", [(0, "#a9b0b9", None), (.5, "#7d858f", None), (1, "#5a6168", None)], 1, 1)
    + lin("cuh", [(0, "#ffe2c0", None), (.5, "#e08a40", None), (1, "#8a4512", None)], 1, 0))
add("pcb",
    '<rect x="6" y="10" width="88" height="80" rx="6" fill="#0f6e3a" stroke="#07401f" stroke-width="2"/>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#15131c" stroke="#e0b44a" stroke-width="1.5"/>' for x, y in ((14, 18), (86, 18), (14, 82), (86, 82)))
    + '<g fill="none" stroke="#e0b44a" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".9">'
    '<path d="M22 30H40L48 38V52"/><path d="M22 40H34L40 46V66H60"/><path d="M76 28V44L68 52H58"/><path d="M28 76H50L56 70H78"/>'
    '<path d="M66 30H76"/><path d="M60 62V58"/></g>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="3.2" fill="#e0b44a"/><circle cx="{x}" cy="{y}" r="1.3" fill="#15131c"/>' for x, y in ((22, 30), (22, 40), (48, 52), (60, 66), (76, 28), (66, 30), (58, 52), (28, 76), (78, 70)))
    + '<rect x="52" y="34" width="12" height="7" rx="1" fill="#1c1c22"/><rect x="50" y="35" width="3" height="5" fill="#d6dbe1"/><rect x="63" y="35" width="3" height="5" fill="#d6dbe1"/>'
    '<rect x="66" y="56" width="16" height="10" rx="1" fill="#1c1c22"/><rect x="64" y="58" width="3" height="6" fill="#d6dbe1"/><rect x="81" y="58" width="3" height="6" fill="#d6dbe1"/>'
    f'<text x="40" y="88" {FONT} font-size="5" fill="#e8f5ec">R12   C3   v1.2</text>')
add("buzzer",
    leadp("M42 84V97") + leadp("M58 84V92")
    + '<circle cx="50" cy="48" r="40" fill="url(#bz)" stroke="#000" stroke-width="1.5"/>'
    '<circle cx="50" cy="48" r="30" fill="none" stroke="#3a3a44" stroke-width="1.5"/>'
    '<circle cx="50" cy="48" r="6" fill="#000"/><circle cx="50" cy="48" r="6" fill="none" stroke="#3a3a44" stroke-width="1"/>'
    '<path d="M70 26V34M66 30H74" stroke="#d9dde3" stroke-width="2"/>'
    f'<text x="50" y="76" text-anchor="middle" {FONT} font-weight="700" font-size="6" fill="#9aa2ad">REMOVE SEAL</text>'
    '<path d="M28 24C34 16 44 12 52 12" fill="none" stroke="#fff" stroke-opacity=".2" stroke-width="4" stroke-linecap="round"/>',
    '<radialGradient id="bz" cx=".4" cy=".35" r=".75"><stop offset="0" stop-color="#4a4a55"/><stop offset="1" stop-color="#0c0c10"/></radialGradient>')

# ---------------------------------------------------------------- schematic symbols (ink on paper)
def paper(inner):
    return ('<rect x="6" y="6" width="88" height="88" rx="8" fill="#f6f2e6" stroke="#c9bfa3" stroke-width="2"/>'
            + "".join(f'<path d="M6 {y}H94" stroke="#bcd3e8" stroke-width=".7"/>' for y in range(18, 94, 10))
            + f'<g fill="none" stroke="#1b2a6b" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')


add("symbol_ground", paper('<path d="M50 16V48M26 48H74M34 58H66M42 68H58M48 78H52"/>'))
add("symbol_opamp", paper('<path d="M30 22V78L80 50Z"/><path d="M14 36H30M14 64H30M80 50H92"/>'
                          '<path d="M34 36H42M38 32V40M34 64H42" stroke-width="2.4"/>'))
add("symbol_resistor", paper('<path d="M10 50H26L30 40L38 60L46 40L54 60L62 40L70 60L74 50H90"/>'
                             '<circle cx="10" cy="50" r="2.5" fill="#1b2a6b"/><circle cx="90" cy="50" r="2.5" fill="#1b2a6b"/>'))

# --------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
for name, svg in P.items():
    with open(os.path.join(OUT, name + ".svg"), "w") as f:
        f.write(svg)
print(len(P), "electro")
