# Course website

The website for _The Craft of Computing_, built with [Quarto][].

    make build      # render the site into _site/
    make preview    # render and serve with live reload
    make push       # render and rsync _site/ to the server

## The schedule

The class schedule is data, not markup. Edit `schedule.yml`; the table itself
is generated.

- `schedule.yml` -- one entry per row of the table
- `gen_schedule.py` -- turns those entries into `overview/_schedule-rows.md`,
  run automatically by the `pre-render` hook in `_quarto.yml`
- `overview/schedule.qmd` -- the header row, the caption and the include
- `styles.css` -- the table styling, including the muted holiday rows

[Quarto]: https://quarto.org/docs/websites
