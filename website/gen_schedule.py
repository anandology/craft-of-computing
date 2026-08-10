#!/usr/bin/env python3
"""Generate the class schedule table rows from schedule.yml.

The script reads a list of rows, renders each field as a table cell --
joining list values so each item lands on its own line -- and writes out the
body of a pandoc pipe table. The header row, the caption and all the styling
live in overview/schedule.qmd, which pulls the rows in with an include.

The one thing it interprets is `holiday: true`, which tags the row so
styles.css can mute it. Everything else is passed through as written.

Run by quarto through the pre-render hook in _quarto.yml.
"""

import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
SOURCE = HERE / "schedule.yml"
TARGET = HERE / "overview" / "_schedule-rows.md"

# Order of the fields across the table. Must match the header in schedule.qmd.
COLUMNS = ["week", "day", "date", "times", "session", "topics"]

# Rows per week. The week separators in styles.css are drawn on every even
# row, so a week with any other number of rows shifts the borders below it.
ROWS_PER_WEEK = 2

# A `holiday: true` row gets this class attached to its Session cell.
# styles.css mutes any row containing it.
HOLIDAY_COLUMN = "session"
HOLIDAY_CLASS = "holiday"


def cell(value):
    """Render one field as a table cell. Lists get one item per line."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "<br>".join(str(item) for item in value)
    return str(value)


def render(record):
    cells = [cell(record.get(name)) for name in COLUMNS]

    if record.get("holiday"):
        index = COLUMNS.index(HOLIDAY_COLUMN)
        cells[index] = "[%s]{.%s}" % (cells[index], HOLIDAY_CLASS)

    return "| " + " | ".join(cells) + " |"


def check_rows_per_week(records):
    counts = {}
    for record in records:
        week = record.get("week")
        counts[week] = counts.get(week, 0) + 1

    for week, count in counts.items():
        if count != ROWS_PER_WEEK:
            print(
                f"{SOURCE.name}: {week} has {count} rows, expected "
                f"{ROWS_PER_WEEK}. The week separators will be misaligned "
                f"from here on.",
                file=sys.stderr,
            )


def main():
    records = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    check_rows_per_week(records)
    rows = "\n".join(render(record) for record in records)
    TARGET.write_text(rows + "\n", encoding="utf-8")
    print(f"{TARGET.name}: wrote {len(records)} rows")


if __name__ == "__main__":
    main()
