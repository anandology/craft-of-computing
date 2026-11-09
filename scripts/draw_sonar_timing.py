"""Draw the HC-SR04 timing diagram: the Trig pulse, the sound going out and coming back,
and the Echo pulse, whose length is the time the sound took.

Usage:
    python3 scripts/draw_sonar_timing.py website/microcontrollers/images/hc-sr04-timing.svg
"""
import math
import sys

ACC, WASH = "#3C5A8A", "#DFE6F1"
PANEL, RULE, INK, MUTED = "#F5F1E8", "#DFD8C8", "#1A1916", "#8A8270"
SANS = "'IBM Plex Sans', system-ui, sans-serif"

W, H = 900, 350
X0, X1 = 150, 860                     # time runs left to right
HI = 34                               # height of a high signal
TRIG, SOUND, ECHO = 90, 175, 265      # baselines of the three rows
T_ON, T_OFF = 180, 210                # Trig high for 10 us
OUT0, OUT1 = 230, 290                 # the burst going out
BACK0, BACK1 = 620, 680               # the echo arriving

out = []
def add(s): out.append(s)
def text(x, y, s, size=17, fill=INK, anchor="middle", weight=400):
    add(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
        f'font-weight="{weight}" dominant-baseline="central">{s}</text>')
def signal(y, rises, falls):
    d = f"M{X0},{y} H{rises} V{y-HI} H{falls} V{y} H{X1}"
    add(f'<path d="{d}" stroke="{ACC}" stroke-width="3" fill="none" stroke-linejoin="round"/>')
def burst(x0, x1, y, amp):
    pts = [f"{x:.1f},{y - amp * math.sin((x - x0) / (x1 - x0) * 8 * 2 * math.pi):.1f}"
           for x in range(x0, x1 + 1)]
    add(f'<polyline points="{" ".join(pts)}" stroke="{ACC}" stroke-width="2.5" fill="none"/>')

add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" fill="{PANEL}" stroke="{RULE}"/>')
# guides where the Echo pulse starts and ends
for x in (OUT1, BACK0):                # broken where the sound labels sit
    for y1, y2 in ((SOUND - HI - 10, SOUND + 14), (SOUND + 46, ECHO + 10)):
        add(f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{MUTED}" '
            f'stroke-width="1.5" stroke-dasharray="5 5"/>')
for y, name in ((TRIG, "Trig"), (SOUND, "Sound"), (ECHO, "Echo")):
    text(X0 - 24, y - HI / 2, name, 18, INK, "end", 600)
add(f'<line x1="{X0}" y1="{SOUND}" x2="{X1}" y2="{SOUND}" stroke="{RULE}" stroke-width="2"/>')

signal(TRIG, T_ON, T_OFF)
text((T_ON + T_OFF) / 2, TRIG - HI - 18, "10 µs", 15, MUTED)
text(T_OFF + 18, TRIG - HI / 2, "the program sends a pulse", 15, MUTED, "start")

burst(OUT0, OUT1, SOUND, 16)
burst(BACK0, BACK1, SOUND, 7)
text((OUT0 + OUT1) / 2, SOUND + 30, "sound goes out", 15, MUTED)
text((BACK0 + BACK1) / 2, SOUND + 30, "echo comes back", 15, MUTED)

signal(ECHO, OUT1, BACK0)
# bracket under the Echo pulse: its length is the time
by = ECHO + 30
add(f'<path d="M{OUT1},{by-8} V{by} H{BACK0} V{by-8}" stroke="{INK}" stroke-width="1.8" fill="none"/>')
text((OUT1 + BACK0) / 2, by + 24, "Echo stays high while the sound travels there and back", 16, INK, weight=600)

aria = ("A timing diagram with three rows. Trig: the program holds it high for 10 microseconds. "
        "Sound: just after, the sensor sends a short burst of sound, and later a weaker echo comes back. "
        "Echo: it goes high when the burst has gone out and low when the echo comes back, so the length "
        "of the Echo pulse is the time the sound took to travel there and back.")
open(sys.argv[1], "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="{aria}" font-family="{SANS}">\n' + "\n".join(out) + "\n</svg>\n")
