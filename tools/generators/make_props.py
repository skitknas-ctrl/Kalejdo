# Historik: det här skriptet ritade de inbyggda prylarna i props/. SVG-filerna i props/ är källan nu.
# Kör inte rakt av, eftersom det skriver över befintliga filer. Använd det som mall för nya prylar i samma stil.
# Användning: python tools/generators/make_props.py <utmapp>
"""Generates the starter SVG library for Kalejdo into <out>/props/<category>/<name>.svg."""
import math, os, random, sys

OUT = os.path.join(sys.argv[1], "props")
P = {}


def svg(body, defs=""):
    d = f"<defs>{defs}</defs>" if defs else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">'
            f"{d}{body}</svg>\n")


def add(cat, name, body, defs=""):
    P[(cat, name)] = svg(body, defs)


def pts(lst):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in lst)


def polar(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def star(cx, cy, R, r, n, rot=-90):
    return [polar(cx, cy, R if i % 2 == 0 else r, rot + i * 180 / n) for i in range(2 * n)]


def ngon(cx, cy, r, n, rot=-90):
    return [polar(cx, cy, r, rot + i * 360 / n) for i in range(n)]


def shrink(poly, f, dx=0, dy=0):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return [(cx + (x - cx) * f + dx, cy + (y - cy) * f + dy) for x, y in poly]


def sector(cx, cy, r, a0, a1):
    x0, y0 = polar(cx, cy, r, a0)
    x1, y1 = polar(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return f"M{cx:.1f} {cy:.1f}L{x0:.1f} {y0:.1f}A{r} {r} 0 {large} 1 {x1:.1f} {y1:.1f}Z"


def ring_path(cx, cy, R, r):
    return (f"M{cx-R} {cy}a{R} {R} 0 1 0 {2*R} 0a{R} {R} 0 1 0 {-2*R} 0Z"
            f"M{cx-r} {cy}a{r} {r} 0 1 0 {2*r} 0a{r} {r} 0 1 0 {-2*r} 0Z")


SC = lambda f: f'transform="translate(50 50) scale({f}) translate(-50 -50)"'

# ---------------------------------------------------------------- glass
def shard(name, poly, col, hi):
    add("glass", name,
        f'<polygon points="{pts(poly)}" fill="{col}" fill-opacity=".62" stroke="{hi}" stroke-width="2.5" stroke-linejoin="round"/>'
        f'<polygon points="{pts(shrink(poly, .45, -6, -6))}" fill="#fff" fill-opacity=".22"/>')

shard("shard_red", [(14, 80), (48, 10), (88, 70)], "#ff2d55", "#ffa3b6")
shard("shard_blue", [(10, 40), (60, 8), (90, 54), (44, 92)], "#2f7bff", "#a8c8ff")
shard("shard_green", [(16, 18), (84, 30), (48, 90)], "#1fc45a", "#a3f0bf")
shard("shard_amber", [(8, 56), (44, 14), (92, 34), (70, 86)], "#ffae00", "#ffe08a")
shard("shard_violet", [(30, 8), (92, 62), (12, 86)], "#9b5cff", "#d4bcff")
shard("shard_cyan", ngon(50, 52, 42, 5), "#13cfe2", "#a6f3fb")
shard("shard_pink", [(20, 10), (80, 10), (90, 50), (50, 92), (10, 50)], "#ff5fc8", "#ffc4ec")
shard("shard_lime", [(6, 70), (40, 20), (94, 44)], "#a6e22e", "#e1ff9e")


def bead(name, col, dark):
    defs = (f'<radialGradient id="g" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".95"/>'
            f'<stop offset=".35" stop-color="{col}"/><stop offset="1" stop-color="{dark}"/></radialGradient>')
    add("glass", name, f'<circle cx="50" cy="50" r="40" fill="url(#g)" fill-opacity=".88"/>'
        f'<circle cx="50" cy="50" r="9" fill="{dark}" fill-opacity=".75"/>', defs)

bead("bead_red", "#ff4040", "#8a0010")
bead("bead_blue", "#3d8bff", "#0a2a80")
bead("bead_gold", "#ffcc33", "#9a6400")
bead("bead_green", "#2ed47a", "#05582a")

add("glass", "glass_rod",
    '<g transform="rotate(-35 50 50)"><rect x="8" y="37" width="84" height="26" rx="13" fill="#ff7a00" fill-opacity=".6" stroke="#ffc08a" stroke-width="2.5"/>'
    '<rect x="18" y="42" width="62" height="6" rx="3" fill="#fff" fill-opacity=".5"/></g>')
add("glass", "glass_rod_blue",
    '<g transform="rotate(40 50 50)"><rect x="12" y="39" width="76" height="22" rx="11" fill="#2bb7ff" fill-opacity=".6" stroke="#b5e6ff" stroke-width="2.5"/>'
    '<rect x="20" y="43" width="56" height="5" rx="2.5" fill="#fff" fill-opacity=".5"/></g>')
add("glass", "sequin_gold",
    f'<path d="{ring_path(50, 50, 40, 9)}" fill="#ffc21a" fill-rule="evenodd" stroke="#fff3b0" stroke-width="2"/>'
    f'<path d="{ring_path(50, 50, 30, 18)}" fill="#fff" fill-opacity=".25" fill-rule="evenodd"/>')
add("glass", "sequin_holo",
    '<defs><linearGradient id="h" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ff7ad9"/><stop offset=".33" stop-color="#7ae0ff"/>'
    '<stop offset=".66" stop-color="#b6ff7a"/><stop offset="1" stop-color="#ffd27a"/></linearGradient></defs>'
    f'<path d="{ring_path(50, 50, 40, 8)}" fill="url(#h)" fill-rule="evenodd" stroke="#fff" stroke-width="2"/>')
add("glass", "glass_drop",
    '<path d="M50 6C66 34 80 50 80 64A30 30 0 0 1 20 64C20 50 34 34 50 6Z" fill="#18c9b0" fill-opacity=".6" stroke="#aaf5ea" stroke-width="2.5"/>'
    '<path d="M40 56C40 48 45 42 48 38C46 48 46 54 48 62Z" fill="#fff" fill-opacity=".5"/>')
add("glass", "glass_moon",
    '<path d="M62 8A42 42 0 1 0 92 70A34 34 0 1 1 62 8Z" fill="#ff6aa8" fill-opacity=".6" stroke="#ffc6de" stroke-width="2.5"/>')

# ---------------------------------------------------------------- gems
def gem_round(name, c1, c2, c3):
    o = [polar(50, 50, 42, 22.5 + 45 * i) for i in range(8)]
    n = [polar(50, 50, 22, 22.5 + 45 * i) for i in range(8)]
    f = "".join(f'<polygon points="{pts([o[i], o[(i+1)%8], n[(i+1)%8], n[i]])}" fill="{c1 if i % 2 else c2}"/>' for i in range(8))
    add("gems", name, f + f'<polygon points="{pts(n)}" fill="{c3}"/>'
        f'<polygon points="{pts(o)}" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="2" stroke-linejoin="round"/>'
        f'<polygon points="{pts([n[5], n[6], (50, 50)])}" fill="#fff" fill-opacity=".6"/>')

gem_round("ruby", "#b0003a", "#e0115f", "#ff5c93")
gem_round("sapphire", "#0b2f9e", "#1f5fe0", "#6f9cff")
gem_round("topaz", "#c96a00", "#ff9d00", "#ffd166")

add("gems", "emerald",
    '<polygon points="30,10 70,10 82,22 82,78 70,90 30,90 18,78 18,22" fill="#0b7a3e" stroke="#bff5d6" stroke-width="2" stroke-linejoin="round"/>'
    '<polygon points="34,20 66,20 72,26 72,74 66,80 34,80 28,74 28,26" fill="#16a35a"/>'
    '<rect x="36" y="30" width="28" height="40" fill="#45d38a"/>'
    '<path d="M30 10L36 30M70 10L64 30M82 78L64 70M18 78L36 70" stroke="#bff5d6" stroke-opacity=".6" stroke-width="1.5"/>'
    '<polygon points="36,30 52,30 36,50" fill="#fff" fill-opacity=".45"/>')
heart = "M50 88C20 66 8 48 12 32C16 16 38 12 50 30C62 12 84 16 88 32C92 48 80 66 50 88Z"
add("gems", "heart_gem",
    f'<path d="{heart}" fill="#d81b7a" stroke="#ffc2e2" stroke-width="2"/>'
    f'<path d="{heart}" fill="#ff5fae" {SC(.6)}/>'
    '<path d="M50 30L50 88M12 32L36 42L50 30L64 42L88 32" fill="none" stroke="#ffc2e2" stroke-opacity=".6" stroke-width="1.5"/>'
    '<path d="M24 26C30 20 38 22 42 28L30 36Z" fill="#fff" fill-opacity=".55"/>')
drop = "M50 6C64 30 82 46 82 62A32 32 0 0 1 18 62C18 46 36 30 50 6Z"
add("gems", "pear_gem",
    f'<path d="{drop}" fill="#1747c9" stroke="#bcd0ff" stroke-width="2"/>'
    f'<path d="{drop}" fill="#4f7dff" {SC(.58)}/>'
    '<path d="M50 6V94M18 62H82" stroke="#bcd0ff" stroke-opacity=".5" stroke-width="1.5"/>'
    '<path d="M40 40L50 26L48 52Z" fill="#fff" fill-opacity=".55"/>')
mq = "M6 50Q50 -4 94 50Q50 104 6 50Z"
add("gems", "marquise",
    f'<path d="{mq}" fill="#6a1fb5" stroke="#e1c6ff" stroke-width="2"/>'
    f'<path d="{mq}" fill="#a65cff" {SC(.55)}/>'
    '<path d="M6 50H94M50 23V77" stroke="#e1c6ff" stroke-opacity=".55" stroke-width="1.5"/>'
    '<path d="M30 40Q42 30 50 30L42 46Z" fill="#fff" fill-opacity=".5"/>')
tri = [(50, 8), (92, 84), (8, 84)]
add("gems", "trillion",
    f'<polygon points="{pts(tri)}" fill="#d9a400" stroke="#fff2b3" stroke-width="2" stroke-linejoin="round"/>'
    f'<polygon points="{pts(shrink(tri, .5))}" fill="#ffd54a"/>'
    f'<path d="M50 8L50 44M92 84L64 70M8 84L36 70" stroke="#fff2b3" stroke-opacity=".6" stroke-width="1.5"/>'
    '<polygon points="50,44 42,58 50,30" fill="#fff" fill-opacity=".5"/>')
add("gems", "diamond",
    '<polygon points="18,32 34,14 66,14 82,32 50,90" fill="#a8ecff" stroke="#ffffff" stroke-width="2" stroke-linejoin="round"/>'
    '<polygon points="18,32 82,32 50,90" fill="#6fd6f5"/>'
    '<polygon points="34,14 42,32 50,14 58,32 66,14" fill="#d6f7ff"/>'
    '<path d="M18 32H82M42 32L50 90L58 32" fill="none" stroke="#fff" stroke-width="1.5" stroke-opacity=".8"/>')
add("gems", "pearl",
    '<radialGradient id="g" cx=".35" cy=".32" r=".75"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#f3e6ee"/><stop offset="1" stop-color="#c9b3c3"/></radialGradient>'
    .join(["", ""]) and
    '<circle cx="50" cy="50" r="40" fill="url(#g)"/><ellipse cx="38" cy="36" rx="10" ry="6" fill="#fff" fill-opacity=".8" transform="rotate(-35 38 36)"/>',
    '<radialGradient id="g" cx=".35" cy=".32" r=".75"><stop offset="0" stop-color="#ffffff"/><stop offset=".55" stop-color="#f3e6ee"/><stop offset="1" stop-color="#c9b3c3"/></radialGradient>')
add("gems", "opal",
    '<ellipse cx="50" cy="50" rx="34" ry="44" fill="#e9f3ff" stroke="#c9d8f0" stroke-width="2"/>'
    '<circle cx="40" cy="36" r="9" fill="#ff7ac8" fill-opacity=".55"/><circle cx="58" cy="44" r="11" fill="#5fe3c0" fill-opacity=".55"/>'
    '<circle cx="44" cy="62" r="10" fill="#7aa6ff" fill-opacity=".55"/><circle cx="60" cy="70" r="7" fill="#ffd36b" fill-opacity=".6"/>'
    '<circle cx="34" cy="50" r="6" fill="#b884ff" fill-opacity=".55"/>')

# ---------------------------------------------------------------- shapes
add("shapes", "star", f'<polygon points="{pts(star(50, 54, 46, 19, 5))}" fill="#ffcf1f" stroke="#c98700" stroke-width="3" stroke-linejoin="round"/>'
    f'<polygon points="{pts(star(50, 54, 22, 9, 5))}" fill="#fff1a6"/>')
add("shapes", "star8", f'<polygon points="{pts(star(50, 50, 46, 24, 8))}" fill="#ff4f7b" stroke="#a3002c" stroke-width="3" stroke-linejoin="round"/>'
    '<circle cx="50" cy="50" r="12" fill="#ffd0dc"/>')
add("shapes", "sparkle", '<path d="M50 4C54 38 62 46 96 50C62 54 54 62 50 96C46 62 38 54 4 50C38 46 46 38 50 4Z" fill="#7ef0ff" stroke="#1b9fb3" stroke-width="2.5" stroke-linejoin="round"/>')
add("shapes", "heart", f'<path d="{heart}" fill="#ff2c4f" stroke="#a5001d" stroke-width="3"/>'
    '<path d="M24 28C30 22 38 24 41 30" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="4" stroke-linecap="round"/>')
add("shapes", "moon", '<path d="M60 6A44 44 0 1 0 94 70A36 36 0 1 1 60 6Z" fill="#ffd84a" stroke="#c99500" stroke-width="3"/>')
rays = "".join(f'<polygon points="{pts([polar(50, 50, 46, a), polar(50, 50, 28, a - 12), polar(50, 50, 28, a + 12)])}" fill="#ff9d00"/>' for a in range(0, 360, 30))
add("shapes", "sun", rays + '<circle cx="50" cy="50" r="27" fill="#ffd21f" stroke="#ff9d00" stroke-width="3"/>'
    '<circle cx="41" cy="46" r="3" fill="#6b3b00"/><circle cx="59" cy="46" r="3" fill="#6b3b00"/>'
    '<path d="M40 57Q50 66 60 57" fill="none" stroke="#6b3b00" stroke-width="3" stroke-linecap="round"/>')
sp = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in [polar(50, 50, 3 + t * 0.66, t * 18) for t in range(0, 61)])
add("shapes", "spiral", f'<polyline points="{sp}" fill="none" stroke="#7a3cff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')
add("shapes", "ring", f'<path d="{ring_path(50, 50, 40, 24)}" fill="#24c6a0" fill-rule="evenodd" stroke="#0b6e57" stroke-width="3"/>')
add("shapes", "plus", '<path d="M38 8H62V38H92V62H62V92H38V62H8V38H38Z" fill="#3fa9ff" stroke="#0b5ea8" stroke-width="3" stroke-linejoin="round"/>')
add("shapes", "lightning", '<polygon points="58,4 18,56 46,56 36,96 82,40 54,40 66,4" fill="#ffe11a" stroke="#c98a00" stroke-width="3" stroke-linejoin="round"/>')
add("shapes", "raindrop", '<path d="M50 6C66 34 80 50 80 64A30 30 0 0 1 20 64C20 50 34 34 50 6Z" fill="#3b8cff" stroke="#0c46a8" stroke-width="3"/>'
    '<path d="M36 62A14 14 0 0 0 44 76" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".75"/>')
arms = ""
for a in range(0, 360, 60):
    x, y = polar(50, 50, 44, a)
    arms += f'<line x1="50" y1="50" x2="{x:.1f}" y2="{y:.1f}"/>'
    for d, l in ((22, 12), (33, 9)):
        bx, by = polar(50, 50, d, a)
        for s in (-45, 45):
            ex, ey = polar(bx, by, l, a + s)
            arms += f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{ex:.1f}" y2="{ey:.1f}"/>'
add("shapes", "snowflake", f'<g stroke="#bfe9ff" stroke-width="5" stroke-linecap="round">{arms}</g>'
    f'<g stroke="#4aa8e0" stroke-width="2" stroke-linecap="round">{arms}</g>')
add("shapes", "dots", '<circle cx="34" cy="36" r="18" fill="#ff5f5f"/><circle cx="66" cy="40" r="14" fill="#ffc531"/>'
    '<circle cx="46" cy="70" r="16" fill="#38c7ff"/><circle cx="72" cy="72" r="9" fill="#8de04a"/>')
add("shapes", "zigzag", '<polyline points="6,62 22,38 38,62 54,38 70,62 86,38 94,50" fill="none" stroke="#ff4fd8" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
add("shapes", "squiggle", '<path d="M8 50C18 20 30 20 36 50S54 80 64 50S82 20 92 50" fill="none" stroke="#19d1a0" stroke-width="10" stroke-linecap="round"/>')
add("shapes", "triangle", '<polygon points="50,8 94,86 6,86" fill="#ff8a1f" stroke="#a84a00" stroke-width="3" stroke-linejoin="round"/>'
    '<polygon points="50,40 70,76 30,76" fill="#ffd1a6"/>')
add("shapes", "flower_shape", "".join(f'<circle cx="{polar(50, 50, 24, a)[0]:.1f}" cy="{polar(50, 50, 24, a)[1]:.1f}" r="20" fill="#ff7ab6"/>' for a in range(0, 360, 60))
    + '<circle cx="50" cy="50" r="16" fill="#ffe14a"/>')

# ---------------------------------------------------------------- nature
add("nature", "leaf", '<path d="M50 94C18 72 12 34 50 6C88 34 82 72 50 94Z" fill="#3fb34f" stroke="#1d6a28" stroke-width="3"/>'
    '<path d="M50 14V90M50 34L34 24M50 34L66 24M50 52L30 40M50 52L70 40M50 70L32 58M50 70L68 58" stroke="#1d6a28" stroke-width="2.5" stroke-linecap="round"/>')
add("nature", "autumn_leaf", '<path d="M50 94C18 72 12 34 50 6C88 34 82 72 50 94Z" fill="#ff8a1e" stroke="#a84300" stroke-width="3" transform="rotate(30 50 50)"/>'
    '<path d="M50 14V90" stroke="#a84300" stroke-width="2.5" transform="rotate(30 50 50)"/>')
petals = "".join(f'<ellipse cx="50" cy="24" rx="8" ry="20" fill="#fff" stroke="#d9d9e8" stroke-width="1.5" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 30))
add("nature", "daisy", petals + '<circle cx="50" cy="50" r="13" fill="#ffc81f" stroke="#d48a00" stroke-width="2"/>')
blossom = "".join(f'<path d="M50 50C36 36 38 14 46 12L50 18L54 12C62 14 64 36 50 50Z" fill="#ffb7d5" stroke="#e86aa3" stroke-width="2" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 72))
add("nature", "blossom", blossom + '<circle cx="50" cy="50" r="7" fill="#ffd94a"/>')
add("nature", "tulip", '<path d="M50 56V94" stroke="#2e9a3c" stroke-width="5"/><path d="M50 82C36 80 30 70 30 62C42 64 48 70 50 82Z" fill="#3fb34f"/>'
    '<path d="M28 20L40 32L50 16L60 32L72 20C76 44 68 60 50 60C32 60 24 44 28 20Z" fill="#ff3b5c" stroke="#a30024" stroke-width="3" stroke-linejoin="round"/>')
clover = "".join(f'<path d="{heart}" fill="#2fbf4f" stroke="#156b28" stroke-width="3" transform="rotate({a} 50 50) translate(50 50) scale(.5) translate(-50 -96)"/>' for a in (0, 90, 180, 270))
add("nature", "clover", clover + '<circle cx="50" cy="50" r="5" fill="#156b28"/>')
add("nature", "feather", '<path d="M76 8C40 16 18 50 22 90C50 80 84 50 76 8Z" fill="#2fb7c9" stroke="#0e6e7a" stroke-width="3"/>'
    '<path d="M18 96L74 12" stroke="#f4f0d8" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M36 70L28 64M44 58L32 48M52 46L40 34M60 34L50 22" stroke="#0e6e7a" stroke-width="2" stroke-linecap="round"/>')
ribs = "".join(f'<line x1="50" y1="88" x2="{polar(50, 88, 76, a)[0]:.1f}" y2="{polar(50, 88, 76, a)[1]:.1f}"/>' for a in range(-160, -15, 20))
add("nature", "shell", '<clipPath id="c"><path d="M50 88L12 46C14 22 32 10 50 10S86 22 88 46Z"/></clipPath>'
    '<path d="M50 88L12 46C14 22 32 10 50 10S86 22 88 46Z" fill="#ffd8b8"/>'
    f'<g stroke="#e0956a" stroke-width="2.5" clip-path="url(#c)">{ribs}</g>'
    '<path d="M50 88L12 46C14 22 32 10 50 10S86 22 88 46Z" fill="none" stroke="#c77b4a" stroke-width="3" stroke-linejoin="round"/><path d="M38 88H62L56 96H44Z" fill="#ffd8b8" stroke="#c77b4a" stroke-width="2.5"/>')
add("nature", "starfish", f'<polygon points="{pts(star(50, 54, 46, 20, 5))}" fill="#ff7a3d" stroke="#b33f00" stroke-width="4" stroke-linejoin="round"/>'
    + "".join(f'<circle cx="{polar(50, 54, d, a)[0]:.1f}" cy="{polar(50, 54, d, a)[1]:.1f}" r="2.5" fill="#ffd2b8"/>' for a in range(-90, 270, 72) for d in (12, 22, 31)))
add("nature", "mushroom", '<path d="M40 52H60L64 88H36Z" fill="#fff4e0" stroke="#b39770" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M8 56C8 30 28 12 50 12S92 30 92 56Z" fill="#e8262e" stroke="#8c0d12" stroke-width="3"/>'
    '<circle cx="30" cy="38" r="6" fill="#fff"/><circle cx="52" cy="26" r="7" fill="#fff"/><circle cx="72" cy="40" r="5" fill="#fff"/><circle cx="48" cy="46" r="4" fill="#fff"/>')
add("nature", "cactus", '<path d="M30 80H70L64 96H36Z" fill="#d36b3a" stroke="#7e3613" stroke-width="3"/>'
    '<path d="M42 80V22A8 8 0 0 1 58 22V80Z M42 56H30A6 6 0 0 1 24 50V36A5 5 0 0 1 34 36V46H42Z M58 48H68V30A5 5 0 0 1 78 30V44A8 8 0 0 1 70 52H58Z" fill="#3aa64a" stroke="#1b5e25" stroke-width="3" stroke-linejoin="round"/>'
    '<circle cx="50" cy="14" r="5" fill="#ff5fae"/>')
add("nature", "acorn", '<path d="M28 44H72V54C72 76 62 90 50 94C38 90 28 76 28 54Z" fill="#d9a35b" stroke="#7a4d17" stroke-width="3"/>'
    '<path d="M22 46C22 28 34 20 50 20S78 28 78 46Z" fill="#8a5a2b" stroke="#4a2c0c" stroke-width="3"/>'
    '<path d="M50 20V8" stroke="#4a2c0c" stroke-width="4" stroke-linecap="round"/>'
    '<path d="M30 38H70M34 30H66" stroke="#4a2c0c" stroke-width="2" stroke-opacity=".6"/>')
add("nature", "pine", '<polygon points="50,6 80,46 66,46 88,76 12,76 34,46 20,46" fill="#1f8f4a" stroke="#0d4d24" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="44" y="76" width="12" height="16" fill="#7a4d17"/><circle cx="40" cy="58" r="4" fill="#ff4747"/><circle cx="60" cy="40" r="4" fill="#ffd21f"/><circle cx="62" cy="66" r="4" fill="#3db8ff"/>')
add("nature", "sunflower", "".join(f'<ellipse cx="50" cy="20" rx="9" ry="18" fill="#ffc400" stroke="#c98a00" stroke-width="1.5" transform="rotate({a} 50 50)"/>' for a in range(0, 360, 24))
    + '<circle cx="50" cy="50" r="18" fill="#6b3b14"/>' + "".join(f'<circle cx="{polar(50, 50, r, a)[0]:.1f}" cy="{polar(50, 50, r, a)[1]:.1f}" r="1.8" fill="#c48a3a"/>' for r in (6, 12) for a in range(0, 360, 40 if r == 6 else 25)))

# ---------------------------------------------------------------- food
def citrus(name, rind, pith, flesh):
    seg = "".join(f'<path d="{sector(50, 50, 31, a + 3, a + 42)}" fill="{flesh}"/>' for a in range(0, 360, 45))
    add("food", name, f'<circle cx="50" cy="50" r="44" fill="{rind}"/><circle cx="50" cy="50" r="37" fill="{pith}"/>{seg}'
        f'<circle cx="50" cy="50" r="5" fill="{pith}"/>')

citrus("lemon_slice", "#f5d400", "#fff8cf", "#ffe74a")
citrus("orange_slice", "#ff8a00", "#ffe9cc", "#ffa733")
citrus("lime_slice", "#4cae24", "#eaffcf", "#9ae04a")
citrus("grapefruit_slice", "#ff9a6a", "#ffe8dc", "#ff5e6c")
seeds = "".join(f'<ellipse cx="{polar(50, 50, 18, a)[0]:.1f}" cy="{polar(50, 50, 18, a)[1]:.1f}" rx="1.6" ry="3.4" fill="#1a1a1a" transform="rotate({a + 90} {polar(50, 50, 18, a)[0]:.1f} {polar(50, 50, 18, a)[1]:.1f})"/>' for a in range(0, 360, 20))
add("food", "kiwi_slice", f'<circle cx="50" cy="50" r="44" fill="#8a6a3a"/><circle cx="50" cy="50" r="39" fill="#6ac43a"/><circle cx="50" cy="50" r="28" fill="#8ed85a"/>'
    f'<ellipse cx="50" cy="50" rx="11" ry="8" fill="#f2f7d8"/>{seeds}')
wm_seeds = "".join(f'<ellipse cx="{x}" cy="{y}" rx="2" ry="3.5" fill="#222"/>' for x, y in ((30, 44), (44, 54), (56, 54), (70, 44), (50, 40), (38, 36), (62, 36)))
add("food", "watermelon", '<path d="M6 30A44 44 0 0 0 94 30Z" fill="#2e9a3c"/><path d="M12 30A38 38 0 0 0 88 30Z" fill="#e9ffd8"/>'
    f'<path d="M16 30A34 34 0 0 0 84 30Z" fill="#ff3d55"/>{wm_seeds}')
add("food", "cherries", '<path d="M32 66C34 40 44 22 60 10M68 62C66 40 64 24 60 10" fill="none" stroke="#3b7a1f" stroke-width="3.5" stroke-linecap="round"/>'
    '<path d="M60 10C70 6 82 12 84 20C74 22 66 18 60 10Z" fill="#4cae24"/>'
    '<circle cx="30" cy="72" r="18" fill="#d10f2f" stroke="#7a0016" stroke-width="2.5"/><circle cx="70" cy="68" r="18" fill="#e3173a" stroke="#7a0016" stroke-width="2.5"/>'
    '<circle cx="24" cy="66" r="4" fill="#fff" fill-opacity=".6"/><circle cx="64" cy="62" r="4" fill="#fff" fill-opacity=".6"/>')
sb = "".join(f'<ellipse cx="{x}" cy="{y}" rx="1.6" ry="2.6" fill="#ffe680"/>' for x, y in ((36, 42), (50, 40), (64, 42), (42, 56), (58, 56), (50, 70), (34, 30), (66, 30), (50, 54), (44, 80) if False else (46, 82)))
add("food", "strawberry", '<path d="M50 94C26 78 14 52 18 34C22 22 36 20 50 24C64 20 78 22 82 34C86 52 74 78 50 94Z" fill="#ff2a45" stroke="#99001a" stroke-width="3"/>'
    + sb + '<path d="M50 26L36 12L46 20L50 6L54 20L64 12Z" fill="#2fae3f" stroke="#156b28" stroke-width="2" stroke-linejoin="round"/>')
rnd = random.Random(7)
spr = ""
cols = ["#ffffff", "#ffe14a", "#3fd0ff", "#7cff6b", "#b46bff"]
for _ in range(16):
    a = rnd.uniform(0, 360); r = rnd.uniform(23, 36)
    x, y = polar(50, 50, r, a); ang = rnd.uniform(0, 180)
    spr += f'<rect x="{x-3:.1f}" y="{y-1.2:.1f}" width="6" height="2.4" rx="1.2" fill="{rnd.choice(cols)}" transform="rotate({ang:.0f} {x:.1f} {y:.1f})"/>'
icing = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in [polar(50, 50, 40 + (3 if i % 2 else -1), i * 15) for i in range(24)])
add("food", "donut", f'<path d="{ring_path(50, 50, 45, 14)}" fill="#e3a65a" fill-rule="evenodd" stroke="#8a5a1f" stroke-width="2.5"/>'
    f'<path d="M{icing.replace(" ", "L")}Z M31 50a19 19 0 1 0 38 0a19 19 0 1 0 -38 0Z" fill="#ff7ab8" fill-rule="evenodd"/>{spr}')
add("food", "candy", '<polygon points="30,50 6,30 12,50 6,70" fill="#ff5fae" stroke="#a3005a" stroke-width="2.5" stroke-linejoin="round"/>'
    '<polygon points="70,50 94,30 88,50 94,70" fill="#ff5fae" stroke="#a3005a" stroke-width="2.5" stroke-linejoin="round"/>'
    '<ellipse cx="50" cy="50" rx="24" ry="18" fill="#ff8ac4" stroke="#a3005a" stroke-width="2.5"/>'
    '<path d="M36 40L46 62M50 36L60 62" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".8"/>')
lp = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in [polar(50, 36, 2 + t * 1.1, t * 14) for t in range(0, 26)])
add("food", "lollipop", '<rect x="47" y="60" width="6" height="36" rx="3" fill="#f4f0e6" stroke="#b8ad95" stroke-width="1.5"/>'
    '<circle cx="50" cy="36" r="31" fill="#ffe3f1" stroke="#ff4f9a" stroke-width="3"/>'
    f'<polyline points="{lp}" fill="none" stroke="#ff4f9a" stroke-width="5" stroke-linecap="round"/>')
add("food", "ice_cream", '<polygon points="30,50 70,50 50,96" fill="#e8b062" stroke="#9a6420" stroke-width="2.5" stroke-linejoin="round"/>'
    '<path d="M36 56L58 78M48 54L62 68M42 66L56 52M34 56L52 86" stroke="#9a6420" stroke-width="1.5" stroke-opacity=".7"/>'
    '<circle cx="38" cy="42" r="15" fill="#ffd1e6" stroke="#d9709f" stroke-width="2"/><circle cx="62" cy="42" r="15" fill="#c8f0d6" stroke="#4cae72" stroke-width="2"/>'
    '<circle cx="50" cy="26" r="16" fill="#8a5a3a" stroke="#4a2c14" stroke-width="2"/><circle cx="50" cy="8" r="5" fill="#e3173a"/>')
add("food", "cupcake", '<path d="M24 54H76L68 92H32Z" fill="#4fb8ff" stroke="#1b6aa8" stroke-width="2.5" stroke-linejoin="round"/>'
    '<path d="M36 54L38 92M50 54V92M64 54L62 92" stroke="#1b6aa8" stroke-width="2" stroke-opacity=".6"/>'
    '<path d="M18 56C14 44 24 36 32 38C32 26 44 20 52 26C58 18 74 22 72 36C82 36 88 48 80 56Z" fill="#fff0f7" stroke="#e086b3" stroke-width="2.5"/>'
    '<circle cx="54" cy="18" r="7" fill="#e3173a"/>')
chips = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#5a3315"/>' for x, y, r in ((36, 36, 5), (60, 30, 4), (66, 56, 5), (40, 62, 4), (52, 46, 3.5), (30, 50, 3), (56, 72, 4)))
add("food", "cookie", '<path d="M50 8C72 8 92 26 92 48C92 72 74 92 50 92C26 92 8 74 8 50C8 26 28 8 50 8Z" fill="#d9a35b" stroke="#8a5a1f" stroke-width="3"/>' + chips)
add("food", "banana", '<path d="M14 30C18 66 50 86 86 70C88 64 84 62 80 64C52 72 30 56 26 30Z" fill="#ffdd33" stroke="#a37800" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M12 22L16 32L26 30L24 20Z" fill="#6b4a14"/>')
add("food", "cheese", '<path d="M8 70L80 26L94 40V80H8Z" fill="#ffc933" stroke="#b37a00" stroke-width="3" stroke-linejoin="round"/>'
    '<circle cx="30" cy="70" r="6" fill="#e6a400"/><circle cx="58" cy="60" r="8" fill="#e6a400"/><circle cx="80" cy="66" r="5" fill="#e6a400"/><circle cx="74" cy="44" r="4" fill="#e6a400"/>')
add("food", "fried_egg", '<path d="M50 8C70 8 74 22 86 30C98 40 92 64 80 74C68 90 44 94 30 86C12 78 6 58 12 42C18 26 32 8 50 8Z" fill="#fff" stroke="#d9d9d9" stroke-width="2.5"/>'
    '<circle cx="50" cy="48" r="17" fill="#ffb800" stroke="#e08a00" stroke-width="2"/><circle cx="44" cy="42" r="5" fill="#fff" fill-opacity=".7"/>')
add("food", "chili", '<path d="M70 22C80 30 82 46 70 62C56 80 34 90 12 92C34 82 50 66 56 46C60 32 62 24 70 22Z" fill="#e8262e" stroke="#8c0d12" stroke-width="3"/>'
    '<path d="M66 24C68 14 76 8 86 8C82 12 80 18 78 26Z" fill="#3aa64a" stroke="#1b5e25" stroke-width="2"/>')
add("food", "pretzel", '<path d="M50 74C30 90 10 74 14 54C18 34 40 30 50 50C60 70 76 64 78 50C80 30 62 26 50 40C40 52 34 64 22 66M50 74C70 90 90 74 86 54" fill="none" stroke="#9a5a1f" stroke-width="10" stroke-linecap="round"/>'
    '<g fill="#fff"><circle cx="20" cy="50" r="2"/><circle cx="34" cy="38" r="2"/><circle cx="70" cy="36" r="2"/><circle cx="82" cy="62" r="2"/><circle cx="58" cy="62" r="2"/></g>')

# ---------------------------------------------------------------- critters
add("critters", "rubber_duck", '<path d="M10 56C20 54 22 48 30 50C40 44 68 46 82 56C90 70 76 88 50 88C24 88 10 76 10 56Z" fill="#ffd21f" stroke="#c98a00" stroke-width="3"/>'
    '<circle cx="62" cy="34" r="18" fill="#ffd21f" stroke="#c98a00" stroke-width="3"/>'
    '<path d="M78 34L96 38L80 46Z" fill="#ff8a00" stroke="#b35c00" stroke-width="2" stroke-linejoin="round"/>'
    '<circle cx="66" cy="30" r="3.5" fill="#222"/><circle cx="67" cy="29" r="1" fill="#fff"/>'
    '<path d="M34 62C44 58 56 60 62 68C52 76 40 74 34 62Z" fill="#ffe57a" stroke="#c98a00" stroke-width="2"/>')
add("critters", "goldfish", '<polygon points="70,50 94,28 90,50 94,72" fill="#ff7a1a" stroke="#b34700" stroke-width="2.5" stroke-linejoin="round"/>'
    '<ellipse cx="44" cy="50" rx="32" ry="22" fill="#ff8f2e" stroke="#b34700" stroke-width="3"/>'
    '<path d="M38 30C44 20 56 22 58 30Z" fill="#ffb066"/><path d="M58 52C62 46 70 46 72 50" fill="none" stroke="#b34700" stroke-width="2"/>'
    '<circle cx="26" cy="44" r="5" fill="#fff"/><circle cx="25" cy="44" r="2.5" fill="#222"/><path d="M14 54Q18 57 22 54" fill="none" stroke="#b34700" stroke-width="2"/>')
add("critters", "ladybug", '<circle cx="50" cy="56" r="36" fill="#e8262e" stroke="#5a0007" stroke-width="3"/>'
    '<path d="M50 22V92" stroke="#1a1a1a" stroke-width="3"/><path d="M30 24A20 16 0 0 1 70 24Z" fill="#1a1a1a"/>'
    '<circle cx="42" cy="20" r="3" fill="#fff"/><circle cx="58" cy="20" r="3" fill="#fff"/>'
    + "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1a1a1a"/>' for x, y, r in ((34, 44, 6), (66, 44, 6), (30, 66, 5), (70, 66, 5), (40, 82, 4), (60, 82, 4))))
add("critters", "butterfly", '<ellipse cx="30" cy="34" rx="22" ry="26" fill="#3fa9ff" stroke="#0b4f8a" stroke-width="2.5" transform="rotate(-20 30 34)"/>'
    '<ellipse cx="70" cy="34" rx="22" ry="26" fill="#3fa9ff" stroke="#0b4f8a" stroke-width="2.5" transform="rotate(20 70 34)"/>'
    '<ellipse cx="32" cy="70" rx="16" ry="18" fill="#ff7ab6" stroke="#a3005a" stroke-width="2.5" transform="rotate(20 32 70)"/>'
    '<ellipse cx="68" cy="70" rx="16" ry="18" fill="#ff7ab6" stroke="#a3005a" stroke-width="2.5" transform="rotate(-20 68 70)"/>'
    '<circle cx="28" cy="32" r="7" fill="#ffe14a"/><circle cx="72" cy="32" r="7" fill="#ffe14a"/>'
    '<rect x="46" y="22" width="8" height="64" rx="4" fill="#2a1a3a"/><path d="M48 24L38 8M52 24L62 8" stroke="#2a1a3a" stroke-width="2.5" stroke-linecap="round"/>')
sh = " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in [polar(56, 46, 2 + t * 1.15, t * 15) for t in range(0, 26)])
add("critters", "snail", '<path d="M8 82C8 72 18 70 30 70H76C88 70 94 76 94 82Z" fill="#c9e07a" stroke="#6a8a1f" stroke-width="2.5"/>'
    '<path d="M14 74C10 62 12 50 16 42M20 72C22 60 26 52 30 46" stroke="#6a8a1f" stroke-width="2.5" stroke-linecap="round" fill="none"/>'
    '<circle cx="16" cy="40" r="3.5" fill="#222"/><circle cx="30" cy="44" r="3.5" fill="#222"/>'
    '<circle cx="56" cy="46" r="30" fill="#c77b4a" stroke="#6a3a14" stroke-width="3"/>'
    f'<polyline points="{sh}" fill="none" stroke="#6a3a14" stroke-width="3" stroke-linecap="round"/>')
add("critters", "bee", '<ellipse cx="34" cy="30" rx="16" ry="12" fill="#dff4ff" fill-opacity=".85" stroke="#7fb3d1" stroke-width="2" transform="rotate(-25 34 30)"/>'
    '<ellipse cx="58" cy="28" rx="16" ry="12" fill="#dff4ff" fill-opacity=".85" stroke="#7fb3d1" stroke-width="2" transform="rotate(25 58 28)"/>'
    '<ellipse cx="48" cy="58" rx="34" ry="24" fill="#ffd21f" stroke="#1a1a1a" stroke-width="3"/>'
    '<path d="M38 36V80M54 35V81" stroke="#1a1a1a" stroke-width="7"/>'
    '<polygon points="82,58 94,54 94,62" fill="#1a1a1a"/><circle cx="24" cy="54" r="4" fill="#1a1a1a"/>')
tent = "".join(f'<path d="M{x} 56C{x + w} 70 {x - w} 82 {x + w * 0.6:.0f} 94" fill="none" stroke="#9b4dff" stroke-width="7" stroke-linecap="round"/>' for x, w in ((24, -6), (36, 6), (50, -6), (64, 6), (76, -6)))
add("critters", "octopus", tent + '<path d="M18 58C14 30 30 10 50 10S86 30 82 58Z" fill="#b06bff" stroke="#5a1fa8" stroke-width="3"/>'
    '<circle cx="38" cy="40" r="7" fill="#fff"/><circle cx="62" cy="40" r="7" fill="#fff"/><circle cx="39" cy="41" r="3.5" fill="#222"/><circle cx="61" cy="41" r="3.5" fill="#222"/>'
    '<path d="M44 52Q50 57 56 52" fill="none" stroke="#5a1fa8" stroke-width="2.5" stroke-linecap="round"/>')
jt = "".join(f'<path d="M{x} 50Q{x + 8} 64 {x} 76T{x} 96" fill="none" stroke="#ff9ad5" stroke-width="3" stroke-opacity=".9" stroke-linecap="round"/>' for x in (28, 40, 52, 64, 74))
add("critters", "jellyfish", jt + '<path d="M14 52C14 26 30 8 50 8S86 26 86 52C76 48 70 56 62 52C56 48 46 56 38 52C30 48 24 56 14 52Z" fill="#ff7ac8" fill-opacity=".7" stroke="#d63b97" stroke-width="2.5"/>'
    '<path d="M30 26C34 18 42 16 48 16" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".7"/>')
add("critters", "whale", '<path d="M8 56C8 34 30 24 52 28C72 32 80 48 82 58L94 44C96 56 94 66 86 70L94 84C84 82 78 76 74 72C64 84 40 88 26 82C14 76 8 66 8 56Z" fill="#3b7fd9" stroke="#123f80" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M10 62C26 74 50 76 68 68C60 80 40 84 26 80C16 76 12 70 10 62Z" fill="#cfe6ff"/>'
    '<circle cx="26" cy="48" r="3.5" fill="#123f80"/><path d="M40 22C38 12 42 6 48 4M40 22C36 14 30 12 26 12M40 22C44 16 50 16 54 18" fill="none" stroke="#6fc3ff" stroke-width="3" stroke-linecap="round"/>')
add("critters", "bird", '<path d="M82 52L96 46L96 60Z" fill="#3fa9ff"/><circle cx="48" cy="54" r="34" fill="#ff5f5f" stroke="#a31f1f" stroke-width="3"/>'
    '<path d="M40 60C54 54 70 58 74 70C62 78 48 74 40 60Z" fill="#ff9a9a" stroke="#a31f1f" stroke-width="2"/>'
    '<polygon points="14,48 2,54 14,58" fill="#ffb800"/><circle cx="28" cy="44" r="5" fill="#fff"/><circle cx="27" cy="44" r="2.5" fill="#222"/>'
    '<path d="M44 20C46 12 54 10 58 14" fill="none" stroke="#a31f1f" stroke-width="3" stroke-linecap="round"/>')
add("critters", "cat_face", '<polygon points="14,42 18,6 42,26" fill="#ff9f43" stroke="#a35400" stroke-width="3" stroke-linejoin="round"/>'
    '<polygon points="86,42 82,6 58,26" fill="#ff9f43" stroke="#a35400" stroke-width="3" stroke-linejoin="round"/>'
    '<ellipse cx="50" cy="56" rx="40" ry="34" fill="#ffad5c" stroke="#a35400" stroke-width="3"/>'
    '<ellipse cx="34" cy="50" rx="6" ry="8" fill="#2e7d32"/><ellipse cx="66" cy="50" rx="6" ry="8" fill="#2e7d32"/>'
    '<ellipse cx="34" cy="50" rx="2" ry="6" fill="#111"/><ellipse cx="66" cy="50" rx="2" ry="6" fill="#111"/>'
    '<polygon points="46,62 54,62 50,67" fill="#ff6f91"/><path d="M50 67Q44 74 38 70M50 67Q56 74 62 70" fill="none" stroke="#a35400" stroke-width="2"/>'
    '<path d="M12 62L30 64M12 70L30 68M88 62L70 64M88 70L70 68" stroke="#a35400" stroke-width="1.5"/>')
add("critters", "frog", '<circle cx="30" cy="30" r="16" fill="#4cc552" stroke="#1e6b22" stroke-width="3"/><circle cx="70" cy="30" r="16" fill="#4cc552" stroke="#1e6b22" stroke-width="3"/>'
    '<ellipse cx="50" cy="60" rx="42" ry="30" fill="#4cc552" stroke="#1e6b22" stroke-width="3"/>'
    '<circle cx="30" cy="30" r="9" fill="#fff"/><circle cx="70" cy="30" r="9" fill="#fff"/><circle cx="32" cy="31" r="5" fill="#111"/><circle cx="68" cy="31" r="5" fill="#111"/>'
    '<path d="M24 62Q50 84 76 62" fill="none" stroke="#1e6b22" stroke-width="3.5" stroke-linecap="round"/>'
    '<circle cx="22" cy="56" r="5" fill="#ff8fa6" fill-opacity=".7"/><circle cx="78" cy="56" r="5" fill="#ff8fa6" fill-opacity=".7"/>')
hexes = "".join(f'<polygon points="{pts(ngon(cx, cy, 9, 6, 0))}" fill="#7ab342" stroke="#33691e" stroke-width="2"/>' for cx, cy in ((50, 50), (50, 32), (50, 68), (34, 41), (66, 41), (34, 59), (66, 59)))
add("critters", "turtle", '<ellipse cx="50" cy="10" rx="9" ry="10" fill="#9ccc65" stroke="#33691e" stroke-width="2.5"/>'
    + "".join(f'<ellipse cx="{x}" cy="{y}" rx="8" ry="11" fill="#9ccc65" stroke="#33691e" stroke-width="2.5" transform="rotate({r} {x} {y})"/>' for x, y, r in ((22, 28, -45), (78, 28, 45), (22, 74, 45), (78, 74, -45)))
    + '<ellipse cx="50" cy="52" rx="32" ry="36" fill="#558b2f" stroke="#33691e" stroke-width="3"/>' + hexes)
add("critters", "crab", '<path d="M26 40L14 24M74 40L86 24" stroke="#c62828" stroke-width="4"/>'
    '<circle cx="12" cy="18" r="10" fill="#ef5350" stroke="#8e0000" stroke-width="2.5"/><circle cx="88" cy="18" r="10" fill="#ef5350" stroke="#8e0000" stroke-width="2.5"/>'
    '<path d="M6 14L14 20M94 14L86 20" stroke="#8e0000" stroke-width="3"/>'
    '<path d="M20 66L6 76M22 72L12 86M80 66L94 76M78 72L88 86" stroke="#c62828" stroke-width="4" stroke-linecap="round"/>'
    '<ellipse cx="50" cy="60" rx="34" ry="24" fill="#ef5350" stroke="#8e0000" stroke-width="3"/>'
    '<path d="M42 38V28M58 38V28" stroke="#8e0000" stroke-width="3"/><circle cx="42" cy="26" r="5" fill="#fff" stroke="#8e0000" stroke-width="2"/><circle cx="58" cy="26" r="5" fill="#fff" stroke="#8e0000" stroke-width="2"/>'
    '<circle cx="42" cy="26" r="2" fill="#111"/><circle cx="58" cy="26" r="2" fill="#111"/><path d="M42 64Q50 70 58 64" fill="none" stroke="#8e0000" stroke-width="2.5"/>')
add("critters", "owl", '<path d="M18 30L24 10L38 22Z M82 30L76 10L62 22Z" fill="#8d6e63" stroke="#4e342e" stroke-width="2.5" stroke-linejoin="round"/>'
    '<ellipse cx="50" cy="56" rx="34" ry="38" fill="#a1887f" stroke="#4e342e" stroke-width="3"/>'
    '<ellipse cx="50" cy="70" rx="20" ry="20" fill="#efebe9"/>'
    '<circle cx="36" cy="40" r="12" fill="#fff" stroke="#4e342e" stroke-width="2"/><circle cx="64" cy="40" r="12" fill="#fff" stroke="#4e342e" stroke-width="2"/>'
    '<circle cx="36" cy="40" r="6" fill="#ffb300"/><circle cx="64" cy="40" r="6" fill="#ffb300"/><circle cx="36" cy="40" r="3" fill="#111"/><circle cx="64" cy="40" r="3" fill="#111"/>'
    '<polygon points="46,50 54,50 50,58" fill="#ff8f00"/><path d="M42 68L46 72L50 68L54 72L58 68M44 78L48 82L52 78L56 82" fill="none" stroke="#8d6e63" stroke-width="2"/>')

# ---------------------------------------------------------------- things
add("things", "button", '<circle cx="50" cy="50" r="42" fill="#ff5c8a" stroke="#a3002f" stroke-width="3"/><circle cx="50" cy="50" r="32" fill="none" stroke="#a3002f" stroke-width="2" stroke-opacity=".6"/>'
    '<g fill="#7a0022"><circle cx="40" cy="40" r="5"/><circle cx="60" cy="40" r="5"/><circle cx="40" cy="60" r="5"/><circle cx="60" cy="60" r="5"/></g>')
add("things", "button_blue", '<circle cx="50" cy="50" r="40" fill="#2ec4b6" stroke="#0b6f66" stroke-width="3"/><circle cx="50" cy="50" r="28" fill="#45d9cb"/>'
    '<g fill="#0b6f66"><circle cx="42" cy="50" r="5"/><circle cx="58" cy="50" r="5"/></g>')
add("things", "paperclip", '<path d="M38 82V26A12 12 0 0 1 62 26V72A8 8 0 0 1 46 72V32" fill="none" stroke="#9aa5b1" stroke-width="5" stroke-linecap="round" transform="rotate(25 50 50)"/>'
    '<path d="M38 82V26A12 12 0 0 1 62 26V72A8 8 0 0 1 46 72V32" fill="none" stroke="#e4e9ef" stroke-width="2" stroke-linecap="round" transform="rotate(25 50 50)"/>')
add("things", "safety_pin", '<g transform="rotate(-30 50 50)"><path d="M20 58H76A8 8 0 0 0 76 42H34" fill="none" stroke="#b0b8c2" stroke-width="4" stroke-linecap="round"/>'
    '<circle cx="14" cy="54" r="8" fill="none" stroke="#b0b8c2" stroke-width="4"/><path d="M22 50H84" stroke="#b0b8c2" stroke-width="4" stroke-linecap="round"/>'
    '<rect x="76" y="40" width="16" height="20" rx="4" fill="#ffd21f" stroke="#a37800" stroke-width="2"/></g>')
add("things", "key", '<g transform="rotate(-40 50 50)"><path d="M10 50A16 16 0 1 0 42 50A16 16 0 1 0 10 50ZM20 50A6 6 0 1 1 32 50A6 6 0 1 1 20 50Z" fill="#ffc21a" fill-rule="evenodd" stroke="#a37800" stroke-width="2.5"/>'
    '<path d="M42 46H92V54H86V64H78V54H72V62H64V54H42Z" fill="#ffc21a" stroke="#a37800" stroke-width="2.5" stroke-linejoin="round"/></g>')
add("things", "screw", '<circle cx="50" cy="50" r="40" fill="#c5ccd4" stroke="#6b7680" stroke-width="3"/><circle cx="44" cy="44" r="30" fill="#dde3e9"/>'
    '<path d="M50 24V76M24 50H76" stroke="#5a6570" stroke-width="8" stroke-linecap="round"/>')
add("things", "hex_nut", f'<path d="M{pts(ngon(50, 50, 44, 6, 0)).replace(" ", "L")}Z M38 50A12 12 0 1 0 62 50A12 12 0 1 0 38 50Z" fill="#aeb8c2" fill-rule="evenodd" stroke="#5a6570" stroke-width="3" stroke-linejoin="round"/>'
    '<circle cx="50" cy="50" r="18" fill="none" stroke="#5a6570" stroke-width="2" stroke-opacity=".5"/>')
gear = []
for i in range(12):
    a = i * 30
    gear += [polar(50, 50, 34, a - 11), polar(50, 50, 44, a - 7), polar(50, 50, 44, a + 7), polar(50, 50, 34, a + 11)]
add("things", "gear", f'<path d="M{pts(gear).replace(" ", "L")}Z {ring_path(50, 50, 12, 12).split("Z")[0]}Z" fill="#ff9d00" fill-rule="evenodd" stroke="#9a5a00" stroke-width="3" stroke-linejoin="round"/>'
    '<circle cx="50" cy="50" r="22" fill="none" stroke="#9a5a00" stroke-width="2" stroke-opacity=".6"/>')
add("things", "coin", '<circle cx="50" cy="50" r="42" fill="#ffc21a" stroke="#a37800" stroke-width="3"/><circle cx="50" cy="50" r="33" fill="none" stroke="#a37800" stroke-width="2.5"/>'
    f'<polygon points="{pts(star(50, 52, 20, 8, 5))}" fill="#ffe27a" stroke="#a37800" stroke-width="2"/>')
add("things", "dice", '<g transform="rotate(12 50 50)"><rect x="12" y="12" width="76" height="76" rx="14" fill="#fff" stroke="#9aa0a6" stroke-width="3"/>'
    '<g fill="#e8262e"><circle cx="32" cy="32" r="7"/><circle cx="68" cy="32" r="7"/><circle cx="50" cy="50" r="7"/><circle cx="32" cy="68" r="7"/><circle cx="68" cy="68" r="7"/></g></g>')
add("things", "marble", '<radialGradient id="g" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".4" stop-color="#7fd3ff" stop-opacity=".7"/><stop offset="1" stop-color="#1569b5" stop-opacity=".85"/></radialGradient>'
    .join(["", ""]) and '<circle cx="50" cy="50" r="42" fill="url(#g)"/><path d="M24 64C40 40 60 74 78 40" fill="none" stroke="#ff4f7b" stroke-width="7" stroke-linecap="round"/>'
    '<path d="M28 34C44 52 60 30 72 62" fill="none" stroke="#ffd21f" stroke-width="5" stroke-linecap="round"/>',
    '<radialGradient id="g" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".4" stop-color="#7fd3ff" stop-opacity=".7"/><stop offset="1" stop-color="#1569b5" stop-opacity=".85"/></radialGradient>')
add("things", "googly_eye", '<circle cx="50" cy="50" r="42" fill="#fff" stroke="#222" stroke-width="4"/><circle cx="58" cy="62" r="20" fill="#111"/><circle cx="52" cy="56" r="5" fill="#fff"/>')
add("things", "umbrella", '<path d="M50 50V82A8 8 0 0 1 34 82" fill="none" stroke="#5a3315" stroke-width="5" stroke-linecap="round"/>'
    '<path d="M6 50C6 26 26 10 50 10S94 26 94 50C88 44 80 44 72 50C66 44 58 44 50 50C42 44 34 44 28 50C20 44 12 44 6 50Z" fill="#7a3cff" stroke="#3b0f8f" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M50 10C40 24 30 36 28 50M50 10C60 24 70 36 72 50M50 10V50" fill="none" stroke="#3b0f8f" stroke-width="2"/>')
add("things", "crown", '<polygon points="10,30 30,54 50,18 70,54 90,30 82,82 18,82" fill="#ffc21a" stroke="#a37800" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="18" y="70" width="64" height="12" fill="#ffda5c" stroke="#a37800" stroke-width="2"/>'
    '<circle cx="10" cy="30" r="5" fill="#e3173a"/><circle cx="50" cy="18" r="5" fill="#2f7bff"/><circle cx="90" cy="30" r="5" fill="#1fc45a"/><circle cx="50" cy="60" r="6" fill="#e3173a"/>')
add("things", "rocket", '<g transform="rotate(35 50 50)"><path d="M42 74L46 92L50 82L54 92L58 74Z" fill="#ff8a00"/>'
    '<path d="M36 60L22 76L40 72Z M64 60L78 76L60 72Z" fill="#e8262e" stroke="#8c0d12" stroke-width="2" stroke-linejoin="round"/>'
    '<path d="M50 6C66 20 68 44 62 74H38C32 44 34 20 50 6Z" fill="#f2f4f7" stroke="#5a6570" stroke-width="3"/>'
    '<circle cx="50" cy="38" r="8" fill="#3fa9ff" stroke="#5a6570" stroke-width="2.5"/><path d="M42 16H58" stroke="#e8262e" stroke-width="4"/></g>')
add("things", "anchor", '<g fill="none" stroke="#2c3e66" stroke-width="7" stroke-linecap="round"><circle cx="50" cy="16" r="8"/><path d="M50 24V88M34 38H66M14 56C16 76 32 88 50 88S84 76 86 56"/></g>'
    '<path d="M8 60L14 50L22 60Z M92 60L86 50L78 60Z" fill="#2c3e66"/>')
add("things", "light_bulb", '<path d="M50 8A28 28 0 0 0 34 60C38 64 38 68 38 72H62C62 68 62 64 66 60A28 28 0 0 0 50 8Z" fill="#ffe86b" stroke="#c99a00" stroke-width="3"/>'
    '<path d="M44 70V52L50 46L56 52V70" fill="none" stroke="#c97a00" stroke-width="2"/>'
    '<rect x="38" y="72" width="24" height="16" rx="3" fill="#aeb8c2" stroke="#5a6570" stroke-width="2.5"/><path d="M38 78H62M38 84H62" stroke="#5a6570" stroke-width="2"/>'
    '<path d="M44 92H56" stroke="#5a6570" stroke-width="4" stroke-linecap="round"/><path d="M36 24C40 18 46 16 50 16" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round"/>')
add("things", "music_note", '<path d="M40 76V16L82 8V64" fill="none" stroke="#2a1a3a" stroke-width="6" stroke-linejoin="round"/><path d="M40 16L82 8V24L40 32Z" fill="#2a1a3a"/>'
    '<ellipse cx="28" cy="78" rx="14" ry="10" fill="#ff4f9a" stroke="#2a1a3a" stroke-width="3" transform="rotate(-20 28 78)"/>'
    '<ellipse cx="70" cy="66" rx="14" ry="10" fill="#ff4f9a" stroke="#2a1a3a" stroke-width="3" transform="rotate(-20 70 66)"/>')
add("things", "pencil", '<g transform="rotate(-45 50 50)"><rect x="14" y="40" width="58" height="20" fill="#ffc21a" stroke="#a37800" stroke-width="2.5"/>'
    '<path d="M14 46H72M14 54H72" stroke="#a37800" stroke-width="1.5"/><polygon points="72,40 92,50 72,60" fill="#f2d2a6" stroke="#a37800" stroke-width="2.5" stroke-linejoin="round"/>'
    '<polygon points="86,47 92,50 86,53" fill="#333"/><rect x="4" y="40" width="10" height="20" rx="3" fill="#ff8fa6" stroke="#b34766" stroke-width="2.5"/></g>')
add("things", "teacup", '<ellipse cx="46" cy="82" rx="38" ry="8" fill="#e8f1ff" stroke="#6a86b3" stroke-width="2.5"/>'
    '<path d="M70 44C88 40 90 66 66 66" fill="none" stroke="#6a86b3" stroke-width="5"/>'
    '<path d="M14 40H76C76 64 64 80 45 80S14 64 14 40Z" fill="#fff" stroke="#6a86b3" stroke-width="3"/>'
    '<path d="M24 54Q34 48 44 54T64 54" fill="none" stroke="#ff7ab6" stroke-width="4" stroke-linecap="round"/>'
    '<path d="M32 30C28 22 36 18 32 10M46 30C42 22 50 18 46 10" fill="none" stroke="#b8c7de" stroke-width="3" stroke-linecap="round"/>')
add("things", "balloon", '<path d="M50 74C52 82 46 88 50 98" fill="none" stroke="#777" stroke-width="2"/>'
    '<ellipse cx="50" cy="38" rx="28" ry="34" fill="#ff3b5c" stroke="#a30024" stroke-width="3"/><polygon points="46,72 54,72 50,78" fill="#a30024"/>'
    '<ellipse cx="38" cy="26" rx="6" ry="10" fill="#fff" fill-opacity=".6" transform="rotate(25 38 26)"/>')
add("things", "magnet", '<path d="M22 86V46A28 28 0 0 1 78 46V86" fill="none" stroke="#e8262e" stroke-width="18"/>'
    '<path d="M13 72H31V90H13Z M69 72H87V90H69Z" fill="#c5ccd4" stroke="#5a6570" stroke-width="2.5"/>')
add("things", "robot", '<path d="M50 18V8" stroke="#5a6570" stroke-width="3"/><circle cx="50" cy="7" r="5" fill="#e8262e"/>'
    '<rect x="16" y="18" width="68" height="56" rx="12" fill="#b0c4de" stroke="#46566b" stroke-width="3"/>'
    '<rect x="8" y="38" width="8" height="18" rx="3" fill="#46566b"/><rect x="84" y="38" width="8" height="18" rx="3" fill="#46566b"/>'
    '<circle cx="36" cy="42" r="9" fill="#fff" stroke="#46566b" stroke-width="2.5"/><circle cx="64" cy="42" r="9" fill="#fff" stroke="#46566b" stroke-width="2.5"/>'
    '<circle cx="36" cy="42" r="4" fill="#20c4ff"/><circle cx="64" cy="42" r="4" fill="#20c4ff"/>'
    '<rect x="32" y="58" width="36" height="8" rx="2" fill="#46566b"/><path d="M38 58V66M44 58V66M50 58V66M56 58V66M62 58V66" stroke="#b0c4de" stroke-width="1.5"/>'
    '<rect x="34" y="78" width="32" height="14" rx="4" fill="#8aa0bd" stroke="#46566b" stroke-width="2.5"/>')
add("things", "planet", '<g transform="rotate(-18 50 50)"><path d="M6 50A44 12 0 0 1 94 50" fill="none" stroke="#ffd27a" stroke-width="6"/>'
    '<circle cx="50" cy="50" r="28" fill="#ff8f5c" stroke="#a3401a" stroke-width="3"/>'
    '<path d="M24 42C40 46 58 40 76 44M24 58C38 62 60 56 76 60" fill="none" stroke="#ffc6a8" stroke-width="3"/>'
    '<path d="M94 50A44 12 0 0 1 6 50" fill="none" stroke="#ffd27a" stroke-width="6"/></g>')
add("things", "hourglass", '<rect x="18" y="6" width="64" height="10" rx="4" fill="#8a5a2b"/><rect x="18" y="84" width="64" height="10" rx="4" fill="#8a5a2b"/>'
    '<path d="M26 16H74C74 36 56 44 56 50S74 64 74 84H26C26 64 44 56 44 50S26 36 26 16Z" fill="#e8f6ff" fill-opacity=".85" stroke="#6a86b3" stroke-width="2.5"/>'
    '<path d="M34 30H66C62 38 54 42 50 46C46 42 38 38 34 30Z M30 82C34 70 44 64 50 62C56 64 66 70 70 82Z" fill="#ffc94a"/>'
    '<path d="M50 46V62" stroke="#ffc94a" stroke-width="2"/>')
add("things", "paper_plane", '<polygon points="6,46 94,12 62,90 46,60" fill="#fff" stroke="#6a86b3" stroke-width="3" stroke-linejoin="round"/>'
    '<polygon points="46,60 94,12 52,82" fill="#d6e4f7" stroke="#6a86b3" stroke-width="2" stroke-linejoin="round"/>')
add("things", "sunglasses", '<path d="M8 36H92" stroke="#222" stroke-width="5" stroke-linecap="round"/>'
    '<path d="M12 36H44V50A16 16 0 0 1 12 50Z M56 36H88V50A16 16 0 0 1 56 50Z" fill="#ff4fd8" stroke="#222" stroke-width="4" stroke-linejoin="round"/>'
    '<path d="M18 42L26 50M62 42L70 50" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-opacity=".7"/>')
add("things", "bell", '<path d="M50 10A6 6 0 0 1 50 22" fill="none" stroke="#a37800" stroke-width="3"/><path d="M18 74C26 66 26 54 26 46A24 24 0 0 1 74 46C74 54 74 66 82 74Z" fill="#ffc21a" stroke="#a37800" stroke-width="3" stroke-linejoin="round"/>'
    '<circle cx="50" cy="80" r="7" fill="#a37800"/><path d="M36 34C38 30 42 28 46 28" fill="none" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-opacity=".7"/>')

# ---------------------------------------------------------------- write
for (cat, name), s in P.items():
    d = os.path.join(OUT, cat)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".svg"), "w") as f:
        f.write(s)
print(len(P), "props")
