"""Glyph C6 photo with headers (PCBCupid, via Lion Circuits), main parts labelled.

Usage:
    curl -sL -o hdr.png https://www.lioncircuits.com/pcbcupid-C6-Header.png
    convert hdr.png -crop 970x622+30+200 +repage -resize 1170x750 -strip -quality 85 hcrop.jpg
    python3 scripts/draw_photo.py hcrop.jpg website/microcontrollers/introduction/images/glyph-c6.svg

The photo is PCBCupid's, served by Lion Circuits (1024px wide); the label
coordinates below are in its pixels.
"""
import base64, sys
INK, ACC = "#1A1916", "#3C5A8A"
SANS = "'IBM Plex Sans', system-ui, sans-serif"
CX, CY, CW = 30, 200, 970            # crop of the 1024px original
W, H = 780, 500
K = W / CW
img = base64.b64encode(open(sys.argv[1], "rb").read()).decode()
def P(x, y):
    return round((x - CX) * K, 1), round((y - CY) * K, 1)
def lead(a, b):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ACC}" stroke-width="1.6"/>'
            f'<circle cx="{x2}" cy="{y2}" r="4" fill="#FFFFFF" stroke="{ACC}" stroke-width="2"/>')
def text(xy, s, anchor="middle"):
    x, y = P(*xy)
    return f'<text x="{x}" y="{y}" font-size="17" fill="{INK}" text-anchor="{anchor}">{s}</text>'
p = [f'<image href="data:image/jpeg;base64,{img}" x="0" y="0" width="{W}" height="{H}"/>']
p += [lead((880, 250), (740, 385)), text((880, 238), "Module")]
p += [lead((330, 250), (425, 535)), text((330, 238), "RESET button")]
p += [lead((600, 250), (520, 503)), text((600, 238), "BOOT button")]
p += [lead((120, 765), (165, 585)), text((120, 790), "USB-C")]
p += [lead((900, 735), (885, 590)), lead((900, 735), (812, 625)), text((900, 760), "Header pins")]
aria = ("Photo of the Glyph C6 board with header pins fitted, labelled: the module, the RESET and BOOT buttons, "
        "the USB-C connector, and a row of header pins along each long edge.")
open(sys.argv[2], "w").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="{aria}" font-family="{SANS}">\n' + "\n".join(p) + "\n</svg>\n")
