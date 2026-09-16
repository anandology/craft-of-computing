"""Receives sigma's events and previews the notebooks they carry.

Students run sigma, which posts a notebook.saved event every time a notebook
changes on disk (see sigma/src/sigma/webhook.py). This stores every event and
serves a page per notebook name showing everyone's copy side by side.

It is a blueprint so it can later be folded into app/app.py the way quiz_app
already is, but it runs on its own port today: the quiz app is live during
class and restarting it should not interrupt capturing notebooks.

    python preview/app.py                     # development, port 8082
    cd preview && gunicorn -b 127.0.0.1:8082 app:app
"""

from flask import Blueprint, Flask, abort, jsonify, redirect, render_template, request, url_for

import store

bp = Blueprint(
    "preview",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static",
)


@bp.app_template_filter("clock")
def clock(timestamp):
    """Turns 2026-09-16T10:23:45Z into 10:23, which is all a live page needs."""
    if not timestamp or "T" not in timestamp:
        return timestamp or ""
    return timestamp.split("T", 1)[1][:5]


@bp.get("/")
def index():
    return redirect(url_for("preview.preview_index"))


@bp.get("/health")
def health():
    return jsonify(ok=True)


@bp.post("/webhook")
def webhook():
    """The endpoint sigma's SIGMA_WEBHOOK_URL points at.

    sigma gives up after 3 seconds and ignores whatever comes back, so this
    stores the event and returns rather than doing any work on it.
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="expected a JSON object"), 400
    if not payload.get("event"):
        return jsonify(error="missing event"), 400

    store.add_event(payload)
    return jsonify(ok=True), 201


@bp.get("/preview")
def preview_index():
    return render_template("preview/index.html", collections=store.get_collections())


@bp.get("/preview/<name>")
def preview_collection(name):
    collection = store.get_collection(name)
    if not collection:
        abort(404)
    return render_template("preview/collection.html", collection=collection)


@bp.get("/preview/_tail/<owner>/<name>.ipynb")
def preview_tail(owner, name):
    """The newest tail as a notebook, for the browser to render.

    What sigma sends is already trimmed to the last cells with their outputs
    clamped, and it keeps the notebook's top level intact, so it goes out as
    it came in.
    """
    tail = store.get_tail(name, owner)
    if tail is None:
        abort(404)
    return jsonify(tail)


def create_app():
    # static_folder=None because the blueprint serves /static; leaving Flask's
    # own static route in place would collide with it.
    app = Flask(__name__, static_folder=None)
    store.init()
    app.register_blueprint(bp)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8082, debug=True)
