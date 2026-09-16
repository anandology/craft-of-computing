"""SQLite store for the events sigma posts from student machines.

The tables and the reasoning behind them are in schema.sql. In short: events
is append-only and the preview reads the newest row per (name, owner).

The tail sigma sends is a notebook in its own right, so nothing here parses or
rewrites one. It is stored as it arrived and served as it was stored.
"""

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent

DB_PATH = os.environ.get("PREVIEW_DB", str(HERE / "data" / "events.db"))

SCHEMA_PATH = HERE / "schema.sql"


def connect():
    """Opens a connection with the pragmas every caller wants.

    A connection per request is cheap and keeps sqlite3's one-thread-per-
    connection rule out of the way. WAL lives in the database file, so setting
    it again here costs nothing; busy_timeout is per connection and does not.
    """
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA busy_timeout=5000")
    db.execute("PRAGMA synchronous=NORMAL")
    return db


def init():
    """Creates the tables if they are not there yet. Safe to call on every start."""
    with connect() as db:
        db.executescript(SCHEMA_PATH.read_text())


def add_event(payload):
    """Stores one event envelope and returns its row id."""
    data = payload.get("data") or {}
    path = data.get("path")
    received_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with connect() as db:
        cursor = db.execute(
            """INSERT INTO events
               (received_at, sent_at, event, training, owner, sigma_version,
                name, path, total_cells, payload)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                received_at,
                payload.get("sent_at"),
                payload.get("event"),
                payload.get("training"),
                owner_of(payload),
                payload.get("sigma_version"),
                notebook_name(path),
                path,
                data.get("total_cells"),
                json.dumps(payload),
            ),
        )
        return cursor.lastrowid


def owner_of(payload):
    """Who sent the event.

    username is the name craft.sh registered the student's ssh key under, and
    is the name to show. It is absent until that has happened, and the unix
    user is the next best thing.
    """
    return payload.get("username") or payload.get("user") or "unknown"


def notebook_name(path):
    """The collection name for a notebook path: the filename without .ipynb.

    Subdirectories are ignored for now, so two notebooks with the same name in
    different directories land in the same collection.
    """
    if not path:
        return None
    return Path(path).stem


def get_collections():
    """Every notebook name seen, most recently active first."""
    with connect() as db:
        rows = db.execute(
            """SELECT name,
                      COUNT(DISTINCT owner) AS size,
                      MAX(received_at) AS updated_at
               FROM events
               WHERE event = 'notebook.saved' AND name IS NOT NULL
               GROUP BY name
               ORDER BY updated_at DESC"""
        ).fetchall()
    return [dict(row) for row in rows]


def get_collection(name):
    """The newest state of each student's copy of a notebook.

    Returns None when nobody has saved a notebook by that name, which is what
    tells the route to 404.
    """
    with connect() as db:
        rows = db.execute(
            """SELECT owner, path, total_cells, received_at AS updated_at
               FROM events
               WHERE id IN (SELECT MAX(id) FROM events
                            WHERE event = 'notebook.saved' AND name = ?
                            GROUP BY owner)
               ORDER BY owner""",
            (name,),
        ).fetchall()

    if not rows:
        return None
    return {"name": name, "notebooks": [dict(row) for row in rows]}


def get_tail(name, owner):
    """The last tail this student saved of this notebook, ready to render."""
    with connect() as db:
        row = db.execute(
            """SELECT payload FROM events
               WHERE event = 'notebook.saved' AND name = ? AND owner = ?
               ORDER BY id DESC LIMIT 1""",
            (name, owner),
        ).fetchone()

    if row is None:
        return None
    return json.loads(row["payload"]).get("data", {}).get("tail")
