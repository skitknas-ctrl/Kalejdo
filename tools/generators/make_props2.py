# Historik: det här skriptet ritade de inbyggda prylarna i props/. SVG-filerna i props/ är källan nu.
# Kör inte rakt av, eftersom det skriver över befintliga filer. Använd det som mall för nya prylar i samma stil.
# Användning: python tools/generators/make_props2.py <utmapp>
"""Christmas + evaQ8 categories for Kalejdo -> <repo>/props/<cat>/<name>.svg"""
import math, os, sys

OUT = os.path.join(sys.argv[1], "props")
P = {}


def add(cat, name, body, defs=""):
    d = f"<defs>{defs}</defs>" if defs else ""
    P[(cat, name)] = ('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
                      f"{d}{body}</svg>\n")


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def pts(lst):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in lst)


def star(cx, cy, R, r, n, rot=-90):
    return [polar(cx, cy, R if i % 2 == 0 else r, rot + i * 180 / n) for i in range(2 * n)]


def ngon(cx, cy, r, n, rot=-90):
    return [polar(cx, cy, r, rot + i * 360 / n) for i in range(n)]


# =============================================================== CHRISTMAS
C = "christmas"


def bauble(name, light, mid, dark, deco):
    defs = (f'<radialGradient id="g" cx=".36" cy=".34" r=".75"><stop offset="0" stop-color="{light}"/>'
            f'<stop offset=".5" stop-color="{mid}"/><stop offset="1" stop-color="{dark}"/></radialGradient>'
            '<clipPath id="c"><circle cx="50" cy="58" r="36"/></clipPath>')
    add(C, name,
        '<path d="M50 6C44 6 44 14 50 14C56 14 56 6 50 6Z" fill="none" stroke="#b8a46a" stroke-width="2.5"/>'
        '<rect x="41" y="13" width="18" height="10" rx="2" fill="#e8c95a" stroke="#9a7b1e" stroke-width="2"/>'
        '<path d="M44 13V23M50 13V23M56 13V23" stroke="#9a7b1e" stroke-width="1.2"/>'
        f'<circle cx="50" cy="58" r="36" fill="url(#g)"/><g clip-path="url(#c)">{deco}</g>'
        f'<circle cx="50" cy="58" r="36" fill="none" stroke="{dark}" stroke-width="2"/>'
        '<ellipse cx="37" cy="44" rx="8" ry="5" fill="#fff" fill-opacity=".7" transform="rotate(-35 37 44)"/>', defs)


bauble("bauble_red", "#ff8a8a", "#e01b2f", "#7a0010",
       '<path d="M10 52Q30 44 50 52T90 52" fill="none" stroke="#ffd34d" stroke-width="5"/>'
       '<path d="M10 66Q30 58 50 66T90 66" fill="none" stroke="#ffd34d" stroke-width="5"/>'
       + "".join(f'<circle cx="{x}" cy="59" r="2.6" fill="#fff"/>' for x in range(20, 90, 12)))
bauble("bauble_gold", "#fff3b0", "#f2b81b", "#8a5a00",
       f'<polygon points="{pts(star(50, 60, 17, 7, 5))}" fill="#fff" fill-opacity=".85"/>'
       + "".join(f'<circle cx="{polar(50, 60, 27, a)[0]:.1f}" cy="{polar(50, 60, 27, a)[1]:.1f}" r="2.4" fill="#fff8d8"/>' for a in range(0, 360, 30)))
bauble("bauble_blue", "#b8dcff", "#2a7de1", "#0b2a6b",
       '<polyline points="12,56 22,46 32,56 42,46 52,56 62,46 72,56 82,46 92,56" fill="none" stroke="#fff" stroke-width="3.5" stroke-linejoin="round"/>'
       '<polyline points="12,72 22,62 32,72 42,62 52,72 62,62 72,72 82,62 92,72" fill="none" stroke="#c9e4ff" stroke-width="3" stroke-linejoin="round"/>')
bauble("bauble_green", "#b6f5c4", "#1fa64a", "#0b4a1f",
       "".join(f'<circle cx="{x}" cy="{y}" r="5" fill="#ff4f5f"/>' for x, y in ((30, 44), (56, 40), (74, 56), (40, 64), (62, 76), (26, 80), (82, 78), (48, 88)))
       + '<path d="M14 58H86" stroke="#ffd34d" stroke-width="4"/>')
bauble("bauble_purple", "#f0c8ff", "#9b3de0", "#3d0f66",
       "".join(f'<path d="M{x} 20V96" stroke="#fff" stroke-opacity=".55" stroke-width="5"/>' for x in (26, 42, 58, 74)))

add(C, "christmas_tree",
    '<rect x="44" y="80" width="12" height="14" fill="#7a4d17"/>'
    '<polygon points="50,12 76,46 64,46 84,70 64,70 90,86 10,86 36,70 16,70 36,46 24,46" fill="#1d8a42" stroke="#0b4a1f" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M32 50Q50 58 68 48M24 74Q50 84 76 72" fill="none" stroke="#ffd34d" stroke-width="3" stroke-linecap="round"/>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="4" fill="{c}"/>' for x, y, c in ((40, 40, "#e8262e"), (58, 58, "#2a7de1"), (36, 62, "#ffd34d"), (64, 78, "#e8262e"), (30, 80, "#2a7de1"), (52, 30, "#ffd34d")))
    + f'<polygon points="{pts(star(50, 12, 11, 4.5, 5))}" fill="#ffd21f" stroke="#a37800" stroke-width="2" stroke-linejoin="round"/>')
add(C, "candy_cane",
    '<path d="M38 94V34A16 16 0 0 1 70 34V42" fill="none" stroke="#7a0010" stroke-width="18" stroke-linecap="round"/>'
    '<path d="M38 94V34A16 16 0 0 1 70 34V42" fill="none" stroke="#fff" stroke-width="14" stroke-linecap="round"/>'
    '<path d="M38 94V34A16 16 0 0 1 70 34V42" fill="none" stroke="#e01b2f" stroke-width="14" stroke-dasharray="7 7"/>'
    '<path d="M42 90V36A12 12 0 0 1 52 22" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="3" stroke-linecap="round"/>')
gb_icing = ('<path d="M30 48Q50 54 70 48M32 88Q38 84 42 88M58 88Q62 84 68 88M18 54Q22 50 26 54M74 54Q78 50 82 54" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>')
add(C, "gingerbread_man",
    '<path d="M50 8A14 14 0 0 1 60 32L82 36A8 8 0 0 1 82 52L64 54L74 84A8 8 0 0 1 60 92L50 72L40 92A8 8 0 0 1 26 84L36 54L18 52A8 8 0 0 1 18 36L40 32A14 14 0 0 1 50 8Z" fill="#c8813c" stroke="#7a4514" stroke-width="3" stroke-linejoin="round"/>'
    + gb_icing + '<circle cx="45" cy="19" r="2.5" fill="#3a1a05"/><circle cx="55" cy="19" r="2.5" fill="#3a1a05"/>'
    '<path d="M44 26Q50 30 56 26" fill="none" stroke="#3a1a05" stroke-width="2" stroke-linecap="round"/>'
    '<circle cx="50" cy="58" r="3" fill="#e8262e"/><circle cx="50" cy="68" r="3" fill="#2fbf4f"/>')
heart = "M50 88C20 66 8 48 12 32C16 16 38 12 50 30C62 12 84 16 88 32C92 48 80 66 50 88Z"
add(C, "gingerbread_heart",
    f'<path d="{heart}" fill="#b5692a" stroke="#6b3510" stroke-width="3"/>'
    f'<path d="{heart}" fill="none" stroke="#fff" stroke-width="2.5" stroke-dasharray="1 5" stroke-linecap="round" transform="translate(50 50) scale(.82) translate(-50 -50)"/>'
    '<path d="M36 48Q42 42 48 48T60 48" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round"/>'
    f'<polygon points="{pts(star(50, 34, 6, 2.5, 5))}" fill="#fff"/>'
    '<circle cx="50" cy="62" r="3" fill="#e8262e"/>')


def present(name, box, ribbon, dark):
    add(C, name,
        f'<rect x="14" y="40" width="72" height="52" rx="3" fill="{box}" stroke="{dark}" stroke-width="3"/>'
        f'<rect x="10" y="30" width="80" height="14" rx="3" fill="{box}" stroke="{dark}" stroke-width="3"/>'
        f'<rect x="44" y="30" width="12" height="62" fill="{ribbon}"/><rect x="14" y="58" width="72" height="9" fill="{ribbon}" fill-opacity=".9"/>'
        f'<path d="M50 30C38 8 18 16 30 28C36 32 44 31 50 30C56 31 64 32 70 28C82 16 62 8 50 30Z" fill="{ribbon}" stroke="{dark}" stroke-width="2.5" stroke-linejoin="round"/>'
        f'<circle cx="50" cy="29" r="5" fill="{ribbon}" stroke="{dark}" stroke-width="2"/>')


present("present_red", "#e01b2f", "#ffd34d", "#6b000c")
present("present_green", "#1fa64a", "#e01b2f", "#0b4a1f")
present("present_blue", "#2a7de1", "#ffffff", "#0b2a6b")
add(C, "stocking",
    '<path d="M30 22H66V60C66 64 70 70 76 74C88 80 86 96 70 94L40 90C24 88 22 72 30 62Z" fill="#e01b2f" stroke="#6b000c" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M62 76C70 76 78 80 80 86" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
    '<rect x="26" y="8" width="44" height="18" rx="8" fill="#fff" stroke="#c9c9d6" stroke-width="2.5"/>'
    '<path d="M38 40L44 46L38 52M52 40L58 46L52 52" fill="none" stroke="#2fbf4f" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
add(C, "santa_hat",
    '<path d="M14 76C18 40 38 14 66 16C82 18 90 34 86 50C82 42 74 38 68 42C70 54 74 66 84 76Z" fill="#e01b2f" stroke="#6b000c" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="8" y="70" width="80" height="18" rx="9" fill="#fff" stroke="#c9c9d6" stroke-width="2.5"/>'
    '<circle cx="86" cy="54" r="10" fill="#fff" stroke="#c9c9d6" stroke-width="2.5"/>')
leaf = "M50 50C42 40 30 38 20 42C24 38 22 32 18 28C30 26 40 30 46 38C46 30 50 24 54 20C56 30 54 40 50 50Z"
add(C, "holly",
    f'<path d="M50 52C40 44 26 46 12 56C18 52 18 46 14 40C26 36 36 36 44 42C40 34 40 26 44 20C52 28 54 40 50 52Z" fill="#1d8a42" stroke="#0b4a1f" stroke-width="2.5" stroke-linejoin="round"/>'
    f'<path d="M50 52C60 44 74 46 88 56C82 52 82 46 86 40C74 36 64 36 56 42C60 34 60 26 56 20C48 28 46 40 50 52Z" fill="#2fa651" stroke="#0b4a1f" stroke-width="2.5" stroke-linejoin="round"/>'
    '<path d="M50 52L22 48M50 52L78 48" stroke="#0b4a1f" stroke-width="1.5"/>'
    '<circle cx="42" cy="62" r="9" fill="#e01b2f" stroke="#7a0010" stroke-width="2"/><circle cx="58" cy="62" r="9" fill="#e01b2f" stroke="#7a0010" stroke-width="2"/>'
    '<circle cx="50" cy="74" r="9" fill="#e8262e" stroke="#7a0010" stroke-width="2"/>'
    '<circle cx="39" cy="59" r="2.5" fill="#fff" fill-opacity=".7"/><circle cx="55" cy="59" r="2.5" fill="#fff" fill-opacity=".7"/><circle cx="47" cy="71" r="2.5" fill="#fff" fill-opacity=".7"/>')
add(C, "snowman",
    '<circle cx="50" cy="72" r="24" fill="#fff" stroke="#9fb4cc" stroke-width="2.5"/>'
    '<circle cx="50" cy="38" r="17" fill="#fff" stroke="#9fb4cc" stroke-width="2.5"/>'
    '<rect x="36" y="8" width="28" height="16" rx="2" fill="#222"/><rect x="30" y="22" width="40" height="5" rx="2" fill="#222"/><rect x="36" y="18" width="28" height="4" fill="#e01b2f"/>'
    '<circle cx="44" cy="35" r="2.5" fill="#222"/><circle cx="56" cy="35" r="2.5" fill="#222"/>'
    '<polygon points="50,40 66,44 50,45" fill="#ff8a00"/>'
    '<path d="M32 52Q50 60 68 52L66 60Q50 66 34 60Z" fill="#e01b2f"/><path d="M60 58L64 74L56 72Z" fill="#e01b2f"/>'
    '<circle cx="50" cy="66" r="2.5" fill="#222"/><circle cx="50" cy="76" r="2.5" fill="#222"/><circle cx="50" cy="86" r="2.5" fill="#222"/>'
    '<path d="M28 66L10 54M72 66L90 54M14 56L10 48M86 56L90 48" stroke="#6b3a14" stroke-width="3" stroke-linecap="round"/>')
wr = ""
for i in range(16):
    a = i * 22.5
    x, y = polar(50, 50, 32, a)
    wr += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="11" ry="6" fill="{"#1d8a42" if i % 2 else "#2fa651"}" stroke="#0b4a1f" stroke-width="1.5" transform="rotate({a + 60:.0f} {x:.1f} {y:.1f})"/>'
for a in range(10, 360, 45):
    x, y = polar(50, 50, 30, a)
    wr += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#e01b2f"/>'
add(C, "wreath", wr +
    '<path d="M50 82L40 96M50 82L60 96" stroke="#e01b2f" stroke-width="5" stroke-linecap="round"/>'
    '<path d="M50 82C40 70 30 76 34 84C38 90 46 86 50 82C54 86 62 90 66 84C70 76 60 70 50 82Z" fill="#e01b2f" stroke="#7a0010" stroke-width="2"/>')
add(C, "candle",
    '<ellipse cx="50" cy="92" rx="30" ry="6" fill="#d9b35a" stroke="#8a6a1e" stroke-width="2"/>'
    '<rect x="36" y="38" width="28" height="54" rx="3" fill="#e01b2f" stroke="#7a0010" stroke-width="2.5"/>'
    '<path d="M40 38V50C40 54 46 54 46 50V38" fill="#ff5c6c"/>'
    '<path d="M50 38V30" stroke="#333" stroke-width="2"/>'
    '<path d="M50 6C58 16 60 24 50 32C40 24 42 16 50 6Z" fill="#ffb21f" stroke="#e06a00" stroke-width="2"/>'
    '<path d="M50 14C54 20 54 24 50 28C46 24 46 20 50 14Z" fill="#fff6b0"/>')
# Swedish "adventsstjärna": paper star with a glow and punched pattern
add(C, "advent_star",
    f'<circle cx="50" cy="50" r="46" fill="#ffd36b" fill-opacity=".25"/>'
    f'<polygon points="{pts(star(50, 50, 44, 18, 8, -90))}" fill="#e01b2f" stroke="#7a0010" stroke-width="2.5" stroke-linejoin="round"/>'
    f'<polygon points="{pts(star(50, 50, 30, 13, 8, -90))}" fill="#ff6a5c"/>'
    + "".join(f'<circle cx="{polar(50, 50, 22, a)[0]:.1f}" cy="{polar(50, 50, 22, a)[1]:.1f}" r="2.6" fill="#fff3b0"/>' for a in range(-90, 270, 45))
    + '<circle cx="50" cy="50" r="7" fill="#fff3b0"/>')
# Swedish "julbock" (straw goat)
straw = '#e6c26a'
add(C, "straw_goat",
    f'<g fill="none" stroke="{straw}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M24 50H70"/><path d="M30 50L24 88M38 50L40 88M62 50L58 88M70 50L74 88"/>'
    '<path d="M70 50L80 26"/><path d="M80 26C70 14 66 6 56 10M80 26C86 14 94 10 92 4"/><path d="M80 26L92 36"/><path d="M24 50L12 40"/></g>'
    '<g fill="none" stroke="#b8902e" stroke-width="1.5" stroke-linecap="round"><path d="M24 48H70M24 52H70M72 48L80 28"/></g>'
    '<g fill="#e01b2f"><rect x="32" y="45" width="5" height="11" rx="1"/><rect x="58" y="45" width="5" height="11" rx="1"/>'
    '<rect x="72" y="36" width="10" height="5" rx="1" transform="rotate(65 77 38)"/>'
    '<rect x="26" y="66" width="10" height="5" rx="1"/><rect x="56" y="66" width="10" height="5" rx="1"/><rect x="36" y="66" width="10" height="5" rx="1"/><rect x="68" y="66" width="10" height="5" rx="1"/></g>')
# Swedish "lussekatt" (saffron bun, S-shape with raisins)
add(C, "lussekatt",
    '<path d="M50 50C50 30 22 22 18 40C14 56 34 62 40 52M50 50C50 70 78 78 82 60C86 44 66 38 60 48" fill="none" stroke="#a35c00" stroke-width="22" stroke-linecap="round"/>'
    '<path d="M50 50C50 30 22 22 18 40C14 56 34 62 40 52M50 50C50 70 78 78 82 60C86 44 66 38 60 48" fill="none" stroke="#f2a400" stroke-width="17" stroke-linecap="round"/>'
    '<path d="M36 32C30 32 24 36 24 42M64 68C70 68 76 64 76 58" fill="none" stroke="#ffd36b" stroke-width="4" stroke-linecap="round"/>'
    '<ellipse cx="38" cy="47" rx="4.5" ry="3.5" fill="#3a1a2a"/><ellipse cx="62" cy="53" rx="4.5" ry="3.5" fill="#3a1a2a"/>')
# Tomte / nisse
add(C, "tomte",
    '<path d="M50 4C34 20 22 38 18 56H82C76 34 64 14 50 4Z" fill="#e01b2f" stroke="#6b000c" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M50 4C56 10 62 12 70 10" fill="none" stroke="#6b000c" stroke-width="3" stroke-linecap="round"/><circle cx="72" cy="10" r="6" fill="#fff" stroke="#c9c9d6" stroke-width="2"/>'
    '<path d="M16 54C10 78 30 96 50 96S90 78 84 54C70 62 30 62 16 54Z" fill="#fff" stroke="#c9c9d6" stroke-width="2.5"/>'
    '<path d="M30 74C36 82 44 84 50 80M70 74C64 82 56 84 50 80" fill="none" stroke="#d9dde6" stroke-width="2"/>'
    '<rect x="14" y="50" width="72" height="10" rx="5" fill="#fff" stroke="#c9c9d6" stroke-width="2"/>'
    '<circle cx="50" cy="66" r="9" fill="#ffb3a0" stroke="#c46a50" stroke-width="2"/>')
add(C, "mitten",
    '<path d="M28 74V36C28 18 64 14 66 34L68 46C72 38 82 38 84 46C86 56 76 66 70 74Z" fill="#2a7de1" stroke="#0b2a6b" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="24" y="72" width="50" height="20" rx="5" fill="#fff" stroke="#c9c9d6" stroke-width="2.5"/>'
    + "".join(f'<polygon points="{pts(star(x, y, 5, 2, 6, 0))}" fill="#fff"/>' for x, y in ((40, 40), (54, 52), (40, 60), (56, 32)))
    + '<path d="M28 66H70" stroke="#fff" stroke-width="3" stroke-dasharray="4 4"/>')
add(C, "reindeer",
    '<g fill="none" stroke="#7a4514" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M36 34L26 18L14 14M26 18L22 6M30 26L18 26"/><path d="M64 34L74 18L86 14M74 18L78 6M70 26L82 26"/></g>'
    '<ellipse cx="22" cy="44" rx="10" ry="6" fill="#a56b30" stroke="#6b3a14" stroke-width="2" transform="rotate(-25 22 44)"/>'
    '<ellipse cx="78" cy="44" rx="10" ry="6" fill="#a56b30" stroke="#6b3a14" stroke-width="2" transform="rotate(25 78 44)"/>'
    '<path d="M30 46C30 30 70 30 70 46C70 62 64 90 50 90S30 62 30 46Z" fill="#a56b30" stroke="#6b3a14" stroke-width="3"/>'
    '<ellipse cx="50" cy="74" rx="14" ry="12" fill="#d9a873"/>'
    '<circle cx="41" cy="50" r="4" fill="#222"/><circle cx="59" cy="50" r="4" fill="#222"/><circle cx="42" cy="49" r="1.3" fill="#fff"/><circle cx="60" cy="49" r="1.3" fill="#fff"/>'
    '<circle cx="50" cy="70" r="9" fill="#e8262e" stroke="#7a0010" stroke-width="2"/><circle cx="47" cy="67" r="2.5" fill="#fff" fill-opacity=".7"/>')
add(C, "jingle_bells",
    '<path d="M30 30C36 22 44 20 50 24C56 20 64 22 70 30" fill="none" stroke="#1d8a42" stroke-width="5" stroke-linecap="round"/>'
    '<circle cx="32" cy="58" r="20" fill="#ffc21a" stroke="#a37800" stroke-width="3"/><circle cx="68" cy="58" r="20" fill="#ffc21a" stroke="#a37800" stroke-width="3"/>'
    '<path d="M18 60H46M54 60H82" stroke="#a37800" stroke-width="2.5"/><circle cx="32" cy="68" r="3.5" fill="#6b4a00"/><circle cx="68" cy="68" r="3.5" fill="#6b4a00"/>'
    '<path d="M32 68V78M68 68V78" stroke="#6b4a00" stroke-width="2"/>'
    '<circle cx="25" cy="50" r="4" fill="#fff" fill-opacity=".7"/><circle cx="61" cy="50" r="4" fill="#fff" fill-opacity=".7"/>'
    '<path d="M50 30C40 16 30 22 36 30C40 34 46 32 50 30C54 32 60 34 64 30C70 22 60 16 50 30Z" fill="#e01b2f" stroke="#7a0010" stroke-width="2"/>'
    '<circle cx="50" cy="30" r="4" fill="#e01b2f" stroke="#7a0010" stroke-width="2"/>')
add(C, "snow_globe",
    '<path d="M22 80H78L84 94H16Z" fill="#8a4a1e" stroke="#4a2408" stroke-width="2.5" stroke-linejoin="round"/>'
    '<circle cx="50" cy="46" r="36" fill="#cfe9ff" fill-opacity=".7" stroke="#8fb6d9" stroke-width="3"/>'
    '<path d="M20 64C30 58 70 58 80 64A36 36 0 0 1 20 64Z" fill="#fff"/>'
    '<polygon points="50,30 62,50 56,50 66,62 34,62 44,50 38,50" fill="#1d8a42"/><rect x="47" y="62" width="6" height="5" fill="#7a4d17"/>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="1.8" fill="#fff"/>' for x, y in ((30, 30), (40, 20), (62, 22), (70, 36), (26, 46), (74, 50), (52, 16), (36, 40)))
    + '<path d="M30 22C34 16 40 13 46 12" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".8"/>')
add(C, "christmas_star",
    f'<polygon points="{pts(star(50, 50, 46, 18, 5))}" fill="#ffd21f" stroke="#a37800" stroke-width="3" stroke-linejoin="round"/>'
    + "".join(f'<polygon points="{pts([(50, 50), polar(50, 50, 46, a), polar(50, 50, 18, a + 36)])}" fill="#fff3a6"/>' for a in range(-90, 270, 72))
    + "".join(f'<circle cx="{polar(50, 50, 48, a)[0]:.1f}" cy="{polar(50, 50, 48, a)[1]:.1f}" r="2.5" fill="#fff8d0"/>' for a in range(-54, 306, 72)))
add(C, "pine_cone",
    '<path d="M50 6V14" stroke="#4a2c0c" stroke-width="3"/>'
    '<path d="M50 12C70 16 80 44 72 68C66 86 56 94 50 94C44 94 34 86 28 68C20 44 30 16 50 12Z" fill="#7a4d17" stroke="#4a2c0c" stroke-width="3"/>'
    + "".join(f'<path d="M{50 - w} {y}Q50 {y + 9} {50 + w} {y}" fill="#a56b30" stroke="#4a2c0c" stroke-width="2"/>' for y, w in ((24, 12), (34, 18), (44, 21), (54, 22), (64, 20), (74, 16), (84, 9)))
    + '<path d="M44 10C38 4 30 6 28 12M56 10C62 4 70 6 72 12" fill="none" stroke="#2fa651" stroke-width="3" stroke-linecap="round"/>')

# =============================================================== evaQ8
E = "evaq8"
GREEN, RED, YEL, BLUE = "#009a44", "#d7141a", "#f9c300", "#005eb8"


def runner(color="#fff", tf="", w=9):
    """Running figure facing right, roughly in a 20..80 box."""
    return (f'<g transform="{tf}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round">'
            f'<circle cx="62" cy="16" r="7.5" fill="{color}" stroke="none"/>'
            '<path d="M56 30L46 52"/><path d="M55 32L66 42L76 38"/><path d="M53 33L42 38L34 31"/>'
            '<path d="M46 52L60 62L60 80"/><path d="M46 52L38 68L24 70"/></g>')


def person(cx, top, s, color="#fff"):
    return (f'<circle cx="{cx}" cy="{top + 4 * s}" r="{4 * s}" fill="{color}"/>'
            f'<path d="M{cx - 6 * s} {top + 22 * s}V{top + 14 * s}A{6 * s} {6 * s} 0 0 1 {cx + 6 * s} {top + 14 * s}V{top + 22 * s}Z" fill="{color}"/>')


def board(color, inner, rx=8):
    return f'<rect x="4" y="4" width="92" height="92" rx="{rx}" fill="{color}"/><rect x="4" y="4" width="92" height="92" rx="{rx}" fill="none" stroke="#fff" stroke-width="3" stroke-opacity=".9"/>' + inner


arrow_r = '<path d="M18 50H70M54 30L76 50L54 70" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="square" stroke-linejoin="miter"/>'
add(E, "exit_sign", board(GREEN,
    '<rect x="62" y="16" width="26" height="68" fill="none" stroke="#fff" stroke-width="6"/>'
    '<path d="M68 84V22L84 30V84" fill="#fff" fill-opacity=".25"/>'
    + runner("#fff", "translate(-6 12) scale(.8)", 10)))
add(E, "exit_sign_left", board(GREEN,
    '<rect x="12" y="16" width="26" height="68" fill="none" stroke="#fff" stroke-width="6"/>'
    + runner("#fff", "translate(106 12) scale(-.8 .8)", 10)))
add(E, "exit_arrow", board(GREEN, arrow_r))
add(E, "exit_arrow_up", board(GREEN, f'<g transform="rotate(-90 50 50)">{arrow_r}</g>'))
add(E, "exit_arrow_diagonal", board(GREEN, f'<g transform="rotate(-45 50 50)">{arrow_r}</g>'))
add(E, "exit_stairs", board(GREEN,
    '<path d="M12 88V74H30V60H48V46H66V32H88" fill="none" stroke="#fff" stroke-width="6" stroke-linejoin="miter"/>'
    + runner("#fff", "translate(10 4) scale(.6)", 12)))
asm = "".join(f'<g transform="rotate({a} 50 50)"><path d="M14 14L30 30" stroke="#fff" stroke-width="6"/><polygon points="34,34 20,32 32,20" fill="#fff"/></g>' for a in (0, 90, 180, 270))
add(E, "assembly_point", board(GREEN, asm + person(40, 38, 1.05) + person(60, 38, 1.05) + person(50, 46, 1.15)))
add(E, "first_aid", board(GREEN, '<path d="M38 16H62V38H84V62H62V84H38V62H16V38H38Z" fill="#fff"/>'))
add(E, "defibrillator", board(GREEN,
    f'<path d="{heart}" fill="#fff" transform="translate(50 54) scale(.72) translate(-50 -50)"/>'
    '<polygon points="54,30 38,58 50,58 44,80 64,48 52,48 58,30" fill="' + GREEN + '"/>'
    '<path d="M76 12V28M68 20H84" stroke="#fff" stroke-width="5"/>'))
add(E, "emergency_phone", board(GREEN,
    '<path d="M24 30C22 24 26 18 32 18H38L44 32L36 38C40 50 50 60 62 64L68 56L82 62V68C82 74 76 78 70 76C46 70 30 54 24 30Z" fill="#fff"/>'
    '<path d="M70 14V34M60 24H80" stroke="#fff" stroke-width="5"/>'))
add(E, "eyewash", board(GREEN,
    '<path d="M18 52C28 36 48 30 64 40C56 48 44 56 18 52Z" fill="#fff"/><circle cx="42" cy="46" r="6" fill="' + GREEN + '"/>'
    + "".join(f'<path d="M{x} 86C{x} 76 {x + 6} 68 {x + 10} 62" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>' for x in (34, 46, 58))
    + '<rect x="30" y="84" width="40" height="6" fill="#fff"/>'))
add(E, "safety_shower", board(GREEN,
    '<path d="M28 18H62V28" fill="none" stroke="#fff" stroke-width="6"/><path d="M48 28H76L70 36H54Z" fill="#fff"/>'
    + "".join(f'<path d="M{x} 42L{x - 4} 54" stroke="#fff" stroke-width="3" stroke-linecap="round"/>' for x in (56, 62, 68, 74))
    + person(56, 56, 1.25)))
# --- fire equipment (red signs)
ext_white = ('<path d="M40 28H52V22H44V18H58V28H60C64 28 66 32 66 36V84C66 88 64 90 60 90H40C36 90 34 88 34 84V36C34 32 36 28 40 28Z" fill="#fff"/>'
             '<path d="M58 22C70 20 76 26 78 36" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>')
flame_w = "M78 52C84 58 86 66 82 72C80 76 74 78 70 76C66 72 68 66 72 62C70 68 74 70 76 66C78 62 76 58 78 52Z"
add(E, "fire_extinguisher_sign", board(RED, f'<g transform="translate(-10 0)">{ext_white}</g><path d="{flame_w}" fill="#fff" transform="translate(-2 -10) scale(1.2) translate(-8 -6)"/>'))
reel = "".join(f'<circle cx="44" cy="46" r="{r}" fill="none" stroke="#fff" stroke-width="3"/>' for r in (10, 17, 24))
add(E, "fire_hose_sign", board(RED, reel + '<circle cx="44" cy="46" r="5" fill="#fff"/>'
    '<path d="M68 46C82 48 84 64 78 74L70 86" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>'
    '<polygon points="64,84 76,90 70,94 60,88" fill="#fff"/>'))
add(E, "fire_alarm_sign", board(RED,
    '<rect x="16" y="20" width="44" height="44" rx="4" fill="none" stroke="#fff" stroke-width="5"/>'
    '<circle cx="38" cy="42" r="9" fill="#fff"/>'
    '<path d="M50 56L50 34A5 5 0 0 1 60 34V52L72 54C78 55 82 60 80 66L76 82C75 86 72 88 68 88H56C52 88 50 86 48 84L38 70C36 66 40 62 44 64L50 68Z" fill="#fff" stroke="' + RED + '" stroke-width="2.5" stroke-linejoin="round"/>'
    '<path d="M70 16L76 10M78 26L86 24M64 12L64 4" stroke="#fff" stroke-width="3.5" stroke-linecap="round"/>'))
add(E, "fire_ladder_sign", board(RED,
    '<path d="M34 14L26 88M66 14L74 88" stroke="#fff" stroke-width="6" stroke-linecap="round"/>'
    + "".join(f'<path d="M{33 - i * 1.1:.1f} {22 + i * 13}H{67 + i * 1.1:.1f}" stroke="#fff" stroke-width="5"/>' for i in range(6))))
add(E, "fire_phone_sign", board(RED,
    '<path d="M24 34C22 28 26 22 32 22H38L44 36L36 42C40 54 50 64 62 68L68 60L82 66V72C82 78 76 82 70 80C46 74 30 58 24 34Z" fill="#fff"/>'
    f'<path d="{flame_w}" fill="#fff" transform="translate(-6 -48) scale(1.1)"/>'))
# --- prohibition
def prohibition(inner):
    return (f'<circle cx="50" cy="50" r="44" fill="#fff"/>{inner}'
            f'<circle cx="50" cy="50" r="40" fill="none" stroke="{RED}" stroke-width="9"/>'
            f'<path d="M22 22L78 78" stroke="{RED}" stroke-width="9"/>')


add(E, "no_smoking", prohibition(
    '<rect x="16" y="50" width="56" height="12" fill="#222"/><rect x="62" y="50" width="10" height="12" fill="#e06a00"/>'
    '<path d="M78 46C72 40 82 34 76 26M86 46C80 40 90 34 84 26" fill="none" stroke="#666" stroke-width="3.5" stroke-linecap="round"/>'))
add(E, "no_open_flame", prohibition(
    '<path d="M50 22C62 36 66 50 60 62C56 70 44 70 40 62C36 54 42 46 46 42C44 50 48 54 52 50C56 44 52 32 50 22Z" fill="#222"/>'
    '<rect x="47" y="70" width="6" height="16" fill="#222"/>'))
add(E, "no_lift_in_fire", prohibition(
    '<rect x="28" y="22" width="44" height="58" fill="none" stroke="#222" stroke-width="4"/>'
    '<path d="M50 22V80" stroke="#222" stroke-width="3"/>'
    '<polygon points="40,30 46,38 34,38" fill="#222"/><polygon points="60,38 66,30 54,30" fill="#222"/>'
    '<path d="M36 76C30 70 32 62 38 58C38 64 42 64 42 60C42 54 46 52 48 48C52 56 54 64 50 72C48 76 40 78 36 76Z" fill="#222"/>'))
add(E, "no_entry", prohibition(person(50, 26, 2.1, "#222")))
add(E, "do_not_block", prohibition(
    '<rect x="24" y="22" width="40" height="60" fill="none" stroke="#222" stroke-width="5"/>'
    '<rect x="44" y="52" width="34" height="30" fill="#222"/><path d="M44 62H78" stroke="#fff" stroke-width="2"/>'))
# --- warnings
def warning(inner):
    return (f'<path d="M50 8L94 88H6Z" fill="{YEL}" stroke="#222" stroke-width="7" stroke-linejoin="round"/>{inner}')


add(E, "warning_fire", warning(
    '<path d="M50 34C62 46 66 58 60 70C56 78 44 78 40 70C36 62 42 54 46 50C44 58 48 62 52 58C56 52 52 42 50 34Z" fill="#222"/>'
    '<rect x="32" y="76" width="36" height="5" fill="#222"/>'))
add(E, "warning_general", warning('<rect x="45" y="36" width="10" height="28" rx="3" fill="#222"/><circle cx="50" cy="73" r="5.5" fill="#222"/>'))
add(E, "warning_explosive", warning(
    f'<polygon points="{pts(star(50, 62, 18, 8, 8, -90))}" fill="#222"/><circle cx="50" cy="62" r="6" fill="{YEL}"/>'))
add(E, "warning_electric", warning('<polygon points="54,30 38,62 50,62 44,82 64,50 52,50 58,30" fill="#222"/>'))
add(E, "warning_smoke", warning(
    '<path d="M30 76C24 76 22 68 28 66C26 58 36 56 40 60C42 52 54 52 56 60C60 56 70 58 70 66C76 68 74 76 68 76Z" fill="#222"/>'
    '<path d="M44 52C40 46 46 42 44 36M54 50C50 44 56 40 54 34" fill="none" stroke="#222" stroke-width="3" stroke-linecap="round"/>'))
# --- mandatory (blue)
add(E, "mandatory_fire_door_closed", f'<circle cx="50" cy="50" r="44" fill="{BLUE}"/>'
    '<rect x="30" y="20" width="40" height="60" fill="none" stroke="#fff" stroke-width="5"/><circle cx="62" cy="52" r="3.5" fill="#fff"/>'
    '<path d="M40 88H60M44 84L40 88L44 92M56 84L60 88L56 92" fill="none" stroke="#fff" stroke-width="3"/>')
# --- objects
add(E, "fire_extinguisher",
    '<path d="M38 18H56V12H44V8H62V18H62V24" fill="#333" stroke="#111" stroke-width="2" stroke-linejoin="round"/>'
    '<path d="M60 14C78 12 86 22 86 36L82 52" fill="none" stroke="#222" stroke-width="5" stroke-linecap="round"/><path d="M78 50L88 56L82 62Z" fill="#222"/>'
    '<path d="M36 24H64C68 24 70 28 70 32V88C70 92 68 94 64 94H36C32 94 30 92 30 88V32C30 28 32 24 36 24Z" fill="' + RED + '" stroke="#7a0010" stroke-width="3"/>'
    '<rect x="34" y="44" width="32" height="26" rx="2" fill="#fff"/><path d="M38 52H62M38 58H62M38 64H54" stroke="#999" stroke-width="2"/>'
    '<circle cx="42" cy="30" r="0" fill="none"/><rect x="36" y="28" width="6" height="58" rx="3" fill="#fff" fill-opacity=".35"/>'
    '<circle cx="50" cy="16" r="5" fill="#fff" stroke="#333" stroke-width="2"/><path d="M50 16L53 13" stroke="' + RED + '" stroke-width="1.5"/>')
add(E, "smoke_detector",
    '<circle cx="50" cy="50" r="42" fill="#f4f5f7" stroke="#b5bac2" stroke-width="3"/>'
    '<circle cx="50" cy="50" r="30" fill="none" stroke="#d6d9de" stroke-width="2"/>'
    + "".join(f'<rect x="{polar(50, 50, 22, a)[0] - 6:.1f}" y="{polar(50, 50, 22, a)[1] - 1.5:.1f}" width="12" height="3" rx="1.5" fill="#b5bac2" transform="rotate({a} {polar(50, 50, 22, a)[0]:.1f} {polar(50, 50, 22, a)[1]:.1f})"/>' for a in range(0, 360, 30))
    + '<circle cx="50" cy="50" r="10" fill="#e6e8eb" stroke="#b5bac2" stroke-width="2"/><circle cx="64" cy="36" r="4" fill="#ff2a2a"/><circle cx="64" cy="36" r="7" fill="#ff2a2a" fill-opacity=".25"/>')
add(E, "fire_blanket",
    '<rect x="16" y="12" width="68" height="78" rx="6" fill="' + RED + '" stroke="#7a0010" stroke-width="3"/>'
    '<rect x="24" y="22" width="52" height="40" rx="3" fill="#fff"/>'
    '<path d="M30 54Q50 30 70 54" fill="none" stroke="' + RED + '" stroke-width="5"/><path d="M50 30C56 36 58 42 54 48C52 50 48 50 46 48C42 42 46 38 50 30Z" fill="' + RED + '"/>'
    '<rect x="26" y="88" width="14" height="10" rx="3" fill="#222"/><rect x="60" y="88" width="14" height="10" rx="3" fill="#222"/>'
    '<path d="M33 90V80M67 90V80" stroke="#222" stroke-width="3"/>')
add(E, "fire_hydrant",
    '<rect x="28" y="84" width="44" height="10" rx="2" fill="#a30f14"/>'
    '<path d="M34 84V36A16 16 0 0 1 66 36V84Z" fill="' + RED + '" stroke="#7a0010" stroke-width="3"/>'
    '<rect x="28" y="34" width="44" height="8" rx="3" fill="#a30f14"/><rect x="44" y="12" width="12" height="8" rx="2" fill="#a30f14"/>'
    '<rect x="16" y="52" width="18" height="16" rx="3" fill="#a30f14"/><rect x="66" y="52" width="18" height="16" rx="3" fill="#a30f14"/>'
    '<circle cx="50" cy="60" r="9" fill="#a30f14" stroke="#7a0010" stroke-width="2"/><circle cx="50" cy="60" r="3" fill="#ffd2d2"/>'
    '<rect x="38" y="46" width="5" height="34" rx="2.5" fill="#fff" fill-opacity=".3"/>')
add(E, "flame",
    '<path d="M50 6C66 24 84 40 80 64C78 82 64 94 50 94S22 84 20 66C18 50 28 40 34 32C34 44 40 50 46 46C52 40 46 22 50 6Z" fill="#ff4a1a" stroke="#b31f00" stroke-width="3"/>'
    '<path d="M52 36C62 50 70 60 66 74C64 84 56 88 50 88S36 84 34 74C33 64 38 58 42 54C42 62 46 66 50 62C54 56 50 46 52 36Z" fill="#ffa21f"/>'
    '<path d="M50 60C56 68 60 74 56 82C54 86 46 86 44 82C42 76 46 72 50 60Z" fill="#ffe36b"/>')
add(E, "firefighter_helmet",
    '<path d="M8 72C8 64 16 60 24 60H76C84 60 92 64 92 72Z" fill="#1a1a1a"/>'
    '<path d="M18 64C18 34 32 16 50 16S82 34 82 64Z" fill="' + YEL + '" stroke="#8a6a00" stroke-width="3"/>'
    '<path d="M50 16V64M34 22C30 34 28 48 28 64M66 22C70 34 72 48 72 64" fill="none" stroke="#c99a00" stroke-width="3"/>'
    '<path d="M38 46H62L64 60H36Z" fill="#c0c4ca" stroke="#5a6570" stroke-width="2"/><path d="M50 48V58" stroke="' + RED + '" stroke-width="3"/>'
    '<path d="M14 72H86" stroke="#eaff00" stroke-width="3"/>')
add(E, "fire_truck",
    '<rect x="6" y="38" width="60" height="38" rx="3" fill="' + RED + '" stroke="#7a0010" stroke-width="2.5"/>'
    '<path d="M66 46H82L94 62V76H66Z" fill="' + RED + '" stroke="#7a0010" stroke-width="2.5" stroke-linejoin="round"/>'
    '<path d="M70 50H81L89 62H70Z" fill="#bfe3ff" stroke="#5a6570" stroke-width="2"/>'
    '<path d="M10 30L62 18M10 36L62 24" stroke="#c0c4ca" stroke-width="3"/>'
    + "".join(f'<path d="M{14 + i * 9} {28.2 - i * 2.08:.1f}L{14 + i * 9} {34.2 - i * 2.08:.1f}" stroke="#c0c4ca" stroke-width="2.5"/>' for i in range(6))
    + '<rect x="12" y="46" width="22" height="14" rx="2" fill="#fff" fill-opacity=".85"/><rect x="38" y="46" width="22" height="14" rx="2" fill="#fff" fill-opacity=".85"/>'
    '<path d="M6 66H94" stroke="#fff" stroke-width="3"/>'
    '<rect x="72" y="40" width="10" height="6" rx="2" fill="#2a7de1"/>'
    '<circle cx="24" cy="78" r="9" fill="#222"/><circle cx="24" cy="78" r="4" fill="#aaa"/><circle cx="78" cy="78" r="9" fill="#222"/><circle cx="78" cy="78" r="4" fill="#aaa"/>')
add(E, "sprinkler",
    '<rect x="40" y="6" width="20" height="16" rx="2" fill="#b08a2e" stroke="#6b5214" stroke-width="2"/>'
    '<path d="M42 22L36 60H64L58 22Z" fill="#d9b35a" stroke="#6b5214" stroke-width="2.5" stroke-linejoin="round"/>'
    '<rect x="45" y="30" width="10" height="22" rx="5" fill="' + RED + '" fill-opacity=".85" stroke="#7a0010" stroke-width="1.5"/>'
    '<path d="M20 64H80" stroke="#6b5214" stroke-width="5" stroke-linecap="round"/>'
    + "".join(f'<path d="M{50 + dx} 70L{50 + dx * 2.2:.0f} 92" stroke="#3fa9ff" stroke-width="3" stroke-linecap="round"/>' for dx in (-16, -8, 0, 8, 16)))
add(E, "fire_axe",
    '<g transform="rotate(-35 50 50)"><rect x="46" y="20" width="8" height="76" rx="3" fill="#c8813c" stroke="#6b3a14" stroke-width="2"/>'
    '<path d="M54 22H70C80 22 86 30 86 40C80 36 72 36 66 38H54Z" fill="#c0c4ca" stroke="#5a6570" stroke-width="2.5" stroke-linejoin="round"/>'
    '<path d="M46 24L26 18L30 34L46 32Z" fill="#c0c4ca" stroke="#5a6570" stroke-width="2.5" stroke-linejoin="round"/>'
    '<rect x="44" y="18" width="12" height="22" rx="2" fill="' + RED + '" stroke="#7a0010" stroke-width="2"/></g>')
add(E, "hi_vis_vest",
    '<path d="M30 10L42 10L50 30L58 10L70 10L84 24L80 92H20L16 24Z" fill="#ff8a00" stroke="#a34a00" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M20 58H80M20 74H80" stroke="#e6e8eb" stroke-width="7"/><path d="M20 58H80M20 74H80" stroke="#fff" stroke-width="3"/>'
    '<path d="M50 30V92" stroke="#a34a00" stroke-width="2"/>'
    '<path d="M34 10L36 58M66 10L64 58" stroke="#fff" stroke-width="5"/>')
add(E, "megaphone",
    '<path d="M18 40H32L76 16V84L32 60H18Z" fill="' + RED + '" stroke="#7a0010" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="10" y="38" width="12" height="24" rx="3" fill="#f2f4f7" stroke="#5a6570" stroke-width="2.5"/>'
    '<path d="M34 60L40 84H52L46 64" fill="#5a6570"/>'
    '<path d="M84 36C90 44 90 56 84 64M90 28C98 40 98 60 90 72" fill="none" stroke="#5a6570" stroke-width="3.5" stroke-linecap="round"/>')
add(E, "flashlight",
    '<g transform="rotate(-30 50 50)"><path d="M50 50L96 30V70Z" fill="#fff6b0" fill-opacity=".7"/>'
    '<rect x="8" y="40" width="38" height="20" rx="4" fill="' + YEL + '" stroke="#8a6a00" stroke-width="2.5"/>'
    '<path d="M46 36H56V64H46Z" fill="#333" stroke="#111" stroke-width="2"/><rect x="20" y="44" width="8" height="12" rx="2" fill="#333"/></g>')
add(E, "alarm_bell",
    '<circle cx="50" cy="50" r="40" fill="' + RED + '" stroke="#7a0010" stroke-width="3"/>'
    '<circle cx="50" cy="50" r="30" fill="#ff4a4a"/><circle cx="50" cy="50" r="8" fill="#c0c4ca" stroke="#5a6570" stroke-width="2"/>'
    '<path d="M40 30C44 26 50 24 56 26" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".7"/>'
    '<path d="M50 90V96" stroke="#5a6570" stroke-width="4"/>'
    '<path d="M6 30L14 34M4 50H12M94 50H86M92 30L84 34" stroke="' + RED + '" stroke-width="3" stroke-linecap="round"/>')
add(E, "fire_bucket",
    '<path d="M50 12C30 12 22 18 22 22" fill="none" stroke="#5a6570" stroke-width="3"/><path d="M50 12C70 12 78 18 78 22" fill="none" stroke="#5a6570" stroke-width="3"/>'
    '<path d="M16 24H84L72 90H28Z" fill="' + RED + '" stroke="#7a0010" stroke-width="3" stroke-linejoin="round"/>'
    '<ellipse cx="50" cy="24" rx="34" ry="5" fill="#a30f14" stroke="#7a0010" stroke-width="2"/>'
    '<text x="50" y="62" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-weight="900" font-size="17" fill="#fff">FIRE</text>')
add(E, "call_point",
    '<rect x="12" y="12" width="76" height="76" rx="6" fill="' + RED + '" stroke="#7a0010" stroke-width="3"/>'
    '<rect x="26" y="26" width="48" height="48" rx="2" fill="#fff" stroke="#9aa0a6" stroke-width="2"/>'
    '<path d="M30 64L66 34" stroke="#c9cdd2" stroke-width="2"/>'
    + "".join(f'<rect x="{36 + i * 8}" y="{40 + (i % 2) * 6}" width="5" height="16" rx="2.5" fill="#d7141a" fill-opacity=".85"/>' for i in range(4))
    + '<rect x="26" y="26" width="48" height="48" rx="2" fill="none" stroke="#5a6570" stroke-width="1.5"/>'
    '<circle cx="18" cy="18" r="2" fill="#7a0010"/><circle cx="82" cy="18" r="2" fill="#7a0010"/><circle cx="18" cy="82" r="2" fill="#7a0010"/><circle cx="82" cy="82" r="2" fill="#7a0010"/>')
add(E, "emergency_light",
    '<rect x="6" y="28" width="88" height="44" rx="6" fill="#f2f4f7" stroke="#9aa0a6" stroke-width="3"/>'
    f'<rect x="12" y="34" width="76" height="32" rx="2" fill="{GREEN}"/>'
    '<rect x="64" y="38" width="18" height="24" fill="none" stroke="#fff" stroke-width="3"/>'
    + runner("#fff", "translate(16 36) scale(.34)", 14)
    + '<path d="M40 44H56M50 38L58 44L50 50" fill="none" stroke="#fff" stroke-width="3.5"/>')
add(E, "you_are_here",
    '<circle cx="50" cy="50" r="44" fill="' + RED + '" fill-opacity=".18"/><circle cx="50" cy="50" r="30" fill="' + RED + '" fill-opacity=".25"/>'
    '<circle cx="50" cy="50" r="16" fill="' + RED + '" stroke="#fff" stroke-width="5"/>')
add(E, "fire_door",
    '<rect x="16" y="8" width="68" height="88" rx="2" fill="#8a96a3" stroke="#4a5560" stroke-width="3"/>'
    '<rect x="24" y="14" width="52" height="82" fill="#c0c8d0" stroke="#4a5560" stroke-width="2"/>'
    '<rect x="40" y="20" width="20" height="26" fill="#d9eefc" stroke="#4a5560" stroke-width="2"/><path d="M40 28H60M40 38H60M50 20V46" stroke="#9aa0a6" stroke-width="1"/>'
    '<rect x="26" y="56" width="16" height="4" rx="2" fill="#333"/>'
    f'<circle cx="50" cy="72" r="11" fill="{BLUE}"/><text x="50" y="76" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-weight="900" font-size="8" fill="#fff">EI60</text>'
    '<path d="M24 8L36 2H64L76 8" fill="none" stroke="#4a5560" stroke-width="3"/>')
add(E, "smoke_cloud",
    '<path d="M24 76C12 76 6 66 12 58C6 48 16 38 26 42C28 30 42 26 50 34C56 24 72 26 74 38C86 36 94 48 88 58C96 66 88 78 78 76Z" fill="#8a929c" stroke="#5a6570" stroke-width="3"/>'
    '<path d="M30 56C36 50 44 52 46 58M58 48C64 44 72 46 72 54" fill="none" stroke="#b5bcc4" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M40 76C38 84 44 88 40 96M60 76C58 84 64 88 60 96" fill="none" stroke="#8a929c" stroke-width="4" stroke-linecap="round"/>')
add(E, "evacuation_chair",
    '<path d="M4 96V84H24V72H44V60H64V48H84V36H96V96Z" fill="#c9ced6"/>'
    '<path d="M4 84H24V72H44V60H64V48H84V36H96" fill="none" stroke="#8a929c" stroke-width="2"/>'
    '<g transform="rotate(-28 50 60)">'
    '<path d="M30 10H48" stroke="#222" stroke-width="5" stroke-linecap="round"/>'
    '<path d="M38 10V76H70" fill="none" stroke="#5a6570" stroke-width="5" stroke-linejoin="round"/>'
    '<path d="M64 60V76" stroke="#5a6570" stroke-width="5"/>'
    f'<rect x="40" y="18" width="11" height="40" rx="3" fill="{YEL}" stroke="#8a6a00" stroke-width="2"/>'
    f'<rect x="40" y="52" width="30" height="10" rx="3" fill="{YEL}" stroke="#8a6a00" stroke-width="2"/>'
    '<rect x="30" y="74" width="46" height="9" rx="4.5" fill="#222"/>'
    '<circle cx="35" cy="78.5" r="5" fill="#555" stroke="#222" stroke-width="2"/><circle cx="71" cy="78.5" r="5" fill="#555" stroke="#222" stroke-width="2"/>'
    '</g>')

# --------------------------------------------------------------- write
for (cat, name), svg in P.items():
    d = os.path.join(OUT, cat)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".svg"), "w") as f:
        f.write(svg)
print(len([k for k in P if k[0] == C]), "christmas,", len([k for k in P if k[0] == E]), "evaq8")
