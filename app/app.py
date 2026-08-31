"""API for the Craft of Computing course.

Currently supports collecting ssh public keys from students. Each key is stored
as a file named after the student's email, so the whole directory can be fed
straight into an authorized_keys file.
"""

import base64
import datetime
import os
import re
import struct
from functools import wraps

from flask import Flask, jsonify, request

# Hardcoded for now. Move to an environment variable before this handles
# anything more sensitive than ssh public keys.
API_TOKEN = "craft-2026-8f3a91c47d5e"

KEYS_DIR = os.environ.get(
    "CRAFT_KEYS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "ssh-keys")
)

# Deliberately strict: the email becomes a filename, so no slashes get through,
# and a leading dot is refused so every key file is visible to a shell glob.
EMAIL_RE = re.compile(r"^[a-z0-9][a-z0-9._%+-]*@[a-z0-9-]+(\.[a-z0-9-]+)+$")

app = Flask(__name__)


def require_token(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        prefix = "Bearer "
        token = auth[len(prefix):] if auth.startswith(prefix) else ""
        if token != API_TOKEN:
            return jsonify(error="unauthorized"), 401
        return f(*args, **kwargs)

    return wrapper


def check_ssh_key(key):
    """Return an error message if key is not a valid ssh public key."""
    parts = key.split()
    if len(parts) < 2:
        return "not an ssh public key: expected '<type> <base64-blob> [comment]'"

    keytype, blob = parts[0], parts[1]
    try:
        data = base64.b64decode(blob, validate=True)
    except Exception:
        return "the key data is not valid base64"

    # An ssh public key blob starts with its own type as a length-prefixed string.
    if len(data) < 4:
        return "the key data is too short to be an ssh public key"
    (n,) = struct.unpack(">I", data[:4])
    if n > len(data) - 4 or data[4:4 + n].decode("utf-8", "replace") != keytype:
        return f"the key data does not match the declared type {keytype!r}"

    return None


def key_path(email):
    return os.path.join(KEYS_DIR, email + ".key")


def read_key(email):
    path = key_path(email)
    mtime = datetime.datetime.fromtimestamp(
        os.path.getmtime(path), datetime.timezone.utc
    )
    return {
        "email": email,
        "ssh_key": open(path).read().strip(),
        "updated_at": mtime.strftime("%Y-%m-%d %H:%M:%S"),
    }


@app.get("/api/health")
def health():
    return jsonify(ok=True)


@app.post("/api/keys")
@require_token
def add_key():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="expected a JSON object"), 400

    email = (payload.get("email") or "").strip().lower()
    ssh_key = " ".join((payload.get("ssh_key") or "").split())

    if not EMAIL_RE.match(email):
        return jsonify(error=f"invalid email: {email!r}"), 400

    error = check_ssh_key(ssh_key)
    if error:
        return jsonify(error=error), 400

    os.makedirs(KEYS_DIR, exist_ok=True)
    path = key_path(email)
    status = 200 if os.path.exists(path) else 201

    # Write to a temporary file and rename, so a reader never sees a half-written key.
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(ssh_key + "\n")
    os.replace(tmp, path)

    return jsonify(read_key(email)), status


@app.get("/api/keys")
@require_token
def list_keys():
    names = []
    if os.path.isdir(KEYS_DIR):
        names = [f[:-len(".key")] for f in os.listdir(KEYS_DIR) if f.endswith(".key")]

    names.sort(key=lambda email: os.path.getmtime(key_path(email)), reverse=True)
    items = [read_key(email) for email in names]
    return jsonify(count=len(items), items=items)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)
