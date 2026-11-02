"""Draw the Glyph C6 front with each pin labelled by its physical pin number and GPIO number.

Usage:
    curl -sL -o ov.avif \
        https://files.pcbcupid.com/Documentation/Boards/glyph_c6/PCBCUPID_esp32c6-overview_result.avif
    convert ov.avif ov.png
    convert ov.png -crop 410x915+100+135 +repage -fuzz 6% -fill none \
        -draw "color 0,0 floodfill" -draw "color 409,0 floodfill" \
        -draw "color 0,914 floodfill" -draw "color 409,914 floodfill" board.png
    convert board.png -rotate 180 board-rot.png
    python3 scripts/draw_pinout.py board-rot.png website/microcontrollers/introduction/images/glyph-c6-pinout.svg

The crop cuts the board out of PCBCupid's overview image and clears the
background; the rotation points the USB connector away from the reader.
"""
import base64, sys

ACC, ACC_DARK, WASH = "#3C5A8A", "#2E466C", "#DFE6F1"
PANEL, RULE, INK, MUTED = "#F5F1E8", "#DFD8C8", "#1A1916", "#8A8270"
RED = "#B3412F"
SANS = "'IBM Plex Sans', system-ui, sans-serif"

png, out = sys.argv[1], sys.argv[2]
SRC_W, SRC_H = 410, 915           # the cropped photo
S = 0.74                          # display scale
BW, BH = SRC_W * S, SRC_H * S
W, TOP = 780, 56
H = TOP + BH + 24
BX = (W - BW) / 2
# hole centres in the cropped photo
LX, RX = 29.5, 378.5
LY = [116, 160, 203, 246, 290, 334, 378, 421, 464, 508, 552, 597]
RY = [115, 158, 202, 246, 290, 334, 378, 422, 465, 509, 552, 596, 640, 684, 728, 771]

LEFT = ["GPIO5", "GPIO4", "GPIO3", "GPIO2", "GPIO1", "GPIO0", "GPIO6", "GPIO7", "GPIO8", "5V", "RST", "BAT"]
RIGHT = ["GND", "GPIO16", "GPIO17", "GPIO23", "GPIO22", "GPIO21", "GPIO20", "GPIO19", "GPIO18",
         "GPIO15", "GPIO14", "GPIO9", "GND", "3V3", "3V3", "RST"]  # pins 28 down to 13

def style(name):
    if name.startswith("GPIO"):
        return WASH, ACC, ACC_DARK
    if name == "3V3":
        return "#F6DDD8", RED, RED
    if name == "GND":
        return "#E4E1DA", INK, INK
    return "#FFFFFF", RULE, MUTED          # pins we do not use

def label(name, num, hx, hy, side):
    fill, stroke, text = style(name)
    pw, ph, r = 66, 22, 11
    if side == "left":
        cx = BX - 26
        px = cx - r - 8 - pw
    else:
        cx = BX + BW + 26
        px = cx + r + 8
    return (f'<line x1="{cx}" y1="{hy}" x2="{hx}" y2="{hy}" stroke="{MUTED}" stroke-width="1.2"/>'
            f'<circle cx="{hx}" cy="{hy}" r="3" fill="{MUTED}"/>'
            f'<circle cx="{cx}" cy="{hy}" r="{r}" fill="#FFFFFF" stroke="{MUTED}" stroke-width="1.2"/>'
            f'<text x="{cx}" y="{hy + 4}" text-anchor="middle" font-size="11" fill="{INK}">{num}</text>'
            f'<rect x="{px}" y="{hy - ph / 2}" width="{pw}" height="{ph}" rx="5" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
            f'<text x="{px + pw / 2}" y="{hy + 4.5}" text-anchor="middle" font-size="12.5" font-weight="600" fill="{text}">{name}</text>')

img = base64.b64encode(open(png, "rb").read()).decode()
parts = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{PANEL}" stroke="{RULE}"/>',
         f'<image x="{BX}" y="{TOP}" width="{BW}" height="{BH}" href="data:image/png;base64,{img}"/>']
# The photo is turned 180 degrees, so the USB connector points away from the reader,
# as it does on the breadboard: pins 1-12 run up the right edge, 13-28 down the left.
for i, (name, y) in enumerate(zip(LEFT, LY)):
    parts.append(label(name, i + 1, BX + (SRC_W - LX) * S, TOP + (SRC_H - y) * S, "right"))
for i, (name, y) in enumerate(zip(RIGHT, RY)):
    parts.append(label(name, 28 - i, BX + (SRC_W - RX) * S, TOP + (SRC_H - y) * S, "left"))
# column headings sit just above the topmost label on each side
for side, cx, hy in (("left", BX - 26, TOP + (SRC_H - RY[-1]) * S - 24),
                     ("right", BX + BW + 26, TOP + (SRC_H - LY[-1]) * S - 24)):
    pc = cx - 11 - 8 - 33 if side == "left" else cx + 11 + 8 + 33
    parts.append(f'<text x="{cx}" y="{hy}" text-anchor="middle" font-size="11" letter-spacing="1.2" fill="{MUTED}">PIN</text>')
    parts.append(f'<text x="{pc}" y="{hy}" text-anchor="middle" font-size="11" letter-spacing="1.2" fill="{MUTED}">GPIO</text>')
with open(out, "w") as f:
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H:.0f}" viewBox="0 0 {W} {H:.0f}" role="img" '
            f'aria-label="The Glyph C6 with each pin labelled by its physical pin number and its GPIO number. The USB connector is at the top. Pins 1 to 12 run up the right edge and pins 13 to 28 run down the left edge." '
            f'font-family="{SANS}">\n' + "\n".join(parts) + "\n</svg>\n")
