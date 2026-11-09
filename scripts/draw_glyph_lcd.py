"""A 16x2 LCD with an I2C backpack, above the breadboard, wired to the Glyph C6.

Builds on the picture of the Glyph C6 powering the breadboard rails, made by
draw_glyph_breadboard.py, and adds:

- two jumpers at columns 29 and 30 that join the top rails to the bottom ones
- the LCD module above the breadboard, drawn after the robocraze product photo,
  with its four header pins on the left end, on female jumper wires:
  GND -> top - rail (column 8), VCC -> top + rail (column 10),
  SDA -> j15 (below SDA, GPIO4), SCL -> j16 (below SCL, GPIO5).
  SDA and SCL drop through the gaps in the rails at columns 13 and 19.

Usage:
    python3 scripts/draw_glyph_lcd.py \
        website/microcontrollers/images/glyph-c6-breadboard.svg \
        website/microcontrollers/images/glyph-c6-breadboard-lcd.svg
"""
import re, sys

P = 32                                # 0.1" pitch, as in draw_glyph_breadboard.py
def cx(col):
    return 125 + (col - 1) * P
ROW_J = 236
RAIL = {"top-": 106, "top+": 138, "bot+": 685, "bot-": 716}
METAL, METAL_DARK = "#C9CCD0", "#8C9096"
VY = -290                             # room above the breadboard for the LCD
LINES = ("Hello, world!", "Glyph C6")

svg = open(sys.argv[1]).read()
m = re.search(r'height="(\d+)" viewBox="(-?\d+) 0 (\d+) (\d+)"', svg)
H, VX, W = int(m.group(4)), m.group(2), m.group(3)
svg = svg.replace(m.group(0), f'height="{H-VY}" viewBox="{VX} {VY} {W} {H-VY}"', 1)
svg = svg.replace(f'<rect x="{VX}" width="{W}" height="{H}"',
                  f'<rect x="{VX}" y="{VY}" width="{W}" height="{H-VY}"', 1)

out = []
def add(s): out.append(s)

def stroke(d, colour, dark):
    add(f'<path d="{d}" stroke="{dark}" stroke-width="8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<path d="{d}" stroke="{colour}" stroke-width="5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')

def end(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="5" fill="{METAL}" stroke="{METAL_DARK}" stroke-width="1.5"/>')

# --- jumpers joining the top rails to the bottom ones -------------------------------
for col, y1, y2, colour, dark in ((29, RAIL["top+"], RAIL["bot+"], "#E04A44", "#A8302B"),
                                  (30, RAIL["top-"], RAIL["bot-"], "#3A3A3A", "#1A1A1A")):
    x = cx(col)
    stroke(f"M{x},{y1} C{x-10},{y1+30} {x-10},{y2-30} {x},{y2}", colour, dark)
    end(x, y1); end(x, y2)

# --- the LCD module --------------------------------------------------------------
L, R, T, B = 770, 1140, -262, -82     # PCB, about 80 x 36 mm, not to scale
PINS = {"GND": -220, "VCC": -188, "SDA": -156, "SCL": -124}
TIP = 728                             # where the wires leave the female jumpers
add(f'<rect x="{L}" y="{T}" width="{R-L}" height="{B-T}" rx="6" fill="#2E7D3A" stroke="#1F5A28" stroke-width="2"/>')
for hx in (L + 14, R - 14):
    for hy in (T + 14, B - 14):
        add(f'<circle cx="{hx}" cy="{hy}" r="7" fill="#EAE8E3" stroke="{METAL}" stroke-width="3"/>')
add(f'<rect x="795" y="-236" width="320" height="128" rx="4" fill="#1E1E1E"/>')
GL, GT, GW, GH = 808, -222, 294, 100  # the backlit glass
add(f'<rect x="{GL}" y="{GT}" width="{GW}" height="{GH}" rx="2" fill="#2F63D8"/>')
CW = (GW - 24) / 16
for row, line in enumerate(LINES):
    cy = GT + 30 + row * 40
    for i in range(16):
        x = GL + 12 + i * CW
        add(f'<rect x="{x+1:.1f}" y="{cy-15}" width="{CW-2:.1f}" height="30" fill="#3A70E4"/>')
        if i < len(line) and line[i] != " ":
            add(f'<text x="{x+CW/2:.1f}" y="{cy}" font-size="21" fill="#FFFFFF" text-anchor="middle" '
                f'dominant-baseline="central" font-family="\'IBM Plex Mono\', monospace">{line[i]}</text>')
for name, y in PINS.items():
    add(f'<rect x="{TIP+14}" y="{y-3}" width="{L-TIP-14}" height="6" fill="{METAL}" stroke="{METAL_DARK}"/>')

# --- wires from the header to the breadboard ---------------------------------------
RAD = 24
def drop(y, x, colour, dark):         # left from the header, then down at x
    return f"M{TIP},{y} L{x+RAD},{y} Q{x},{y} {x},{y+RAD}"
stroke(drop(PINS["GND"], cx(8), "", "") + f" L{cx(8)},{RAIL['top-']}", "#3A3A3A", "#1A1A1A")
stroke(drop(PINS["VCC"], cx(10), "", "") + f" L{cx(10)},{RAIL['top+']}", "#E04A44", "#A8302B")
stroke(drop(PINS["SDA"], cx(13), "", "") + f" L{cx(13)},165 C{cx(13)},205 {cx(15)},186 {cx(15)},{ROW_J}",
       "#3D7BE0", "#2856A8")
stroke(f"M{TIP},{PINS['SCL']} Q{cx(19)},{PINS['SCL']} {cx(19)},{PINS['SCL']+RAD} L{cx(19)},165 "
       f"C{cx(19)},205 {cx(16)},186 {cx(16)},{ROW_J}", "#3FA34D", "#2A7535")
for x, y in ((cx(8), RAIL["top-"]), (cx(10), RAIL["top+"]), (cx(15), ROW_J), (cx(16), ROW_J)):
    end(x, y)
for y in PINS.values():               # the female jumper housings, on top of the wires
    add(f'<rect x="{TIP-2}" y="{y-8}" width="18" height="16" rx="2" fill="#2A2A2A"/>')
for name, y in PINS.items():          # pin names over the wires; on the module they are on the back
    add(f'<text x="{TIP-10}" y="{y-13}" font-size="11" fill="#5A574F" font-weight="700" text-anchor="end" '
        f'dominant-baseline="central">{name}</text>')

aria = (" Two jumper wires join the top rails to the bottom ones: a red one at column 29 and a black one "
        "at column 30. A 16 by 2 LCD module sits above the breadboard, showing Hello, world! on the first "
        "line and Glyph C6 on the second. Four jumper wires run from the pins on its left end: GND to the "
        "top minus rail with a black wire, VCC to the top plus rail with a red wire, SDA to j15 with a blue "
        "wire, and SCL to j16 with a green wire.")
svg = svg.replace('" font-family=', aria + '" font-family=', 1)
svg = svg.replace("</svg>", "\n".join(out) + "\n</svg>")
open(sys.argv[2], "w").write(svg)
