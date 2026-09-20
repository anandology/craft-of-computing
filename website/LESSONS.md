# Authoring Lessons

This document records the lesson-writing decisions made while restructuring the
Python unit. It is both an authoring guide and a handoff for future sessions.
It is intended to contain all context needed to continue the work.

## Goal

Each lesson should teach one idea in a form that a student can read, try, and
return to later. Prefer several short lessons over one chapter that combines
unrelated concepts.

A lesson is not short because it has few lines. It is short because it asks the
student to build one new mental model. Supporting details belong only when they
help explain or use that model.

The course should read as a book: continuous prose that explains ideas through
evidence. It is not a reference manual or a sequence of disconnected lab
instructions. A conceptual lesson should be readable without first creating a
scratch directory or performing a setup ritual.

## Site constraints

The site is a static Quarto website. Readers are anonymous. There is no login,
backend, or progress tracking.

Do not add:

- Progress bars or completion marks.
- Lesson counters such as "Lesson 4 of 12."
- `localStorage` or other hidden progress state.
- Features that require a server-side checker.

The sidebar already communicates position in the course. Practice must either
be checked in the browser, checked by tools installed on the student's machine,
or presented with an answer the student can reveal.

Pages are organized by unit. Each unit folder has a `_metadata.yml` file with a
unit body class such as `body-classes: unit-2`. The body class scopes the unit's
accent color in the theme.

The Quarto configuration defines one sidebar per unit. Each sidebar has an `id`
and groups lessons with `section:` entries. Add every published lesson to the
appropriate sidebar; a new file is not added automatically. Do not insert fake
separator items such as `text: "---"`, because they break previous and next
navigation across sections.

Unit links belong in the navbar, not in a custom sidebar switcher. Page
navigation and breadcrumbs should remain enabled.

Directories linked as destinations need an `index.qmd`. Unpublished pages
belong in `drafts/`, which is excluded from rendering.

## Portability

Lesson frontmatter and prose should remain easy to move to another static-site
generator.

Use only this lesson metadata unless a page has a specific need:

```yaml
---
title: "The For Loop"
unit: 2
cluster: "Collections and Repetition"
---
```

The `cluster` value must match the sidebar section.

Do not use Quarto shortcodes in lesson bodies. Callouts are allowed when a
warning or note needs special emphasis.

Executable `{python}` cells are an intentional exception in the current Python
unit because their generated results are evidence for the explanation. The
`#| error: true` option is used once where a rendered traceback is itself the
subject of the lesson. Record a clear reason before adding another
generator-specific feature.

Practice will eventually use a project-owned fenced syntax rather than a
Quarto quiz shortcode. Propose and review that syntax before implementing it.
Before writing a renderer, check whether a maintained Quarto extension meets
the requirements. If none does, prefer a small Lua filter and dependency-free
JavaScript of roughly 100 lines or less, with no build step.

Put shared visual changes in `theme.scss`, not in lesson bodies. Preserve the
warm paper theme, the unit accent colors, and the established typography unless
a design change has been approved.

## Restructuring existing material

When splitting an existing page, preserve its prose unless a rewrite has been
explicitly approved. Moving a section into a focused lesson is different from
rewriting it. Flag wording that needs correction instead of silently changing
the author's meaning.

Keep existing pages rendering while replacement lessons are being developed.
Unlink or remove an old page only after that decision has been made explicitly.

## Audience and language

The students have varied backgrounds, and many may not be comfortable reading
English. Make the English simple, but do not replace technical vocabulary with
vague language.

Use these rules:

- Introduce the correct term when the concept first appears. Use `integer`,
  `floating-point number`, `Unicode`, `method`, and `iteration` rather than
  avoiding those words.
- Explain a technical term in a short sentence and then use it consistently.
- Prefer short sentences with one claim each.
- Use the same noun again when a pronoun could be ambiguous.
- Describe the exact action a student should take. For example, write "Enter a
  whole number" rather than "Type one," where `one` could be read as literal
  input.
- Distinguish actions performed by Python from actions performed by an
  interface. Python evaluates an expression; an interpreter or notebook
  displays its result.
- Do not name an interface unless the difference matters to the lesson. Avoid
  interrupting the explanation with incidental differences between JupyterLab
  and the Python interpreter.
- Do not describe a result that the student will not see in the environment
  used for the course.
- Do not oversimplify until a statement becomes false. For example, a `float`
  represents a real number; floating-point precision can be deferred without
  renaming it "a number with a fractional part."
- Treat text in every language as ordinary text. Introduce Unicode as the name
  of the standard, not as a special procedure needed for non-English text.

Read every sentence literally before publishing it. Check whether a beginner
could interpret an instruction in a different way.

## Lesson scope

Start with the central idea and use it to decide what stays in the lesson.

Good combinations share one mental model:

- Number and string values belong together in Values and Expressions because
  both demonstrate that expressions produce values.
- Creating a list and selecting an element belong together because indexing is
  part of the model of an ordered collection.
- `TypeError` belongs with types because it demonstrates that types determine
  valid operations.

Split concepts when one can be understood without the other:

- Variables follow values because students should meet values before naming
  them.
- General error reading follows types and `TypeError`.
- Repetition follows lists because a loop needs a collection worth visiting.
- Calling functions, using methods, and importing modules should be separate
  lessons even though later programs use all three.
- Writing scripts should be its own lesson.

Defer details that do not help the current idea:

- Multiline strings, escapes, and Unicode code points do not belong in the
  first lesson about text values.
- Floating-point precision does not belong in the first lesson about numeric
  values.
- List mutation is not needed at this level.
- Comments should be introduced when a program genuinely benefits from one,
  not as an isolated syntax lesson.
- Defining functions comes after students have used functions, methods,
  modules, scripts, files, and command-line arguments.

## Lesson shape

Use this order unless the content gives a strong reason not to:

1. Open with a concrete situation or limitation.
2. State what the lesson gives the student.
3. Add `In this lesson, we'll learn how to:` with one to four outcomes.
4. State the central idea in bold.
5. Explain the idea through small, cumulative examples.
6. Add a Practice section.
7. Add an optional Quiz section only when it checks a useful distinction.
8. End with a Summary table.
9. End the summary with one idea to carry forward.

The opening should help a student decide whether the lesson is relevant. Do
not begin with a definition that has no motivating context.

The central idea should be a rule that explains the examples, not a slogan.
For example:

> A variable is a name that refers to a value.

Each section should advance that idea. If a section needs a second central
idea, it probably belongs in another lesson.

## Sequencing concepts

Teach a mechanism before its first unexplained use. If a small mechanism is
needed locally, introduce it immediately before the example.

Examples from the current drafts:

- Introduce `print()` before using it in the Unicode examples.
- Introduce values before variables.
- Introduce lists and indexes before `for` loops.
- Introduce `IndentationError` as an error students may encounter, then give
  indentation a real purpose in The For Loop.
- Introduce modules before using `sys.argv` from the `sys` module.
- Introduce methods before calling `read()` on a file object.

Reuse earlier knowledge instead of reteaching it. The For Loop can use lists,
variables, `print()`, and indentation because those ideas have already
appeared.

## Continuity between lessons

Treat every cross-reference as a dependency that later edits must preserve.

- Refer to a durable concept that an earlier lesson deliberately hands
  forward.
- Do not depend on a specific example or quote from another lesson unless it is
  essential.
- Do not add references merely to make the unit sound connected.
- Add a closing bridge only when the named lesson actually comes next in the
  sidebar and continues the same idea.
- Establish a convention once. Later lessons should use it rather than reopen
  the decision.

Warn students where a mistake causes data loss or silent failure. Use a warning
callout rather than hiding the warning in a long paragraph. Do not turn every
minor error into a callout.

## Examples

Examples are part of the explanation. They must be accurate and worth
understanding.

- Run every command and code example. Do not invent or approximate output.
- Check that prose describes the actual rendered result.
- Introduce names and syntax before using them.
- Use small values that make the operation visible.
- Prefer examples that connect to later work.
- When code changes state, show the relevant state before and after the change.
- Do not add a second concept merely to make an example look realistic.
- Do not repeat generated output in a separate text block. Let the output
  appear once, then explain what it demonstrates.
- Keep names descriptive. Use singular names for one element and plural names
  for collections, such as `language` and `languages`.
- Avoid script filenames that shadow standard-library modules. In particular,
  do not use `pwd.py`; Python has a module named `pwd`. Use `where.py` or
  `cwd.py` instead.

Use executable `{python}` blocks when the rendered result is part of the
lesson. Use static `python` blocks for code that students must predict, code
that is intentionally invalid, or code that should not execute during the
render.

Executable cells are an intentional generator-specific feature in the current
Python lessons. Do not add other generator-specific syntax without recording
why it is needed.

## Terminal transcripts

Use a `session` fence for terminal commands and their output. Write the block
as it appears on screen:

```session
$ python date.py
Mon Sep 21 10:30:00 2026
```

The session filter removes the leading `$` from selected text and redraws it as
an unselectable prompt. Never tell students to type or remove the prompt.

Prefer one command per transcript so its result can be explained directly. A
command ending in `\` may continue on the next line. Long terminal lines wrap
on small screens.

Use only commands already introduced. Examples use `/home/anand` as the home
directory. Shell errors and command output must match the real program exactly.
Do not add copy buttons to terminal blocks; typing commands is part of the
command-line unit's practice.

## Errors

Errors are evidence, not decoration. Show an error only when reading or fixing
it supports the lesson.

Teach students to read the last line first:

- The text before the colon names the error.
- The text after the colon explains the immediate problem.
- The lines above identify where the error occurred.

Use a complete rendered traceback at least once in the Reading Errors lesson.
The first `TypeError` example uses an executable block with `#| error: true`
for this reason. This is an intentional Quarto-specific exception: the actual
traceback is the subject of the lesson.

After the complete example, shorter examples may quote only the final line
when the rest of the traceback would repeat the same lesson.

Use errors in dependency order:

- `TypeError` follows value types.
- `SyntaxError`, `IndentationError`, and `NameError` belong in Reading Errors.
- `IndexError` appears after list indexes.

Error text can change between Python versions. Verify the wording against the
course environment before publishing it.

## Practice

Every lesson ends with practice before the summary. Practice should exercise
the central idea and should not introduce new syntax.

State the result to achieve, not the exact sequence of code to type. Give
students enough information to begin, then leave them to choose and combine the
operations they have learned.

Give every problem the same visual form, using a `### Problem N` heading. Start
with Problem 1 and number problems continuously from top to bottom. If practice
has several sections, do not restart the numbering in a new section.

Useful forms at this stage are:

- Predict a value or output, then run the code and compare.
- Explain why the actual result differs from a prediction.
- Write a small expression or code fragment that produces a stated result.
- Correct code using an error message.
- Combine mechanisms already taught in the lesson sequence.

Keep the amount small. Two to five meaningful tasks are better than many
repetitive questions.

A separate quiz is optional. Add one only when it checks a misconception or an
important distinction that practice does not already cover. Predicting output
is already quiz-like; do not duplicate it merely to add a Quiz heading.

The planned browser practice has two forms:

- Predict-the-output questions are checked in the browser and show an
  explanation after checking, not only right or wrong.
- Tasks performed in the student's own terminal or Python environment cannot
  be checked by the static website. They provide a hint and a revealable
  answer.

Until the custom practice syntax and renderer are available, use plain
Markdown practice that students check by running the code. Do not imitate an
interactive checker with lesson-specific HTML.

## Sigma verification

The installed Sigma magics are `%load_problem` and `%verify_problem`. The
current verifier supports function and script problems. It does not reliably
verify the output of an arbitrary earlier notebook cell.

Do not force Sigma verification into the introductory lessons. For values,
variables, types, lists, and loops, students should predict, run, and compare.

Begin using Sigma when students write scripts or define functions:

- A script problem can provide input files, run the script, and compare its
  standard output.
- A function problem can call the function with known inputs and verify the
  returned value.

This boundary keeps early practice simple and makes verification meaningful.

## Summaries

Every lesson ends with one summary table and one idea to carry forward.

The table should:

- Stand on its own for a student returning later.
- Use independent examples rather than an execution transcript.
- State rules directly.
- Use meaningful names and self-explanatory placeholders.
- Include only concepts taught in the lesson.
- Use the correct technical terms.

Do not introduce a term in the summary. For example, introduce Unicode in the
body before using `Unicode string` in a summary row.

The carry-forward sentence should state the lesson's central idea in a form
that the next lesson can rely on.

## Titles and filenames

Choose titles that students can remember, search for, and say in class. Prefer
the established technical name when it is clear.

Titles should be plain and unique across the site. A section title should not
repeat or closely paraphrase its parent title.

For example, **The For Loop** and `for-loop.qmd` are easier to recall than
**Repeating with for** and `repeating-with-for.qmd`.

Use lowercase, hyphenated filenames that match the title closely:

- `values-and-expressions.qmd`
- `types-and-errors.qmd`
- `reading-errors.qmd`
- `for-loop.qmd`
- `command-line-arguments.qmd`

Use the frontmatter contract in the Portability section. Add every published
lesson to `_quarto.yml`; creating a file does not add it to navigation.

## Building and verification

Run `make build` after structural or content changes. It renders the complete
site into `_site/`.

The pre-render hook regenerates `overview/_schedule-rows.md` from
`schedule.yml`. Never edit the generated rows by hand. A build may update that
tracked file even when the lesson itself does not concern the schedule.

For every lesson:

1. Run the exact Python examples independently and confirm their values,
   output, and error text.
2. Render the lesson or site and inspect the generated output.
3. Confirm its sidebar section and previous/next order.
4. Check the page at desktop and mobile widths.

If a full render is blocked by the local environment, validate the Markdown
and examples separately and record the blocker. Do not report a successful
render when only source validation was possible.
