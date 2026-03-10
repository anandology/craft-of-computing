"""sketch - generate simple images using shell commands."""

import os
import sys
import urllib.request

import click


CANVAS_W = 400
CANVAS_H = 400


@click.group()
def sketch():
    """Generate simple images using shell commands."""
    pass


@sketch.command()
@click.argument("x1", type=float)
@click.argument("y1", type=float)
@click.argument("x2", type=float)
@click.argument("y2", type=float)
def line(x1, y1, x2, y2):
    """Draw a line from (x1, y1) to (x2, y2)."""
    click.echo(f"line {x1:g} {y1:g} {x2:g} {y2:g}")


@sketch.command()
@click.argument("cx", type=float)
@click.argument("cy", type=float)
@click.argument("radius", type=float)
def circle(cx, cy, radius):
    """Draw a circle with center at (cx, cy) and the given radius."""
    if radius <= 0:
        raise click.BadParameter("must be positive", param_hint="'radius'")
    click.echo(f"circle {cx:g} {cy:g} {radius:g}")


@sketch.command()
@click.argument("x", type=float)
@click.argument("y", type=float)
@click.argument("width", type=float)
@click.argument("height", type=float)
def rectangle(x, y, width, height):
    """Draw a rectangle with its top-left corner at (x, y)."""
    if width <= 0:
        raise click.BadParameter("must be positive", param_hint="'width'")
    if height <= 0:
        raise click.BadParameter("must be positive", param_hint="'height'")
    click.echo(f"rectangle {x:g} {y:g} {width:g} {height:g}")


@sketch.command()
@click.argument("color")
def stroke(color):
    """Set the outline color for subsequent shapes."""
    click.echo(f"stroke {color}")


@sketch.command()
@click.argument("color")
def fill(color):
    """Set the fill color for subsequent shapes."""
    click.echo(f"fill {color}")


# --- Rendering ---

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


def render_sk(lines):
    """Parse .sk lines and return SVG string."""
    current_stroke = "black"
    current_fill = "none"
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
                click.echo(f"render: line {lineno}: stroke expects 1 argument, skipping", err=True)
                continue
            current_stroke = rest[0]
        elif cmd == "fill":
            if len(rest) != 1:
                click.echo(f"render: line {lineno}: fill expects 1 argument, skipping", err=True)
                continue
            current_fill = rest[0]
        elif cmd in SHAPE_RENDERERS:
            expected, renderer = SHAPE_RENDERERS[cmd]
            if len(rest) != expected:
                click.echo(f"render: line {lineno}: {cmd} expects {expected} arguments, skipping", err=True)
                continue
            try:
                parts = [float(v) for v in rest]
            except ValueError:
                click.echo(f"render: line {lineno}: {cmd} has non-numeric arguments, skipping", err=True)
                continue
            elements.append(renderer(parts, current_stroke, current_fill))
        else:
            click.echo(f"render: line {lineno}: unknown command '{cmd}', skipping", err=True)

    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W} {CANVAS_H}">\n'
    for el in elements:
        svg += el + "\n"
    svg += "</svg>"
    return svg


def read_sk(file):
    """Read .sk content from a file path or stdin."""
    if file:
        return open(file).readlines()
    return sys.stdin.readlines()


@sketch.command()
@click.argument("file", required=False, type=click.Path(exists=True))
def render(file):
    """Render a .sk file to SVG. Reads from stdin if no file is given."""
    lines = read_sk(file)
    click.echo(render_sk(lines))


@sketch.command()
@click.argument("file", required=False, type=click.Path(exists=True))
def live(file):
    """Render and push to a live-sketch server.

    Reads from stdin if no file is given.

    The server URL is read from the SKETCH_LIVE_URL environment variable:

        export SKETCH_LIVE_URL=http://localhost:8080/demo
    """
    url = os.environ.get("SKETCH_LIVE_URL")
    if not url:
        raise click.UsageError(
            "SKETCH_LIVE_URL is not set\n\n"
            "Set it to the URL of your live-sketch page:\n\n"
            "  export SKETCH_LIVE_URL=http://localhost:8080/demo"
        )

    lines = read_sk(file)
    svg = render_sk(lines)

    svg_url = url.rstrip("/") + ".svg"
    req = urllib.request.Request(svg_url, data=svg.encode(), method="PUT")
    try:
        urllib.request.urlopen(req)
        click.echo(f"pushed to {url}")
    except urllib.error.URLError as e:
        raise click.ClickException(f"could not reach {svg_url}: {e.reason}")


def main():
    sketch()


if __name__ == "__main__":
    main()
