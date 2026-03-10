"""live-sketch - a web server that displays sketches that update in real time."""

import calendar
import sys
import time
from flask import Flask, request, Response

app = Flask(__name__)

# In-memory storage: {"sketch_id": (svg_string, timestamp)}
sketches = {}

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
    var lastModified = null;

    function timeAgo(seconds) {{
      if (seconds < 5)  return "just now";
      if (seconds < 60) return Math.floor(seconds) + " seconds ago";
      if (seconds < 120) return "1 minute ago";
      if (seconds < 3600) return Math.floor(seconds / 60) + " minutes ago";
      if (seconds < 7200) return "1 hour ago";
      return Math.floor(seconds / 3600) + " hours ago";
    }}

    function poll() {{
      var headers = {{}};
      if (lastModified) {{
        headers["If-Modified-Since"] = lastModified;
      }}
      fetch("/{sketch_id}.svg", {{ headers: headers }})
        .then(function(response) {{
          if (response.status === 200) {{
            lastModified = response.headers.get("Last-Modified");
            return response.text();
          }}
          return null;
        }})
        .then(function(svg) {{
          if (svg !== null) {{
            document.getElementById("drawing").innerHTML = svg;
          }}
        }});
    }}

    function updateAgo() {{
      if (lastModified) {{
        var then = new Date(lastModified).getTime();
        var seconds = (Date.now() - then) / 1000;
        document.getElementById("ago").textContent = timeAgo(seconds);
      }}
    }}

    setInterval(poll, 1000);
    setInterval(updateAgo, 1000);
    poll();
  </script>
</body>
</html>
"""


@app.route("/<sketch_id>")
def view(sketch_id):
    """Show the HTML page for a sketch."""
    html = PAGE_HTML.format(sketch_id=sketch_id)
    return Response(html, content_type="text/html")


@app.route("/<sketch_id>.svg", methods=["GET"])
def get_svg(sketch_id):
    """Return the SVG, supporting If-Modified-Since."""
    if sketch_id not in sketches:
        return Response("not found\n", status=404)

    svg, modified = sketches[sketch_id]
    last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(modified))

    # Check If-Modified-Since
    ims = request.headers.get("If-Modified-Since")
    if ims:
        ims_time = calendar.timegm(time.strptime(ims, "%a, %d %b %Y %H:%M:%S GMT"))
        if modified <= ims_time:
            return Response(status=304, headers={"Last-Modified": last_modified})

    return Response(
        svg,
        content_type="image/svg+xml",
        headers={"Last-Modified": last_modified},
    )


@app.route("/<sketch_id>.svg", methods=["PUT"])
def put_svg(sketch_id):
    """Upload or replace an SVG."""
    svg = request.get_data(as_text=True)
    if not svg.strip():
        return Response("empty body\n", status=400)

    sketches[sketch_id] = (svg, int(time.time()))
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
    app.run(host="127.0.0.1", port=port)


if __name__ == "__main__":
    main()
