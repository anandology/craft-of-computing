# Notebook preview

Captures the events sigma posts from student machines and shows everyone's
copy of a notebook side by side, updating as they work.

## Running it

    python preview/app.py                     # development, port 8082
    cd preview && gunicorn -b 127.0.0.1:8082 app:app

Run gunicorn from this directory: like `app/`, the modules import each other
by plain name rather than as a package.

Students point sigma at it by setting `SIGMA_WEBHOOK_URL`:

    SIGMA_WEBHOOK_URL=http://<host>:8082/webhook

## Pages

| URL | What it is |
| --- | --- |
| `/preview` | every notebook name seen, most recently active first |
| `/preview/<name>` | everyone's copy of that notebook, refreshing every 5s |
| `/preview/_tail/<owner>/<name>.ipynb` | one student's newest tail, as JSON |
| `/webhook` | where sigma posts events |

## Storage

One SQLite database, `data/events.db`, overridden with `PREVIEW_DB`. The
tables are in `schema.sql`, applied on every start.

The `events` table is append-only: one row per event, the whole envelope in
`payload`, the fields the preview queries on lifted into columns beside it.
The rows for a notebook in `id` order are its history; the preview reads only
the newest row per `(name, owner)`.

sigma posts a `notebook.saved` only when the notebook's tail actually changed,
so a row means the student did something and `received_at` is a last-seen
time. At 40 students saving every few seconds this is a handful of writes a
second, which one SQLite writer in WAL mode does not notice.

What sigma sends is already a notebook: the last cells with their outputs
clamped, keeping the top-level `nbformat` and `metadata`. So nothing here
parses or rewrites a notebook — the stored tail goes to the browser as it
arrived and nbpreview renders it.

## Notes

- **Subdirectories are ignored.** A notebook's collection name is its filename
  without `.ipynb`, so two notebooks with the same name in different
  directories share a page.
- **No authentication.** Anything that can reach `/webhook` can write to the
  database. Fine on a private network, not on the open internet.
- **The student list on a collection page is fixed at page load.** Someone who
  starts saving afterwards appears on the next reload.

`static/nbpreview/` is vendored from
[nbpreview](https://github.com/jsvine/nbpreview); see its `LICENSE.txt`.
