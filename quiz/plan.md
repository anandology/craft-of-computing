---
status: in-progress
created: 2026-08-03
---

# Quiz

Quiz collects live answers from students during class. Quizzes are YAML files in this
repository; the app serves each one as a phone-friendly form and a projector-friendly
results page, and is deployed as a single Cloudflare Worker backed by D1.

## Design

**One Worker, one table.**

The whole application is `src/index.ts` on Cloudflare Workers, with a single D1 table.
There is no Durable Object: coordination would only be needed to push live updates over
a websocket, and the results page polls instead, so no per-session actor has to exist.
There is no framework, no client bundle and no static asset pipeline — pages are template
strings and their behaviour is a small inline script. D1 on the free plan covers a class.

**Quizzes are repository files, and the filename is the URL.**

`quizzes/q0.yml` is answered at `/q0` and watched at `/q0/results`. A build step
(`scripts/build.mjs`) compiles every file into `src/quizzes.json`, which the Worker
imports, so malformed YAML fails before deployment rather than during a lecture. Nothing
about a quiz is editable at runtime and there is no authoring UI; changing a question is
an edit and a deploy.

A question with `opts` is a fixed choice, without it is free text. Mentimeter's model —
one question per slide, the audience's phone slaved to the presenter's current slide —
needs presenter-driven state sync to work. Separate files give the same effect for free:
advancing means naming a different URL. A file therefore holds however many questions
belong together, and the count changes nothing about how it is served.

**Answers are keyed by voter, so a second answer replaces the first.**

Each browser mints a UUID into `localStorage` on first visit. The primary key is
`(quiz, voter, qid)` and every write is an `INSERT OR REPLACE`, so changing an answer
updates in place and can never double-count. The same property makes resuming possible:
`/<quiz>/mine?voter=…` returns that voter's own answers, the page prefills them and opens
at the first unanswered question, or at the review screen if there are none.

This identity is deliberately weak, and rests on every student having their own device —
a laptop if not a phone. Clearing site data, using another browser or answering on a
second device produces a new respondent. That is the right trade for a classroom and the
wrong one for anything that must be counted exactly.

**Answering is one question at a time, saved as it goes.**

Choosing an option advances by itself; free text advances on Enter or Next; Back revisits.
Each answer is saved the moment it is given rather than on a final submit, so a student who
stops halfway still counts for what they answered. The consequence to remember is that the
response total counts anyone who answered at least one question.

**Results are public, polled, and ordered by the question rather than by popularity.**

`/<quiz>/results` re-fetches every two seconds and animates bar widths. Fixed options draw
in the order the YAML declares them, so a scale stays a scale instead of being resorted by
count. Free text is grouped case-insensitively with whitespace collapsed, capped at the top
ten, and capitalised for display. Results are deliberately unauthenticated so students can
watch them too, which also means the URL is guessable.

## Verification

`npm run build` is the first gate: it rejects a missing title, an empty question list, a
duplicate question id, a bad slug and an options list shorter than two.

Beyond that the app is checked by driving it — the served pages have no importable units
worth testing in isolation, but the request/response and browser behaviour are worth
pinning down. Those checks belong to whichever task adds the behaviour, against
`wrangler dev` and a headless browser; there is no separate testing task.

Manual release check:

- Answer a quiz on a phone, reopen it, and confirm the answers come back prefilled
- Confirm changing an answer moves the bar rather than adding a second response
- Open the results page on the projector while several people answer
- Confirm a free-text question groups `Telugu` and `telugu` into one bar
- Confirm a scale question stays in declared order once one bucket overtakes another

## Tasks

Each task is a slice a student or a lecturer can use, not a layer. The schema, the build
step and the pages all move together within one.

### [DONE] answering: a student answers a quiz written in the repo

Author quizzes as `quizzes/*.yml`, compiled to `src/quizzes.json` by a build step that
rejects a malformed file before it can deploy, with the filename as the slug and the URL.
Serve each one as a stepper: one question at a time, a progress bar, choices that advance
by themselves, text that advances on Enter or Next, and Back to revisit.

Store answers in D1 keyed by `(quiz, voter, qid)` and written with `INSERT OR REPLACE`,
saving each answer as it is given rather than at the end. Give each browser a `localStorage`
UUID and serve `/<quiz>/mine?voter=…` so a returning student's answers come back prefilled,
opening at their first unanswered question or at a review screen that can change any of them.

**Acceptance Criteria:**

- [x] `quizzes/q0.yml` is answered at `/q0`; a duplicate question id, missing title, empty
      question list or one-option `opts` fails `npm run build`; an unknown slug is 404
- [x] Choosing an option advances without a further click; text advances on Enter or Next;
      Back shows the earlier question with its answer still selected
- [x] Reloading after finishing opens the review screen intact; reloading after two of four
      opens at question three; a browser with no stored id starts empty
- [x] Changing an answer leaves that voter's row count unchanged
- [x] A value not offered by a fixed-choice question is discarded; a malformed voter id is 400

### [DONE] results: the room watches the answers arrive

Serve `/<quiz>/results`, re-fetching every two seconds and animating bar widths. Draw fixed
options in the order the YAML declares them and free text by frequency, grouped
case-insensitively with whitespace collapsed, capped at ten and capitalised for display.

**Acceptance Criteria:**

- [x] A scale question keeps its declared order as counts change
- [x] `Telugu` and `telugu` occupy one bar
- [x] A submitted `<script>` tag appears as characters, not markup
- [x] A dropped poll leaves the last numbers on screen instead of an error

### [DONE] in-slides: the results are a slide in the presentation

Serve `/<quiz>/slide`: results filling the left two thirds, and a QR code for the answer
page, the URL and the response count on the right third. Generate the QR in the Worker as
inline SVG rather than fetching an image, so a projector with a flaky network still shows
it, and force dark-on-white regardless of page theme because a tinted QR scans unreliably.

Show one question at a time — four are clipped at 16:9. The slide polls the whole quiz and
hides all but the current question, so stepping between them costs no request and no reload.
Step with the arrow and page keys, since a presentation clicker sends those, or with the
arrows beside a `2 / 4` counter in the join panel. `?q=<id>` opens at a question and `?q=all`
puts them all on one slide.

The QR also expands to fill the screen, for the "everyone scan this" moment at the start of a
class: click it or press `f`, and `?qr` opens there so it can be its own slide in a deck. The
panel is top-aligned rather than centred, because centring re-balances the column per question
and makes the title jump as the slide is stepped.

**Acceptance Criteria:**

- [x] Columns are exactly 2fr/1fr and neither axis scrolls at 1600x900
- [x] The default renders one question; `?q=all` renders the whole quiz
- [x] Arrows and clicker keys move one question at a time and stop at both ends rather
      than wrapping; the counter follows; a poll landing mid-talk does not reset the view
- [x] The results page is unaffected: it still shows every question at once
- [x] The QR fills the screen on click, `f` or `?qr`, keeps counting while it is up, and
      closes on click, `f`, `Esc` or the next click of the clicker
- [x] The QR renders about 300px on a 1600x900 projector and stays dark-on-white in
      both light and dark themes
- [x] The URL shown is the real origin, so it is right on workers.dev or a custom domain

## Backlog

Unvetted ideas, not scheduled work. Nothing here is a task until it is approved and moved
up to `## Tasks`. Each is cheap to add later because none of them changes the schema.

**question-types.** Free text is a poor fit for a question with a known long answer list,
such as Indian states: it invites spelling variants that only case folding repairs. A
fixed-choice type usable at thirty-odd options on a phone, plus shared option lists
reusable across quizzes. Possibly ordered buckets declared as such rather than relying on
option order.

**export.** Raw rows for one quiz, so cohort answers can be cited later in the course and
so a semester's data can be reviewed before it is deleted.

**live-push.** Two-second polling is invisible in a room and costs nothing to run. If it
ever must be instant, a Durable Object per quiz with hibernatable websockets is the shape.

**moderation.** Free-text answers appear on the results page as soon as they are submitted.
Mentimeter stages them for the presenter to publish, because in a large enough room someone
eventually types something that should not be on a screen.

## Handover

Both slices that make the app work are done and verified locally: quizzes are authored in
`quizzes/*.yml`, answered one question at a time at `/<slug>`, and watched at
`/<slug>/results`. Answers save per question, prefill on return, and replace rather than
duplicate.

**It has never been deployed.** Everything was checked against `wrangler dev` with a local
D1 and a headless browser; nothing has run on Cloudflare. `wrangler.toml` still carries a
placeholder `database_id`, so going live means creating the database, applying `schema.sql`
remotely and deploying — the steps are in the README.

Two loose ends worth knowing before continuing. `quizzes/q1.yml` is a placeholder written
to demonstrate the single-question case and should be replaced with a real quiz. And the
checks so far live in ad-hoc scripts outside the repository, so they should be brought in
alongside the next change rather than left to be re-run by hand.
