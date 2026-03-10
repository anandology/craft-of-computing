"""live-sketch - a web server that displays sketches that update in real time."""

import queue
import sys
import time
from flask import Flask, request, Response

app = Flask(__name__)

# In-memory storage: {"sketch_id": (svg_string, timestamp)}
sketches = {}

# SSE listeners: {"sketch_id": [queue, queue, ...]}
listeners = {}

PAGE_HTML = """\
<!DOCTYPE html>
<html>
<head>
  <title>{sketch_id} - live sketch</title>
  <style>
    body {{
      font-family: monospace;
      margin: 40px auto;
      max-width: 480px;
      text-align: center;
    }}
    #info {{
      color: #888;
      margin-bottom: 12px;
    }}
    #drawing {{
      border: 1px solid #ccc;
    }}
    #empty {{
      color: #aaa;
      padding: 40px;
    }}
  </style>
</head>
<body>
  <div id="info">last modified: <span id="ago">never</span></div>
  <div id="drawing">
    <div id="empty">no sketch yet</div>
  </div>
  <script>
    var lastUpdate = null;

    function timeAgo(seconds) {{
      if (seconds < 5)  return "just now";
      if (seconds < 60) return Math.floor(seconds) + " seconds ago";
      if (seconds < 120) return "1 minute ago";
      if (seconds < 3600) return Math.floor(seconds / 60) + " minutes ago";
      if (seconds < 7200) return "1 hour ago";
      return Math.floor(seconds / 3600) + " hours ago";
    }}

    function updateAgo() {{
      if (lastUpdate) {{
        var seconds = (Date.now() - lastUpdate) / 1000;
        document.getElementById("ago").textContent = timeAgo(seconds);
      }}
    }}

    var source = new EventSource("/{sketch_id}/events");
    source.onmessage = function(event) {{
      document.getElementById("drawing").innerHTML = event.data;
      lastUpdate = Date.now();
      updateAgo();
    }};

    setInterval(updateAgo, 1000);
  </script>
</body>
</html>
"""


def notify_listeners(sketch_id, svg):
    """Push SVG to all clients listening on this sketch."""
    for q in listeners.get(sketch_id, []):
        q.put(svg)


@app.route("/<sketch_id>")
def view(sketch_id):
    """Show the HTML page for a sketch."""
    html = PAGE_HTML.format(sketch_id=sketch_id)
    return Response(html, content_type="text/html")


@app.route("/<sketch_id>/events")
def events(sketch_id):
    """SSE stream for live updates."""
    q = queue.Queue()

    # Register this client
    if sketch_id not in listeners:
        listeners[sketch_id] = []
    listeners[sketch_id].append(q)

    # Send the current SVG immediately if it exists
    if sketch_id in sketches:
        svg, _ = sketches[sketch_id]
        q.put(svg)

    def stream():
        try:
            while True:
                svg = q.get()
                # SSE format: each line prefixed with "data: ", blank line to end
                lines = svg.replace("\n", "\ndata: ")
                yield f"data: {lines}\n\n"
        finally:
            listeners[sketch_id].remove(q)

    return Response(stream(), content_type="text/event-stream")


@app.route("/<sketch_id>.svg", methods=["GET"])
def get_svg(sketch_id):
    """Return the current SVG."""
    if sketch_id not in sketches:
        return Response("not found\n", status=404)

    svg, _ = sketches[sketch_id]
    return Response(svg, content_type="image/svg+xml")


@app.route("/<sketch_id>.svg", methods=["PUT"])
def put_svg(sketch_id):
    """Upload or replace an SVG and notify all listeners."""
    svg = request.get_data(as_text=True)
    if not svg.strip():
        return Response("empty body\n", status=400)

    sketches[sketch_id] = (svg, time.time())
    notify_listeners(sketch_id, svg)
    return Response("ok\n", status=200)


def main():
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"live-sketch: port must be a number, got '{sys.argv[1]}'", file=sys.stderr)
            sys.exit(1)

    print(f"live-sketch: serving on http://localhost:{port}")
    app.run(host="127.0.0.1", port=port, threaded=True)


if __name__ == "__main__":
    main()
