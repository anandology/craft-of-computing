-- Events posted by sigma from student machines.
--
-- Append-only: one row per event, so the rows for a notebook in id order are
-- its history. The preview reads only the newest row per (name, owner).
--
-- The whole envelope is kept in payload and the fields the preview queries on
-- are lifted into columns beside it, so a change to what the preview shows
-- does not need a migration of what was already captured.

CREATE TABLE IF NOT EXISTS events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,

    -- When this server stored the event. sigma only posts a notebook.saved
    -- when the tail actually changed, so this doubles as a last-seen time.
    received_at   TEXT NOT NULL,
    -- When the student's machine sent it, and thus subject to its clock.
    sent_at       TEXT,

    event         TEXT NOT NULL,
    training      TEXT,
    -- The registered username, falling back to the unix user. See store.owner_of.
    owner         TEXT,
    sigma_version TEXT,

    -- The notebook filename without .ipynb: the collection everyone's copy
    -- is grouped under. Null for events that carry no notebook.
    name          TEXT,
    -- The path as sigma sent it, kept whole even though name ignores directories.
    path          TEXT,
    -- Cells in the student's whole notebook, not in the stored tail.
    total_cells   INTEGER,

    -- The full JSON envelope, tail included.
    payload       TEXT NOT NULL
);

-- Covers both preview queries: the newest row per owner within a collection,
-- and the newest row for one owner's copy.
CREATE INDEX IF NOT EXISTS events_notebook ON events (event, name, owner, id);
