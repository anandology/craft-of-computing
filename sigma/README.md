# Sigma

System for loading and verifying problems in a jupyter notebook.

## How to use

To make sigma work,  write a setup script that creates  a file: 

    ~/.ipython/profile_default/startup/startup.py

with content:

```python
from sigma import magic
magic.register()
```

To send an event every time a notebook is saved, add this to
`~/.jupyter/jupyter_server_config.py`:

```python
from sigma import webhook

def post_save(model, os_path, contents_manager, **kwargs):
    if model["type"] != "notebook":
        return
    webhook.notebook_saved(os_path, model["path"])

c.FileContentsManager.post_save_hook = post_save
```

## Config

Sigma is configured with environment variables, read in `src/sigma/config.py`.

| Variable | Default | What it does |
|---|---|---|
| `SIGMA_PROBLEM_ROOT` | `~/craft/problems` | Where `%load_problem` and `%verify_problem` look for problems. |
| `SIGMA_WEBHOOK_URL` | empty | Where events are posted. No events are sent when empty. |
| `SIGMA_TRAINING_NAME` | `craft-of-computing` | Sent with every event, so one webhook can serve several trainings. |
| `SIGMA_HOME_PATH` | `/home` | Not used yet. |
| `SIGMA_TRAINING_DATA_DIR` | `training-data` | Not used yet. |

## Events

Every event is posted as JSON to `SIGMA_WEBHOOK_URL`, wrapped in the same
envelope:

```
POST $SIGMA_WEBHOOK_URL
Content-Type: application/json

{
  "event": "problem.verified",
  "training": "craft-of-computing",
  "username": "firstname-lastname",
  "user": "anand",
  "sent_at": "2026-09-16T10:12:03Z",
  "sigma_version": "0.1.0",
  "data": {...}
}
```

| Field | Value |
|---|---|
| `event` | Name of the event, see below |
| `training` | `SIGMA_TRAINING_NAME` |
| `username` | Login name on the course server, from `~/.ssh/craft-registered`, which `craft.sh setup-ssh` writes. `null` if the student hasn't run it. |
| `user` | `$USER` on the student's machine |
| `sent_at` | When the event was sent, in UTC |
| `sigma_version` | Version of sigma that sent it |
| `data` | Depends on the event |

There is no authentication. Requests have a 3 second timeout, the response is
ignored and failures are silently dropped, so the student never sees an error
from the server. The request is sent while the notebook is being saved or the
problem verified, so a slow server makes those slow.

The server should accept an event it doesn't know with a 2xx, so a newer sigma
keeps working with an older server.

### problem.verified

Sent when `%verify_problem NAME` runs, after the checks finish.

```json
{
  "problem": "square",
  "notebook": "python/square.ipynb",
  "status": "pass",
  "output": "🎉 Congratulations! You have successfully solved problem square!!"
}
```

| Field | Value |
|---|---|
| `problem` | Name of the problem |
| `notebook` | Path of the notebook, relative to where JupyterLab was started. `null` when it can't be found. |
| `status` | One of the statuses below |
| `output` | The messages shown to the student, one per line |

| Status | When |
|---|---|
| `pass` | Every check passed. |
| `fail` | At least one check failed. |
| `notfound` | The function or script the problem asks for doesn't exist. |
| `NOT SUPPORTED` | The problem has neither `function_name` nor `script_name`, so it can't be verified. |

### notebook.saved

Sent when a notebook is saved, including autosaves. It is not sent when the
tail is the same as the last one sent for that notebook.

```json
{
  "path": "python/square.ipynb",
  "total_cells": 42,
  "tail": {"nbformat": 4, "metadata": {...}, "cells": [...]}
}
```

| Field | Value |
|---|---|
| `path` | Path of the notebook, relative to where JupyterLab was started |
| `total_cells` | Number of cells in the whole notebook |
| `tail` | The notebook with only its last 10 cells, and each text output cut to about 25 lines. See `ipytail.py`. |
