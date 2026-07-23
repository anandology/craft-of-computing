# Sketch

Sketch is a simple tool for generating images using shell commands.

## Quick Start

```bash
sketch circle 200 200 80 --stroke red --fill blue > drawing.sk
sketch render drawing.sk > drawing.svg
```

## Commands

### line

Draw a line between two points.

```bash
sketch line 10 20 200 150
sketch line 10 20 200 150 --stroke red --stroke-width 3
```

### circle

Draw a circle with a center point and radius.

```bash
sketch circle 200 200 50
sketch circle 200 200 50 --stroke red --fill blue
```

### rectangle

Draw a rectangle from a top-left corner with a given width and height.

```bash
sketch rectangle 50 50 100 80
sketch rectangle 50 50 100 80 --fill yellow --stroke black
```

### render

Render a `.sk` file to SVG. Reads from stdin if no file is given.

```bash
sketch render drawing.sk
cat drawing.sk | sketch render
```

### live

Render and push to a live-sketch server. Reads from stdin if no file is given.

```bash
export SKETCH_LIVE_URL=http://localhost:8080/demo
sketch live drawing.sk
cat drawing.sk | sketch live
```

## Style Options

All shape commands accept the following options:

| Option | Environment Variable | Default | Description |
|---|---|---|---|
| `--stroke` | `SKETCH_STROKE` | `black` | Outline color |
| `--fill` | `SKETCH_FILL` | `none` | Fill color |
| `--stroke-width` | `SKETCH_STROKE_WIDTH` | `1` | Stroke width |

Options override environment variables. Environment variables override defaults.

```bash
# Using options
sketch circle 200 200 50 --stroke red --fill blue

# Using environment variables
export SKETCH_STROKE=red
sketch circle 200 200 50

# Options override environment variables
SKETCH_STROKE=green sketch circle 200 200 50 --stroke red
# stroke will be red
```

## The .sk File Format

A `.sk` file is plain text. Each line is one drawing command with `key=value` attributes.

```
circle cx=200 cy=200 radius=80 stroke=red fill=blue
line x1=10 y1=20 x2=200 y2=150 stroke=black stroke-width=3
rectangle x=50 y=50 width=100 height=80 stroke=black fill=none
```

### Design

Every line is self-contained. A line carries its command, its coordinates, and its style. There is no state that carries over from one line to the next.

This means:

- **Any line can be understood on its own.** You never need to look elsewhere in the file to know what a line does.
- **`grep` works.** `grep circle drawing.sk` gives you all circles, complete with their colors and positions.
- **`head` and `tail` work.** The first 5 lines are a valid drawing. The last 3 lines are a valid drawing. No missing context.
- **`tac` works.** Reverse the file and you get the same shapes in reverse draw order. Still valid.
- **`cat` is composition.** `cat a.sk b.sk > c.sk` combines two drawings. No style bleeds from one file to the other.

Lines starting with `#` are comments. Blank lines are ignored.

```
# A simple scene
circle cx=200 cy=200 radius=80 stroke=red fill=blue

# A border
rectangle x=0 y=0 width=400 height=400 stroke=black fill=none
```

The canvas is 400x400 pixels. The top-left corner is (0, 0).

## Live Sketch

`live-sketch` is a web server that displays sketches in real time.

```bash
# Start the server
live-sketch

# Push a sketch (browser updates instantly)
export SKETCH_LIVE_URL=http://localhost:8080/demo
sketch live drawing.sk
```

The browser page connects via server-sent events. Every time you push a new sketch, the image updates immediately -- no refresh needed.

### Animation

Because updates are instant, you can animate:

```bash
export SKETCH_LIVE_URL=http://localhost:8080/demo
for x in $(seq 10 10 400); do
    sketch circle $x 200 50 --fill blue | sketch live
    sleep 0.1
done
```
