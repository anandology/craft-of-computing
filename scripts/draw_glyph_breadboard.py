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
With --pot as well, a 10k potentiometer stands above the breadboard, on female
jumper wires: wiper -> j11 (below A0, GPIO0), outer lugs -> top - and + rails,
and two jumpers at columns 29 and 30 join the top rails to the bottom ones:
    ... glyph-c6-breadboard-pot.svg PINOUT.png --led --d15 --pot
With --sonar as well (instead of --pot), the breadboard is full length, 60 columns,
and an HC-SR04 stands in e44-e47 (Vcc, Trig, Echo, Gnd), facing the reader:
a44 -> + rail, a47 -> - rail, D19 (a9) -> c45 (Trig), D18 (a8) -> c46 (Echo):
    ... glyph-c6-breadboard-sonar.svg PINOUT.png --led --d15 --sonar
With --button as well (instead of --pot or --sonar), the breadboard is full length,
a 12 mm push button straddles the centre gap with its pins in d34, d36, g34, g36,
and the LED is drawn off. Without --d15, the button switches the LED by itself:
+ rail -> a36 and a34 -> a23 (the LED's anode), with no wire from the board to the LED.
The pins across the gap are joined inside the button, so 34 and 36 are its two sides:
    ... glyph-c6-breadboard-button.svg PINOUT.png --led --button
With --d15, the board reads the button: D7 (j9) -> j34, over the top of the board,
and a36 -> - rail:
    ... glyph-c6-breadboard-button-d7.svg PINOUT.png --led --d15 --button

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

out = []
def add(s): out.append(s)

def hole(x, y):
    add(f'<rect x="{x-8}" y="{y-8}" width="16" height="16" rx="3" fill="{EDGE}"/>'
        f'<rect x="{x-6}" y="{y-6}" width="12" height="12" rx="2" fill="{HOLE}"/>')

def text(x, y, s, size=13, fill=LABEL, anchor="middle", weight=400):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}" dominant-baseline="central">{s}</text>')

# --- breadboard ---------------------------------------------------------------
SONAR = "--sonar" in sys.argv
BUTTON = "--button" in sys.argv
NCOL = 60 if SONAR or BUTTON else 30  # the sensor and the button need a full-length breadboard
EXT = (NCOL - 30) * P
W, H = 1160 + EXT, 800
VX = -80                              # room on the left for the USB cable
POT = "--pot" in sys.argv
VY = -310 if POT else 0               # room above for the potentiometer
add(f'<rect x="{VX}"' + (f' y="{VY}"' if VY else '') + f' width="{W-VX}" height="{H-VY}" fill="{BG}"/>')
RAIL_COLS = [c for g in range(NCOL // 6) for c in range(2 + 6 * g, 7 + 6 * g)]
add(f'<rect x="83" y="64" width="{1012+EXT}" height="693" rx="10" fill="{BOARD}" stroke="{EDGE}" stroke-width="2"/>')
add(f'<rect x="85" y="384" width="{1008+EXT}" height="52" fill="#E6E3DC"/>')
for y, c in [(88, BLUE), (157, RED), (664, RED), (734, BLUE)]:
    add(f'<line x1="106" y1="{y}" x2="{1072+EXT}" y2="{y}" stroke="{c}" stroke-width="3"/>')
for key, y in RAIL.items():
    for col in RAIL_COLS:
        hole(cx(col), y)
    sign, colr = ("+", RED) if key.endswith("+") else ("−", BLUE)
    text(103, y, sign, 15, colr, weight=700)
for r, y in ROW.items():
    for col in range(1, NCOL + 1):
        hole(cx(col), y)
    text(101, y, r); text(1076 + EXT, y, r)
for col in range(5, NCOL + 1, 5):
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
if SONAR:                             # left of the wire, above the D18 and D19 jumpers
    text(cx(16) - 10, 612, "GND", 12, "#3A3A3A", "end", 700)
else:                                 # below the D15 jumper
    text(cx(16) + 10, 654 if "--d15" in sys.argv else 642, "GND", 12, "#3A3A3A", "start", 700)
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
    if not BUTTON:                      # with the button, the LED is drawn off
        add(f'<circle cx="{lx}" cy="{ly}" r="140" fill="url(#glow)"/>')
    D15 = "--d15" in sys.argv
    if not D15 and not BUTTON:
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
              "" if BUTTON else " A blue jumper wire connects the plus rail to a23.") + " A red LED has its anode in e23 and its cathode "
             "in e25. A 330 ohm resistor runs from d25 to d28, and a green jumper wire connects a28 to the "
             "minus rail." + ("" if BUTTON else " The LED is lit."))
# --- with --pot: a potentiometer above the board, wiper to A0 ----------------------
def lead(x1, y1, x2, y2, colour, dark, knee=None):
    if knee:                            # straight down to the knee, then bend across
        d = f"M{x1},{y1} L{x1},{knee} C{x1},{knee+40} {x2},{y2-50} {x2},{y2}"
    else:
        d = f"M{x1},{y1} C{x1},{(y1+y2)/2} {x2},{(y1+y2)/2} {x2},{y2}"
    add(f'<path d="{d}" stroke="{dark}" stroke-width="8" fill="none" stroke-linecap="round"/>'
        f'<path d="{d}" stroke="{colour}" stroke-width="5" fill="none" stroke-linecap="round"/>')
    add(f'<circle cx="{x2}" cy="{y2}" r="5" fill="#C9CCD0" stroke="#8C9096" stroke-width="1.5"/>')

if POT:
    wire(29, RAIL["top+"], RAIL["bot+"], "#E04A44", "#A8302B")    # top + rail <-> bottom + rail
    wire(30, RAIL["top-"], RAIL["bot-"], "#3A3A3A", "#1A1A1A")    # top - rail <-> bottom - rail
    X = cx(13)                          # wiper lug over column 13, a gap in the rails
    LUGS = (X - 2 * P, X, X + 2 * P)    # 0.2" apart, as on the part
    METAL, METAL_DARK = "#C9CCD0", "#8C9096"
    # legs, with a female jumper pushed onto each
    for x in LUGS:
        add(f'<rect x="{x-5}" y="-62" width="10" height="44" fill="{METAL}" stroke="{METAL_DARK}"/>')
    # body: brown phenolic case with an eyelet over each leg
    add(f'<rect x="{X-104}" y="-152" width="208" height="92" rx="8" fill="#B5582A" stroke="#8A3F1C" stroke-width="2"/>')
    for x in LUGS:
        add(f'<circle cx="{x}" cy="-88" r="12" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="1.5"/>'
            f'<circle cx="{x}" cy="-88" r="4.5" fill="#6B3A1E"/>')
    # mounting plate, threaded bushing and knurled shaft with its slot
    add(f'<rect x="{X-116}" y="-176" width="232" height="30" rx="6" fill="#B8BCC2" stroke="{METAL_DARK}" stroke-width="1.5"/>')
    add(f'<rect x="{X-38}" y="-218" width="76" height="44" fill="#A9ADB2" stroke="{METAL_DARK}" stroke-width="1.5"/>')
    for y in range(-212, -176, 6):
        add(f'<line x1="{X-38}" y1="{y}" x2="{X+38}" y2="{y}" stroke="{METAL_DARK}" stroke-width="1"/>')
    add(f'<rect x="{X-28}" y="-298" width="56" height="82" rx="4" fill="#D4D7DB" stroke="{METAL_DARK}" stroke-width="1.5"/>')
    for x in range(X - 21, X + 22, 7):
        add(f'<line x1="{x}" y1="-292" x2="{x}" y2="-220" stroke="#A9ADB2" stroke-width="1.5"/>')
    add(f'<rect x="{X-3}" y="-298" width="6" height="26" fill="#6E7278"/>')
    # a curved arrow: turn the knob
    add(f'<path d="M{X-58},-252 A62,22 0 0 0 {X+52},-246" stroke="{LABEL}" stroke-width="2.5" fill="none"/>'
        f'<path d="M{X+60},-252 L{X+44},-252 L{X+54},-238 Z" fill="{LABEL}"/>')
    text(X + 122, -105, "10 kΩ", 15, "#5A574F", "start", 700)
    # jumper wires from the lugs: left -> top - rail, wiper -> j11 (A0), right -> top + rail
    lead(LUGS[0], -18, cx(11), RAIL["top-"], "#3A3A3A", "#1A1A1A")
    lead(LUGS[1], -18, cx(11), ROW["j"], "#9B6BD6", "#6E45A8", knee=165)   # through the rail gap
    lead(LUGS[2], -18, cx(15), RAIL["top+"], "#E04A44", "#A8302B")
    for x in LUGS:
        add(f'<rect x="{x-8}" y="-30" width="16" height="28" rx="2" fill="#2A2A2A"/>')
    text(cx(11) - 10, 186, "A0", 12, "#6E45A8", "end", 700)
    aria += (" A 10 kilohm potentiometer stands above the breadboard, its knob pointing up. A purple jumper "
             "wire connects its middle lug to j11, above the A0 pin. Its left lug connects to the top minus "
             "rail with a black wire, and its right lug to the top plus rail with a red wire. A red jumper "
             "wire joins the top plus rail to the bottom plus rail at column 29, and a black jumper wire joins "
             "the top minus rail to the bottom minus rail at column 30.")

# --- with --sonar: an HC-SR04 ultrasonic sensor standing in row e, facing the reader --
if SONAR:
    VCC, TRIG, ECHO, GND = 44, 45, 46, 47          # its pins, in row e
    wire(VCC, ROW["a"], RAIL["bot+"], "#E04A44", "#A8302B")    # a44 -> + rail (3V3)
    wire(GND, ROW["a"], RAIL["bot-"], "#3A3A3A", "#1A1A1A")    # a47 -> - rail
    # D19 (pin 21, column 9) -> c45 (Trig) and D18 (pin 20, column 8) -> c46 (Echo),
    # dipping below row a, one inside the other so they do not cross
    for x1, x2, low, colour, dark in ((cx(9), cx(TRIG), 668, "#F08A24", "#B4621A"),
                                      (cx(8), cx(ECHO), 692, "#3D7BE0", "#2856A8")):
        y1, y2 = ROW["a"], ROW["c"]
        d = f"M{x1},{y1} C{x1},{low} {x2},{low} {x2},{y2}"
        add(f'<path d="{d}" stroke="{dark}" stroke-width="8" fill="none" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="{colour}" stroke-width="5" fill="none" stroke-linecap="round"/>')
        for x, y in ((x1, y1), (x2, y2)):
            add(f'<circle cx="{x}" cy="{y}" r="5" fill="#C9CCD0" stroke="#8C9096" stroke-width="1.5"/>')
    # the sensor, drawn face-on as if standing up from row e: legs, header, board
    METAL, METAL_DARK = "#C9CCD0", "#8C9096"
    X = (cx(VCC) + cx(GND)) / 2
    PW, TOP, BOT = 567, 152, 404                   # 45 x 20 mm board
    for col in (VCC, TRIG, ECHO, GND):
        add(f'<rect x="{cx(col)-3}" y="{BOT+16}" width="6" height="{ROW["e"]-BOT-16}" fill="{METAL}" stroke="{METAL_DARK}"/>'
            f'<circle cx="{cx(col)}" cy="{ROW["e"]}" r="4" fill="{METAL}" stroke="{METAL_DARK}"/>')
    add(f'<rect x="{cx(VCC)-16}" y="{BOT}" width="{cx(GND)-cx(VCC)+32}" height="18" rx="2" fill="#2A2A2A"/>')
    add(f'<rect x="{X-PW/2}" y="{TOP}" width="{PW}" height="{BOT-TOP}" rx="6" fill="#1F5FA8" stroke="#16457A" stroke-width="2"/>')
    for hx in (X - PW/2 + 16, X + PW/2 - 16):
        for hy in (TOP + 16, BOT - 16):
            add(f'<circle cx="{hx}" cy="{hy}" r="8" fill="{BG}" stroke="{METAL}" stroke-width="3"/>')
    add('<defs><pattern id="mesh" width="7" height="7" patternUnits="userSpaceOnUse">'
        '<rect width="7" height="7" fill="#33363B"/><circle cx="3.5" cy="3.5" r="1.6" fill="#5A5E65"/></pattern></defs>')
    CY = (TOP + BOT) / 2
    for dx, name in ((-164, "T"), (164, "R")):  # transmitter left, receiver right
        add(f'<circle cx="{X+dx}" cy="{CY}" r="101" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="2"/>'
            f'<circle cx="{X+dx}" cy="{CY}" r="84" fill="url(#mesh)" stroke="#6E7278" stroke-width="2"/>')
        text(X + dx * 0.42, TOP + 37, name, 15, "#FFFFFF", weight=700)
    add(f'<rect x="{X-30}" y="{TOP+70}" width="60" height="22" rx="11" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="1.5"/>')
    text(X, CY + 70, "HC-SR04", 14, "#FFFFFF", weight=700)
    for col, name in ((VCC, "Vcc"), (TRIG, "Trig"), (ECHO, "Echo"), (GND, "Gnd")):
        text(cx(col), BOT - 12, name, 10, "#FFFFFF", weight=600)
    aria += (" The breadboard is twice as long. Further along, an HC-SR04 ultrasonic sensor stands with its "
             "pins in e44 to e47, Vcc, Trig, Echo and Gnd, and its two round transducers facing the near edge "
             "of the breadboard. A red jumper wire connects a44 to the plus rail, and a black one connects a47 "
             "to the minus rail. An orange jumper wire connects a9, below the D19 pin, to c45, the Trig "
             "column, and a blue one connects a8, below the D18 pin, to c46, the Echo column.")

# --- with --button: a 12 mm push button across the centre gap, D7 to one side, GND to the other --
if BUTTON:
    A, B = 34, 36                                  # its pins: d34, g34 and d36, g36
    METAL, METAL_DARK = "#C9CCD0", "#8C9096"
    X, Y = cx(35), 410                             # middle of the centre gap
    if "--d15" in sys.argv:                        # the board reads the button
        wire(B, ROW["a"], RAIL["bot-"], "#3A3A3A", "#1A1A1A")      # a36 -> - rail
        # D7 (pin 8, column 9, row i) -> j34, up over the column numbers and along
        x1, x2, y, top = cx(9), cx(A), ROW["j"], 172
        d = (f"M{x1},{y} L{x1},{top+28} Q{x1},{top} {x1+28},{top} L{x2-28},{top} "
             f"Q{x2},{top} {x2},{top+28} L{x2},{y}")
        add(f'<path d="{d}" stroke="#2E9C9A" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<path d="{d}" stroke="#49C2BF" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
        for x in (x1, x2):
            add(f'<circle cx="{x}" cy="{y}" r="5" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="1.5"/>')
        text(x1 - 10, 200, "D7", 12, "#237A78", "end", 700)
        aria += (" The breadboard is twice as long. Further along, a square push button straddles the centre "
                 "gap, with its four pins in d34, d36, g34 and g36. A teal jumper wire runs from j9, above the "
                 "D7 pin, over the column numbers to j34. A black jumper wire connects a36 to the minus rail. "
                 "The LED is off.")
    else:                                          # 3.3 V through the button to the LED
        wire(B, ROW["a"], RAIL["bot+"], "#E04A44", "#A8302B")         # a36 -> + rail
        x1, x2, y = cx(A), cx(23), ROW["a"]                           # a34 -> a23, below row a
        d = f"M{x1},{y} C{x1},{y+52} {x2},{y+52} {x2},{y}"
        add(f'<path d="{d}" stroke="#2856A8" stroke-width="8" fill="none" stroke-linecap="round"/>'
            f'<path d="{d}" stroke="#3D7BE0" stroke-width="5" fill="none" stroke-linecap="round"/>')
        for x in (x1, x2):
            add(f'<circle cx="{x}" cy="{y}" r="5" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="1.5"/>')
        aria += (" The breadboard is twice as long. Further along, a square push button straddles the centre "
                 "gap, with its four pins in d34, d36, g34 and g36. A red jumper wire connects a36 to the plus "
                 "rail. A blue jumper wire connects a34 to a23, the LED's anode. The LED is off.")
    # legs, 5 mm apart along the breadboard and 12.5 mm across the gap
    for col in (A, B):
        for r, dy in (("g", 1), ("d", -1)):
            add(f'<rect x="{cx(col)-5}" y="{min(ROW[r], Y + dy * -60)}" width="10" '
                f'height="{abs(ROW[r] - (Y + dy * -60))}" fill="{METAL}" stroke="{METAL_DARK}"/>'
                f'<circle cx="{cx(col)}" cy="{ROW[r]}" r="4" fill="{METAL}" stroke="{METAL_DARK}"/>')
    # body, 12 mm square: black base, metal plate with four rivets, round cap
    add(f'<rect x="{X-75}" y="{Y-75}" width="150" height="150" rx="8" fill="#232323" stroke="#111111" stroke-width="2"/>')
    add(f'<rect x="{X-64}" y="{Y-64}" width="128" height="128" rx="4" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="1.5"/>')
    for dx in (-50, 50):
        for dy in (-50, 50):
            add(f'<circle cx="{X+dx}" cy="{Y+dy}" r="6" fill="#6E7278"/>')
    add(f'<circle cx="{X}" cy="{Y}" r="44" fill="#1A1A1A" stroke="#000000" stroke-width="2"/>'
        f'<circle cx="{X-10}" cy="{Y-12}" r="20" fill="#2C2C2C"/>')

open(sys.argv[1], "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W-VX}" height="{H-VY}" viewBox="{VX} {VY} {W-VX} {H-VY}" role="img" '
    f'aria-label="{aria}" font-family="{SANS}">\n' + "\n".join(out) + "\n</svg>\n")
