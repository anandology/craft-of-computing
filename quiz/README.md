# Quiz

Quiz is a webapp to live quiz students in the class to get their input interactively.

For simplicity, the questions or quizes are created in the repo and the webapp will provide a way to answer them and see the results. I may want to show some graphs as well.
All of these could be part of my slides.

## Writing a quiz

One YAML file per quiz in `quizzes/`. The filename is the URL:
`quizzes/q0.yml` is answered at `/q0` and watched at `/q0/results`.

```yaml
title: About You

questions:
  - id: state
    q: Which state are you from?          # no opts -> free text

  - id: medium
    q: What was the medium of instruction until 10th?
    opts: [English, Regional language, Mixed]
```

`id` must be unique within the file and is what the answers are stored under, so
renaming one orphans any votes already cast for it.

## Answering

One question at a time, Typeform style. Picking an option advances by itself;
free text advances on Enter or Next. Back revisits earlier questions.

Every answer is saved the moment it is given rather than at the end, so someone
who stops halfway still counts for what they did answer. Reopening the page
fetches what that person said before, prefills it, and jumps to their first
unanswered question — or to the review screen if they finished. From there any
answer can be changed, and the change replaces the old one.

## Results

`/q0/results` polls every 2s. Fixed options are drawn in the order declared, so
scale questions stay in order instead of being resorted by popularity. Free text
is grouped case-insensitively (`Telugu` and `telugu` are one bar), whitespace is
collapsed, and only the top 10 are shown.

## On a slide

`/q0/slide` is a full-screen view for the projector: results fill the left two
thirds, and a QR code, the answer URL and the response count sit on the right.
It shows one question at a time, because four get clipped at 16:9.

Move between questions with `←` / `→` (a presentation clicker's page keys work
too) or the arrows under the count, which also show `2 / 4`. Every question is
polled whether or not it is on screen, so stepping is instant.

    /q0/slide           opens at the first question
    /q0/slide?q=years   opens at that question
    /q0/slide?q=all     the whole quiz on one slide, clips if it is long

Put it on a slide with an iframe, or just open it full-screen on the projector.

## Deploy

    npx wrangler d1 create quiz          # paste database_id into wrangler.toml
    npx wrangler d1 execute quiz --remote --file=schema.sql
    npm run deploy

Locally:

    npx wrangler d1 execute quiz --local --file=schema.sql
    npm run dev

`npm run deploy` regenerates `src/quizzes.json` from the YAML first, so a typo
fails at build rather than in class.

## Notes

Voters are identified by a UUID in `localStorage`. Re-answering replaces the
earlier answers rather than adding to them, so students can change their mind,
and clearing site data lets someone vote twice — fine for a classroom, not a
ballot. That UUID is also what `/q0/mine?voter=…` returns answers for, so
anyone holding it can read that person's answers; it is 122 bits of randomness
and never leaves their browser, but it is the only thing protecting them.

Answers within one quiz are linked by that UUID. For a demographic survey that
is enough to identify individuals in a small class, so tell students the survey
is anonymous but linked, and drop the rows at the end of the semester:

    npx wrangler d1 execute quiz --remote --command "DELETE FROM votes WHERE quiz='q0'"

Results are public — anyone with the URL can watch. That is deliberate, so
students can see them too.
