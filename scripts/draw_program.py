"""Copy a program to the board, then the board runs it on its own.

Usage:
    python3 scripts/draw_program.py website/microcontrollers/introduction/images

Writes running-a-program.svg into the given directory.
"""
import sys
ACC, ACC_DARK, WASH = "#3C5A8A", "#2E466C", "#DFE6F1"
PANEL, RULE, INK, MUTED = "#F5F1E8", "#DFD8C8", "#1A1916", "#8A8270"
SANS = "'IBM Plex Sans', system-ui, sans-serif"
W, H = 780, 250
CY = 140
S = f'stroke="{ACC}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
p = [f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="8" fill="{PANEL}" stroke="{RULE}"/>',
     f'<line x1="{W/2}" y1="20" x2="{W/2}" y2="{H-20}" stroke="{RULE}" stroke-width="1.5"/>',
     f'<text x="24" y="38" font-size="12" letter-spacing="1.5" fill="{MUTED}">1. COPY THE PROGRAM</text>',
     f'<text x="{W/2+24}" y="38" font-size="12" letter-spacing="1.5" fill="{MUTED}">2. THE BOARD RUNS IT</text>']
def box(x, w, label, wash=False, icon=""):
    fill, stroke = (WASH, ACC) if wash else ("#FFFFFF", RULE)
    tx = x + (44 if icon else w / 2)
    anchor = "start" if icon else "middle"
    return (f'<rect x="{x}" y="{CY-26}" width="{w}" height="52" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="{2 if wash else 1.5}"/>'
            + icon + f'<text x="{tx}" y="{CY+5.5}" font-size="15" fill="{ACC_DARK if wash else INK}" '
            f'font-weight="{600 if wash else 400}" text-anchor="{anchor}">{label}</text>')
def arrow(x1, x2):
    return (f'<line x1="{x1}" y1="{CY}" x2="{x2-8}" y2="{CY}" stroke="{ACC}" stroke-width="1.6"/>'
            f'<path d="M{x2-9} {CY-4.5} L{x2} {CY} L{x2-9} {CY+4.5} z" fill="{ACC}"/>')
def muted(x, y, s):
    return f'<text x="{x}" y="{y}" font-size="13" fill="{MUTED}" text-anchor="middle">{s}</text>'
def monitor(x, y):
    return (f'<rect x="{x+1}" y="{y+3}" width="26" height="17" rx="2" {S}/>'
            f'<line x1="{x+14}" y1="{y+20}" x2="{x+14}" y2="{y+25}" {S}/><line x1="{x+8}" y1="{y+25}" x2="{x+20}" y2="{y+25}" {S}/>')
def plug(x, y):
    return (f'<rect x="{x+6}" y="{y+8}" width="16" height="12" rx="2" {S}/>'
            f'<line x1="{x+11}" y1="{y+3}" x2="{x+11}" y2="{y+8}" {S}/><line x1="{x+17}" y1="{y+3}" x2="{x+17}" y2="{y+8}" {S}/>'
            f'<line x1="{x+14}" y1="{y+20}" x2="{x+14}" y2="{y+26}" {S}/>')
def program(cx, cy):
    x, y = cx - 13, cy - 16
    lines = "".join(f'<line x1="{x+6}" y1="{y+9+i*6}" x2="{x+6+w}" y2="{y+9+i*6}" {S}/>' for i, w in enumerate((14, 10, 12)))
    return (f'<path d="M{x} {y} h18 l8 8 v24 h-26 z" fill="#FFFFFF" stroke="{ACC}" stroke-width="1.6" stroke-linejoin="round"/>' + lines)
# 1. computer -> board over USB, carrying the program
p.append(box(24, 140, "Computer", icon=monitor(36, CY-14)))
p.append(arrow(164, 246))
p.append(program(205, CY-36)); p.append(muted(205, CY-60, "program"))
p.append(muted(205, CY+28, "USB cable"))
p.append(box(246, 120, "Board", wash=True))
# 2. charger -> board, LED lit, no computer
X = W / 2
p.append(box(X+24, 134, "Charger", icon=plug(X+36, CY-14)))
p.append(arrow(X+158, X+236))
p.append(muted(X+197, CY+28, "power"))
p.append(box(X+236, 120, "Board", wash=True))
p.append(muted(X+296, CY+48, "running the program"))
# a lit LED wired to the board
lx, ly = X + 296, CY - 70
p.append(f'<line x1="{lx}" y1="{CY-26}" x2="{lx}" y2="{ly+14}" stroke="{ACC}" stroke-width="1.6"/>')
p.append(f'<path d="M{lx-6} {ly+14} V{ly+6} a6 6 0 0 1 12 0 V{ly+14} z" fill="#F2C744" stroke="{ACC}" stroke-width="1.6"/>')
for dx, dy in [(-1, -.2), (1, -.2), (-.6, -.9), (.6, -.9)]:
    p.append(f'<line x1="{lx+12*dx}" y1="{ly+4+12*dy}" x2="{lx+18*dx}" y2="{ly+4+18*dy}" stroke="#D9A21B" stroke-width="1.6" stroke-linecap="round"/>')
aria = ("Two steps. First, a computer copies a program to the board over a USB cable. "
        "Second, the board, powered by a charger and with no computer, runs the program and lights an LED.")
open(f"{sys.argv[1]}/running-a-program.svg", "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="{aria}" font-family="{SANS}">\n' + "\n".join(p) + "\n</svg>\n")
