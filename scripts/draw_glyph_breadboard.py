"""Glyph C6 on a breadboard: 3V3 to the lower + rail, GND to the lower - rail.

Breadboard drawn in the style of breadboard-led.png (breadboard.build).
Board photo cut from the PCBCupid pinout (argv[2]): header rows 0.8" apart (rows c and i),
16-pin edge (pins 13-28) in row c, pin 13 in column 1, USB end to the left.

Usage:
    uv run --with pillow python scripts/draw_glyph_breadboard.py \
        website/microcontrollers/images/glyph-c6-breadboard.svg PINOUT.png
    uv run --with pillow python scripts/draw_glyph_breadboard.py \
        website/microcontrollers/images/glyph-c6-breadboard-led.svg PINOUT.png --led

With --led, it adds the LED circuit of breadboard-led.png in columns 23-28:
+ rail -> a23, LED e23 (anode) to e25, 330 ohm resistor d25-d28, a28 -> - rail.
With --d15 as well, the + rail -> a23 jumper is replaced by a yellow jumper
from a7 (below D15) to a23, so a program switches the LED through GPIO15:
    ... glyph-c6-breadboard-d15.svg PINOUT.png --led --d15

PINOUT.png is PCBCupid's Glyph C6 pinout image at its full 5168x3669 size;
the crop coordinates below are in its pixels. Download it from:

    https://files.pcbcupid.com/Documentation/Boards/glyph_c6/PCBCUPID_GlyphC6_DEVKIT_Pinout_PNG.png
"""
import sys

P = 32                                # 0.1" pitch
SANS = "'IBM Plex Sans', system-ui, sans-serif"
BG, BOARD, EDGE, HOLE = "#EAE8E3", "#FAF9F5", "#D9D6CF", "#2A2A2A"
RED, BLUE, LABEL = "#D9534F", "#4A7FD6", "#8A877F"

def cx(col):                          # column 1..30
    return 125 + (col - 1) * P

ROW = {"j": 236, "i": 268, "h": 300, "g": 332, "f": 364,
       "e": 460, "d": 492, "c": 524, "b": 556, "a": 588}
RAIL = {"top-": 106, "top+": 138, "bot+": 685, "bot-": 716}
RAIL_COLS = [c for g in range(5) for c in range(2 + 6 * g, 7 + 6 * g)]

out = []
def add(s): out.append(s)

def hole(x, y):
    add(f'<rect x="{x-8}" y="{y-8}" width="16" height="16" rx="3" fill="{EDGE}"/>'
        f'<rect x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="{HOLE}"/>')

def text(x, y, s, size=13, fill=LABEL, anchor="middle", weight=400):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}" dominant-baseline="central">{s}</text>')

# --- breadboard ---------------------------------------------------------------
W, H = 1160, 800
VX = -80                              # room on the left for the USB cable
add(f'<rect x="{VX}" width="{W-VX}" height="{H}" fill="{BG}"/>')
add(f'<rect x="83" y="64" width="1012" height="693" rx="10" fill="{BOARD}" stroke="{EDGE}" stroke-width="2"/>')
add(f'<rect x="85" y="384" width="1008" height="52" fill="#E6E3DC"/>')
for y, c in [(88, BLUE), (157, RED), (664, RED), (734, BLUE)]:
    add(f'<line x1="106" y1="{y}" x2="1072" y2="{y}" stroke="{c}" stroke-width="3"/>')
for key, y in RAIL.items():
    for col in RAIL_COLS:
        hole(cx(col), y)
    sign, colr = ("+", RED) if key.endswith("+") else ("−", BLUE)
    text(103, y, sign, 15, colr, weight=700)
for r, y in ROW.items():
    for col in range(1, 31):
        hole(cx(col), y)
    text(101, y, r); text(1076, y, r)
for col in range(5, 31, 5):
    text(cx(col), 216, col); text(cx(col), 617, col)

# --- Glyph C6, cut from the PCBCupid pinout image --------------------------------
from PIL import Image, ImageDraw
import base64, io
PIT = 87.3                                  # pin pitch in the pinout image
X0, Y0, X1, Y1 = 2744, 612, 3542, 2420      # board + USB-C in the pinout image
src = Image.open(sys.argv[2]).convert("RGBA").crop((X0, Y0, X1, Y1))
mask = Image.new("L", src.size, 0)
md = ImageDraw.Draw(mask)
md.rounded_rectangle((0, 0, X1 - X0, 2370 - Y0), radius=115, fill=255)
md.rounded_rectangle((2988 - X0, 2290 - Y0, 3310 - X0, Y1 - Y0), radius=20, fill=255)
src.putalpha(mask)
rot = src.rotate(-90, expand=True)          # clockwise: USB to the left, pins 13-28 at the bottom
s = P / PIT
RET = 2                                     # pixels per drawing unit, for sharp screens
rot = rot.resize((round(rot.width * s * RET), round(rot.height * s * RET)), Image.LANCZOS)
buf = io.BytesIO(); rot.save(buf, "PNG", optimize=True)
h = Y1 - Y0                                 # crop height before rotation
px13, py13 = (h - 1 - (2140 - Y0)), (3491.6 - X0)   # pin 13 in the rotated crop
IX, IY = cx(1) - px13 * s, ROW["c"] - py13 * s
# USB cable off the left edge
MID = IY + (3149 - X0) * s
add(f'<path d="M-80,{MID} L{IX-30},{MID}" stroke="#3A3A3A" stroke-width="12" fill="none"/>')
add(f'<rect x="{IX-44}" y="{MID-22}" width="44" height="44" rx="6" fill="#3A3A3A"/>')
add(f'<image href="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}" '
    f'x="{IX:.1f}" y="{IY:.1f}" width="{rot.width/RET:.1f}" height="{rot.height/RET:.1f}"/>')

# --- jumper wires ---------------------------------------------------------------
def wire(col, y1, y2, colour, dark):
    x = cx(col)
    d = f"M{x},{y1} C{x-10},{y1+30} {x-10},{y2-30} {x},{y2}"
    add(f'<path d="{d}" stroke="{dark}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        f'<path d="{d}" stroke="{colour}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    for y in (y1, y2):
        add(f'<circle cx="{x}" cy="{y}" r="5" fill="#C9CCD0" stroke="#8C9096" stroke-width="1.5"/>')
wire(2, ROW["a"], RAIL["bot+"], "#E04A44", "#A8302B")     # 3V3 (pin 14) -> + rail
wire(16, ROW["a"], RAIL["bot-"], "#3A3A3A", "#1A1A1A")    # GND (pin 28) -> - rail
text(cx(16) + 10, 654 if "--d15" in sys.argv else 642, "GND", 12, "#3A3A3A", "start", 700)  # below the D15 jumper
text(cx(2) + 10, 642, "3V3", 12, "#C0392B", "start", 700)

aria = ("A Glyph C6 board at the left end of a breadboard, straddling the centre gap with its pins in rows c and i "
        "and its USB cable to the left. A red jumper wire connects a2, below the 3V3 pin, to the lower "
        "plus rail. A black jumper wire connects a16, below the last GND pin, to the lower minus rail.")

# --- with --led: the LED circuit of breadboard-led.png, moved 14 columns right ----------
if "--led" in sys.argv:
    A, K, R2 = 23, 25, 28               # LED anode, LED cathode (= resistor start), resistor end
    # glow first, so the parts stay sharp on top of it
    lx, ly = (cx(A) + cx(K)) / 2, 437
    add('<defs><radialGradient id="glow"><stop offset="0" stop-color="#FFF6E8" stop-opacity="0.95"/>'
        '<stop offset="0.3" stop-color="#FFD6C8" stop-opacity="0.55"/>'
        '<stop offset="1" stop-color="#FFB09A" stop-opacity="0"/></radialGradient></defs>')
    add(f'<circle cx="{lx}" cy="{ly}" r="140" fill="url(#glow)"/>')
    D15 = "--d15" in sys.argv
    if not D15:
        wire(A, ROW["a"], RAIL["bot+"], "#3D7BE0", "#2856A8")    # + rail -> a23, row 23 -> anode
    wire(R2, ROW["a"], RAIL["bot-"], "#3FA34D", "#2A7535")   # a28 -> - rail
    # resistor, 330 ohm: orange orange brown, gold tolerance
    y = ROW["d"]; x1, x2 = cx(K), cx(R2); bx0, bx1 = x1 + 22, x2 - 22
    add(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#A9ADB2" stroke-width="3"/>')
    add(f'<rect x="{bx0}" y="{y-9}" width="{bx1-bx0}" height="18" rx="8" fill="#E8C391" stroke="#C9A06A"/>')
    for i, c in enumerate(("#E8892B", "#E8892B", "#8B4A1F")):
        add(f'<rect x="{bx0 + 10 + i * 9}" y="{y-9}" width="5" height="18" fill="{c}"/>')
    add(f'<rect x="{bx1 - 14}" y="{y-9}" width="5" height="18" fill="#C9A23A"/>')
    for x in (x1, x2):
        add(f'<circle cx="{x}" cy="{y}" r="4" fill="#C9CCD0" stroke="#8C9096"/>')
    # LED: legs from e23 and e25 up to the body over the centre gap
    for x in (cx(A), cx(K)):
        add(f'<line x1="{x}" y1="{ROW["e"]}" x2="{lx + (x - lx) * 0.35}" y2="{ly + 8}" stroke="#A9ADB2" stroke-width="3"/>'
            f'<circle cx="{x}" cy="{ROW["e"]}" r="4" fill="#C9CCD0" stroke="#8C9096"/>')
    # flat side of the rim marks the cathode, toward e25
    add(f'<circle cx="{lx}" cy="{ly}" r="20" fill="#F26B5B" stroke="#C94535" stroke-width="2"/>'
        f'<circle cx="{lx}" cy="{ly}" r="12" fill="#FFC2B6"/>'
        f'<path d="M{lx+20},{ly+8} L{lx+20},{ly-8}" stroke="#C94535" stroke-width="5"/>')
    if D15:                             # D15 (pin 19, column 7) -> a23, dipping below row a
        x1, x2, y = cx(7), cx(A), ROW["a"]
        d = f"M{x1},{y} C{x1},{y+52} {x2},{y+52} {x2},{y}"
        add(f'<path d="{d}" stroke="#B7841A" stroke-width="8" fill="none" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="#F0B429" stroke-width="5" fill="none" stroke-linecap="round"/>')
        for x in (x1, x2):
            add(f'<circle cx="{x}" cy="{y}" r="5" fill="#C9CCD0" stroke="#8C9096" stroke-width="1.5"/>')
        text(x1 - 10, 612, "D15", 12, "#9A6B00", "end", 700)
    aria += ((" A yellow jumper wire connects a7, below the D15 pin, to a23." if D15 else
              " A blue jumper wire connects the plus rail to a23.") + " A red LED has its anode in e23 and its cathode "
             "in e25. A 330 ohm resistor runs from d25 to d28, and a green jumper wire connects a28 to the "
             "minus rail. The LED is lit.")
open(sys.argv[1], "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W-VX}" height="{H}" viewBox="{VX} 0 {W-VX} {H}" role="img" '
    f'aria-label="{aria}" font-family="{SANS}">\n' + "\n".join(out) + "\n</svg>\n")
