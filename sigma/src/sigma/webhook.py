"""Sends sigma's events to a webhook.

Every event is posted to config.webhook_url, wrapped in an envelope that says
who sent it and when. See README.md for the events and their data.
"""

import datetime
import hashlib
import json
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import requests

from . import config
from .ipytail import IPyTail

# craft.sh setup-ssh writes "username public-key" here once the key is registered.
CRAFT_REGISTERED = Path.home() / ".ssh" / "craft-registered"

# Hash of the last tail sent for each notebook path.
_last_tails = {}


def trigger(event, data):
    """Sends an event with its data to the webhook. Does nothing when no URL is configured."""
    if not config.webhook_url:
        return

    payload = {
        "event": event,
        "training": config.training_name,
        "username": _get_username(),
        "user": os.getenv("USER"),
        "sent_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sigma_version": _get_sigma_version(),
        "data": data,
    }
    try:
        requests.post(config.webhook_url, json=payload, timeout=3)
    except requests.RequestException:
        pass


def notebook_saved(os_path, path):
    """Sends the notebook.saved event with the last cells of the notebook.

    os_path is where the notebook is on disk, and path is the name sent with
    the event. Nothing is sent when the tail hasn't changed since the last save.
    """
    if not config.webhook_url:
        return

    ipytail = IPyTail()
    notebook = ipytail.read_notebook(os_path)
    tail = ipytail.process_notebook(notebook)

    digest = hashlib.sha256(json.dumps(tail, sort_keys=True).encode()).hexdigest()
    if _last_tails.get(path) == digest:
        return
    _last_tails[path] = digest

    trigger("notebook.saved", {
        "path": path,
        "total_cells": len(notebook["cells"]),
        "tail": tail,
    })


def _get_username():
    try:
        return CRAFT_REGISTERED.read_text().split()[0]
    except (OSError, IndexError):
        return None


def _get_sigma_version():
    try:
        return version("sigma")
    except PackageNotFoundError:
        return None
