#!/usr/bin/env python3
"""sketch - generate simple images using shell commands."""

import sys


USAGE = """\
Usage: sketch command [args...]

Commands:
  line x1 y1 x2 y2       Draw a line
  circle cx cy r          Draw a circle
  rectangle x y w h       Draw a rectangle
  stroke color            Set stroke color
  fill color              Set fill color
  render [file]           Render .sk to SVG (reads stdin if no file)

Run sketch command --help for details on a specific command."""

CANVAS_W = 400
CANVAS_H = 400

HELP = {
    "line": """\
USAGE
  sketch line x1 y1 x2 y2

  Draw a line from point (x1, y1) to point (x2, y2).

ARGUMENTS
  x1  X coordinate of the start point
  y1  Y coordinate of the start point
  x2  X coordinate of the end point
  y2  Y coordinate of the end point

EXAMPLE
  sketch line 10 20 200 150""",

    "circle": """\
USAGE
  sketch circle cx cy radius

  Draw a circle with center at (cx, cy) and the given radius.

ARGUMENTS
  cx      X coordinate of the center
  cy      Y coordinate of the center
  radius  Radius of the circle (must be positive)

EXAMPLE
  sketch circle 200 200 50""",

    "rectangle": """\
USAGE
  sketch rectangle x y width height

  Draw a rectangle with its top-left corner at (x, y).

ARGUMENTS
  x       X coordinate of the top-left corner
  y       Y coordinate of the top-left corner
  width   Width of the rectangle (must be positive)
  height  Height of the rectangle (must be positive)

EXAMPLE
  sketch rectangle 50 50 100 80""",

    "stroke": """\
USAGE
  sketch stroke color

  Set the outline color for shapes drawn after this command.

ARGUMENTS
  color  A color name (red, blue, green, ...) or hex (#ff0000)

EXAMPLE
  sketch stroke red""",

    "fill": """\
USAGE
  sketch fill color

  Set the fill color for shapes drawn after this command.

ARGUMENTS
  color  A color name (red, blue, green, ...) or hex (#ff0000)

EXAMPLE
  sketch fill blue""",

    "render": """\
USAGE
  sketch render [file]

  Render a .sk file to SVG. If no file is given, reads from stdin.

ARGUMENTS
  file  Path to a .sk file (optional)

EXAMPLE
  sketch render drawing.sk
  cat drawing.sk | sketch render""",
}


def error(msg):
    print(f"sketch: {msg}", file=sys.stderr)
    sys.exit(1)


def parse_floats(args, count, label):
    if len(args) != count:
        error(f"{label}: expected {count} arguments, got {len(args)}\n\n{HELP[label]}")
    values = []
    for i, a in enumerate(args):
        try:
            values.append(float(a))
        except ValueError:
            error(f"{label}: argument {i+1} must be a number, got '{a}'\n\n{HELP[label]}")
    return values


def cmd_line(args):
    x1, y1, x2, y2 = parse_floats(args, 4, "line")
    print(f"line {x1:g} {y1:g} {x2:g} {y2:g}")


def cmd_circle(args):
    cx, cy, r = parse_floats(args, 3, "circle")
    if r <= 0:
        error(f"circle: radius must be positive\n\n{HELP['circle']}")
    print(f"circle {cx:g} {cy:g} {r:g}")


def cmd_rectangle(args):
    x, y, w, h = parse_floats(args, 4, "rectangle")
    if w <= 0:
        error(f"rectangle: width must be positive\n\n{HELP['rectangle']}")
    if h <= 0:
        error(f"rectangle: height must be positive\n\n{HELP['rectangle']}")
    print(f"rectangle {x:g} {y:g} {w:g} {h:g}")


def cmd_stroke(args):
    if len(args) != 1:
        error(f"stroke: expected 1 argument, got {len(args)}\n\n{HELP['stroke']}")
    if not args[0]:
        error(f"stroke: color must not be empty\n\n{HELP['stroke']}")
    print(f"stroke {args[0]}")


def cmd_fill(args):
    if len(args) != 1:
        error(f"fill: expected 1 argument, got {len(args)}\n\n{HELP['fill']}")
    if not args[0]:
        error(f"fill: color must not be empty\n\n{HELP['fill']}")
    print(f"fill {args[0]}")


def render_line(parts, stroke, fill):
    x1, y1, x2, y2 = parts
    return f'  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" />'


def render_circle(parts, stroke, fill):
    cx, cy, r = parts
    return f'  <circle cx="{cx}" cy="{cy}" r="{r}" stroke="{stroke}" fill="{fill}" />'


def render_rectangle(parts, stroke, fill):
    x, y, w, h = parts
    return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="{stroke}" fill="{fill}" />'


SHAPE_RENDERERS = {
    "line": (4, render_line),
    "circle": (3, render_circle),
    "rectangle": (4, render_rectangle),
}

RENDER_HELP = {
    "line": "line x1 y1 x2 y2          e.g. line 10 20 200 150",
    "circle": "circle cx cy radius        e.g. circle 200 200 50",
    "rectangle": "rectangle x y width height  e.g. rectangle 50 50 100 80",
    "stroke": "stroke color               e.g. stroke red",
    "fill": "fill color                 e.g. fill blue",
}


def cmd_render(args):
    if len(args) > 1:
        error(f"render: expected 0 or 1 arguments, got {len(args)}\n\n{HELP['render']}")

    if len(args) == 1:
        try:
            with open(args[0]) as f:
                lines = f.readlines()
        except FileNotFoundError:
            error(f"render: file not found: {args[0]}")
        except IsADirectoryError:
            error(f"render: is a directory: {args[0]}")
    else:
        lines = sys.stdin.readlines()

    stroke = "black"
    fill = "none"
    elements = []

    for lineno, raw in enumerate(lines, 1):
        raw = raw.strip()
        if not raw or raw.startswith("#"):
            continue

        tokens = raw.split()
        cmd = tokens[0]
        rest = tokens[1:]

        if cmd == "stroke":
            if len(rest) != 1:
                print(f"sketch: render: line {lineno}: stroke expects 1 argument, skipping\n  usage: {RENDER_HELP['stroke']}", file=sys.stderr)
                continue
            stroke = rest[0]
        elif cmd == "fill":
            if len(rest) != 1:
                print(f"sketch: render: line {lineno}: fill expects 1 argument, skipping\n  usage: {RENDER_HELP['fill']}", file=sys.stderr)
                continue
            fill = rest[0]
        elif cmd in SHAPE_RENDERERS:
            expected, renderer = SHAPE_RENDERERS[cmd]
            if len(rest) != expected:
                print(f"sketch: render: line {lineno}: {cmd} expects {expected} arguments, skipping\n  usage: {RENDER_HELP[cmd]}", file=sys.stderr)
                continue
            try:
                parts = [float(v) for v in rest]
            except ValueError:
                print(f"sketch: render: line {lineno}: {cmd} has non-numeric arguments, skipping\n  usage: {RENDER_HELP[cmd]}", file=sys.stderr)
                continue
            elements.append(renderer(parts, stroke, fill))
        else:
            print(f"sketch: render: line {lineno}: unknown command '{cmd}', skipping", file=sys.stderr)

    print(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}">')
    for el in elements:
        print(el)
    print("</svg>")


COMMANDS = {
    "line": cmd_line,
    "circle": cmd_circle,
    "rectangle": cmd_rectangle,
    "stroke": cmd_stroke,
    "fill": cmd_fill,
    "render": cmd_render,
}


def main():
    if len(sys.argv) < 2:
        error(USAGE)

    cmd = sys.argv[1]
    if cmd in ("-h", "--help"):
        print(USAGE)
        sys.exit(0)

    if cmd not in COMMANDS:
        error(f"unknown command '{cmd}'\n\n{USAGE}")

    args = sys.argv[2:]
    if args and args[0] in ("-h", "--help"):
        print(HELP[cmd])
        sys.exit(0)

    COMMANDS[cmd](args)


if __name__ == "__main__":
    main()
