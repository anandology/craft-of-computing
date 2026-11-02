"""Draw the computer and microcontroller diagrams for the first unit-3 lesson.

Usage:
    python3 scripts/draw_intro_diagrams.py website/microcontrollers/introduction/images

Writes computer.svg and microcontroller.svg into the given directory.
"""
import sys

ACC, ACC_DARK, WASH = "#3C5A8A", "#2E466C", "#DFE6F1"
PANEL, RULE, INK, MUTED = "#F5F1E8", "#DFD8C8", "#1A1916", "#8A8270"
SANS = "'IBM Plex Sans', system-ui, sans-serif"

W, H = 780, 300
ITEM_W, ITEM_H = 200, 44
LX, RX = 24, W - 24 - ITEM_W
BOX_W, BOX_H = 176, 76
BX = (W - BOX_W) / 2


def icon(kind, x, y):
    """A 28x28 line icon with its top-left corner at (x, y)."""
    s = f'stroke="{ACC}" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "keyboard":
        keys = "".join(
            f'<rect x="{x + 4 + c * 5}" y="{y + 9 + r * 4.5}" width="2.6" height="2" fill="{ACC}"/>'
            for r in range(2) for c in range(4))
        return (f'<rect x="{x + 1}" y="{y + 6}" width="26" height="16" rx="2.5" {s}/>' + keys +
                f'<line x1="{x + 8}" y1="{y + 18.5}" x2="{x + 20}" y2="{y + 18.5}" {s}/>')
    if kind == "mouse":
        return (f'<rect x="{x + 8}" y="{y + 3}" width="12" height="22" rx="6" {s}/>'
                f'<line x1="{x + 14}" y1="{y + 4}" x2="{x + 14}" y2="{y + 11}" {s}/>')
    if kind == "monitor":
        return (f'<rect x="{x + 1}" y="{y + 3}" width="26" height="17" rx="2" {s}/>'
                f'<line x1="{x + 14}" y1="{y + 20}" x2="{x + 14}" y2="{y + 25}" {s}/>'
                f'<line x1="{x + 8}" y1="{y + 25}" x2="{x + 20}" y2="{y + 25}" {s}/>')
    if kind == "speaker":
        return (f'<path d="M{x + 3} {y + 11} h5 l7 -6 v18 l-7 -6 h-5 z" {s}/>'
                f'<path d="M{x + 19} {y + 10} q3 4 0 8" {s}/><path d="M{x + 22} {y + 7} q6 7 0 14" {s}/>')
    if kind == "thermometer":
        return (f'<path d="M{x + 11} {y + 17} V{y + 5} a3 3 0 0 1 6 0 V{y + 17}" {s}/>'
                f'<circle cx="{x + 14}" cy="{y + 21}" r="5" {s}/>'
                f'<circle cx="{x + 14}" cy="{y + 21}" r="2.2" fill="{ACC}"/>')
    if kind == "light":
        rays = "".join(
            f'<line x1="{x + 14 + 8 * dx}" y1="{y + 14 + 8 * dy}" x2="{x + 14 + 12 * dx}" y2="{y + 14 + 12 * dy}" {s}/>'
            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7)])
        return f'<circle cx="{x + 14}" cy="{y + 14}" r="5" {s}/>' + rays
    if kind == "button":
        return (f'<rect x="{x + 3}" y="{y + 3}" width="22" height="22" rx="3" {s}/>'
                f'<circle cx="{x + 14}" cy="{y + 14}" r="6" fill="{ACC}"/>')
    if kind == "led":
        return (f'<path d="M{x + 8} {y + 18} V{y + 10} a6 6 0 0 1 12 0 V{y + 18} z" {s}/>'
                f'<line x1="{x + 6}" y1="{y + 18}" x2="{x + 22}" y2="{y + 18}" {s}/>'
                f'<line x1="{x + 11}" y1="{y + 18}" x2="{x + 11}" y2="{y + 26}" {s}/>'
                f'<line x1="{x + 17}" y1="{y + 18}" x2="{x + 17}" y2="{y + 24}" {s}/>')
    if kind == "fan":
        blades = "".join(
            f'<ellipse cx="{x + 14}" cy="{y + 8}" rx="3.6" ry="6" transform="rotate({a} {x + 14} {y + 14})" {s}/>'
            for a in (0, 120, 240))
        return blades + f'<circle cx="{x + 14}" cy="{y + 14}" r="2" fill="{ACC}"/>'
    if kind == "relay":
        return (f'<rect x="{x + 1}" y="{y + 4}" width="26" height="20" rx="2.5" {s}/>'
                f'<circle cx="{x + 7}" cy="{y + 17}" r="1.8" fill="{ACC}"/>'
                f'<circle cx="{x + 21}" cy="{y + 17}" r="1.8" fill="{ACC}"/>'
                f'<line x1="{x + 7}" y1="{y + 17}" x2="{x + 19}" y2="{y + 10}" {s}/>')
    if kind == "display":
        return (f'<rect x="{x + 1}" y="{y + 6}" width="26" height="16" rx="2" {s}/>'
                f'<line x1="{x + 6}" y1="{y + 12}" x2="{x + 20}" y2="{y + 12}" {s}/>'
                f'<line x1="{x + 6}" y1="{y + 17}" x2="{x + 15}" y2="{y + 17}" {s}/>')
    raise ValueError(kind)


def item(kind, label, x, y):
    return (f'<rect x="{x}" y="{y}" width="{ITEM_W}" height="{ITEM_H}" rx="6" fill="#FFFFFF" stroke="{RULE}" stroke-width="1.5"/>'
            + icon(kind, x + 10, y + 8)
            + f'<text x="{x + 48}" y="{y + 27.5}" font-size="15" fill="{INK}">{label}</text>')


def arrow(x1, y1, x2, y2):
    mx = (x1 + x2) / 2
    return (f'<path d="M{x1} {y1} C {mx} {y1}, {mx} {y2}, {x2 - 8} {y2}" fill="none" stroke="{ACC}" stroke-width="1.6"/>'
            f'<path d="M{x2 - 9} {y2 - 4.5} L{x2} {y2} L{x2 - 9} {y2 + 4.5} z" fill="{ACC}"/>')


def column(items, x, cy):
    gap = 14
    total = len(items) * ITEM_H + (len(items) - 1) * gap
    top = cy - total / 2
    return [(kind, label, x, top + i * (ITEM_H + gap)) for i, (kind, label) in enumerate(items)]


def diagram(title, inputs, outputs, aria, extra="", ports=None, pins=False):
    cy = H / 2 + 14
    by = cy - BOX_H / 2
    parts = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" fill="{PANEL}" stroke="{RULE}"/>',
             f'<text x="{LX}" y="34" font-size="12" letter-spacing="1.5" fill="{MUTED}">INPUT</text>',
             f'<text x="{RX + ITEM_W}" y="34" font-size="12" letter-spacing="1.5" fill="{MUTED}" text-anchor="end">OUTPUT</text>']
    left, right = column(inputs, LX, cy), column(outputs, RX, cy)
    n_in, n_out = len(left), len(right)
    PITCH, STUB = 12, 9
    def ys(n, step):
        return [cy + (i - (n - 1) / 2) * step for i in range(n)]
    # On the microcontroller, wires go to pins: every other pin along each edge is used.
    in_y = ys(n_in, PITCH * 2 if pins else 30)
    out_y = ys(n_out, PITCH * 2 if pins else 30)
    lx_end = BX - STUB if pins else BX
    rx_start = BX + BOX_W + STUB if pins else BX + BOX_W
    for (kind, label, x, y), ty in zip(left, in_y):
        parts.append(arrow(x + ITEM_W, y + ITEM_H / 2, lx_end, ty))
        parts.append(item(kind, label, x, y))
    for (kind, label, x, y), sy in zip(right, out_y):
        parts.append(arrow(rx_start, sy, x, y + ITEM_H / 2))
        parts.append(item(kind, label, x, y))
    parts.append(f'<rect x="{BX}" y="{by}" width="{BOX_W}" height="{BOX_H}" rx="10" fill="{WASH}" stroke="{ACC}" stroke-width="2"/>'
                 f'<text x="{W / 2}" y="{cy + 6}" text-anchor="middle" font-size="17" font-weight="600" fill="{ACC_DARK}">{title}</text>')
    if pins:
        for py in ys(5, PITCH):
            for px in (BX - STUB, BX + BOX_W):
                parts.append(f'<rect x="{px}" y="{py - 2.5}" width="{STUB}" height="5" fill="{MUTED}"/>')
        parts.append(f'<text x="{W / 2}" y="{by + BOX_H + 22}" text-anchor="middle" font-size="12" letter-spacing="1.5" fill="{MUTED}">PINS</text>')
    if ports:
        def pill(x, y, text, anchor):
            w = 8.5 * len(text) + 16
            rx = x - w if anchor == "end" else x
            return (f'<rect x="{rx}" y="{y - 9}" width="{w}" height="18" rx="9" fill="#FFFFFF" stroke="{ACC}" stroke-width="1"/>'
                    f'<text x="{rx + w / 2}" y="{y + 4}" text-anchor="middle" font-size="11" fill="{ACC_DARK}">{text}</text>')
        for text, ty in zip(ports[:n_in], in_y):
            parts.append(pill(BX - 4, ty, text, "end"))
        for text, sy in zip(ports[n_in:n_in + n_out], out_y):
            parts.append(pill(BX + BOX_W + 4, sy, text, "start"))
    parts.append(extra)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{aria}" font-family="{SANS}">\n' + "\n".join(parts) + "\n</svg>\n")


def cloud(cx, top):
    """The internet: a cloud above the box, with a two-way link down to it."""
    by = H / 2 + 14 - BOX_H / 2
    d = (f"M{cx - 36} {top + 34} a14 14 0 0 1 4 -27 a22 22 0 0 1 40 -6 "
         f"a17 17 0 0 1 30 11 a12 12 0 0 1 -2 22 z")
    return (f'<path d="{d}" fill="#FFFFFF" stroke="{RULE}" stroke-width="1.5"/>'
            f'<text x="{cx}" y="{top + 25}" text-anchor="middle" font-size="14" fill="{INK}">Internet</text>'
            f'<line x1="{cx}" y1="{top + 40}" x2="{cx}" y2="{by - 4}" stroke="{ACC}" stroke-width="1.6"/>'
            f'<path d="M{cx - 4.5} {top + 44} L{cx} {top + 35} L{cx + 4.5} {top + 44} z" fill="{ACC}"/>'
            f'<path d="M{cx - 4.5} {by - 9} L{cx} {by} L{cx + 4.5} {by - 9} z" fill="{ACC}"/>')


out = sys.argv[1]
with open(f"{out}/computer.svg", "w") as f:
    f.write(diagram(
        "Computer",
        [("keyboard", "Keyboard"), ("mouse", "Mouse")],
        [("monitor", "Monitor"), ("speaker", "Speakers")],
        "A computer takes input from a keyboard and a mouse, sends output to a monitor and speakers, and exchanges data with the internet.",
        extra=cloud(W / 2, 12)))
with open(f"{out}/microcontroller.svg", "w") as f:
    f.write(diagram(
        "Microcontroller",
        [("thermometer", "Temperature sensor"), ("light", "Light sensor"), ("button", "Push button")],
        [("led", "LED"), ("speaker", "Buzzer"), ("relay", "Relay")],
        "A microcontroller takes input from a temperature sensor, a light sensor and a push button, and sends output to an LED, a buzzer and a relay, through wires connected to its pins.", pins=True))
