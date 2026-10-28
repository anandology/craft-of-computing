# Python Unit Plan

This is the working plan and handoff for the Python unit. Durable lesson-writing
rules live in `../LESSONS.md`.

## Direction

Students will use functions, methods, modules, scripts, files, and command-line
arguments before they learn to define functions of their own. This lets them
write useful programs early and gives function definitions a real purpose when
they are introduced later.

Keep each concept in its own lesson. Review every draft before writing the next
one rather than producing the rest of the unit in one pass.

## Current lessons

These lessons exist and are linked in the Unit 2 sidebar:

| Cluster | Lesson | File |
|---------|--------|------|
| Getting Started | Using Python | `using-python.qmd` |
| Getting Started | Values and Expressions | `values-and-expressions.qmd` |
| Getting Started | Variables | `variables.qmd` |
| Getting Started | Types and Errors | `types-and-errors.qmd` |
| Getting Started | Reading Errors | `reading-errors.qmd` |
| Collections and Repetition | Lists | `lists.qmd` |
| Collections and Repetition | The For Loop | `for-loop.qmd` |
| Functions, Methods, and Modules | Calling Functions | `functions.qmd` |
| Functions, Methods, and Modules | Using Methods | `methods.qmd` |
| Functions, Methods, and Modules | Using Modules | `modules.qmd` |
| Making Decisions | The If Statement | `making-decisions/if-statement.qmd` |
| Making Decisions | Boolean Expressions | `making-decisions/boolean-expressions.qmd` |
| Making Decisions | Combining Boolean Expressions | `making-decisions/combining-boolean-expressions.qmd` |
| Writing Programs | Writing Scripts | `writing-scripts.qmd` |
| Writing Programs | Reading Files | `reading-files.qmd` |
| Writing Programs | Command-Line Arguments | `command-line-arguments.qmd` |
| Writing Programs | Word Count | `word-count.qmd` |
| Writing Programs | The argparse Module | `argparse.qmd` |
| Working with Dictionaries | Dictionaries | `dictionaries/dictionaries.qmd` |
| Working with Dictionaries | Iterating over a Dictionary | `dictionaries/iterating.qmd` |
| Working with Lists | Sorting by a Rule | `lists/sorting-by-a-rule.qmd` |
| Working with Dictionaries | Lists of Records | `dictionaries/records.qmd` |
| Working with Dictionaries | Reading JSON | `dictionaries/reading-json.qmd` |

`python-basics.qmd` has deliberately not been changed. It remains linked after
the new lessons and now duplicates much of their content. Decide when to unlink
it, but preserve the file unless explicitly asked to remove or rewrite it.

`using-python.qmd` introduces the interpreter, scripts, and notebooks. Its
script section has been narrowed to a short overview so that `writing-scripts.qmd`
owns the detailed workflow.

## Proposed sequence

### Functions, Methods, and Modules

1. Calling Functions - complete draft
2. Using Methods - complete draft
3. Using Modules - complete draft

### Writing Programs

1. Writing Scripts - complete draft
2. Reading Files - complete draft
3. Command-Line Arguments - complete draft
4. Word Count - complete draft
5. The argparse Module - draft for review

### Making Decisions

This cluster sits after Functions, Methods, and Modules and before String Art,
so every later cluster can use `if`. Files live in `making-decisions/`.

1. The If Statement - draft for review
2. Boolean Expressions - draft for review
3. Combining Boolean Expressions - draft for review

### Working with Dictionaries

A new cluster after Working with Lists, in `dictionaries/`.

1. Dictionaries - draft for review. Covers creating, lookup, replacing and
   adding, the two uses (record and lookup table), and missing keys with `in`
   and `get()`.
2. Iterating over a Dictionary - draft for review
3. Lists of Records (`records.qmd`) - draft for review. A list of dicts
   with a nested list (trains), picking a field, filtering, totals, and
   sorting records with a key function.
4. Reading JSON (`reading-json.qmd`) - draft for review. JSON-to-Python
   mapping, `json.loads()`, `json.load()`, `JSONDecodeError`, and
   `json.dumps()` with `indent`. `json.dump()` is left out, because writing
   files is not taught.
5. Counting with a Dictionary - not started. Builds a dictionary in a loop,
   with word frequency as the main example and a script as the last section.
   Sorting by count can now use `key=`.

Left out: `setdefault()`, `update()`, `dict()` and dictionary comprehensions.

`key=` is taught in Sorting by a Rule (`lists/sorting-by-a-rule.qmd`), after
Sorting Lists: `len`, a `my_len()` that prints its calls, `int`, then a
`lowercase()` function. `my_len()` introduces `return` locally, because no
earlier lesson teaches it. Both sorting lessons are at the end of Working with
Lists, so Sorting by a Rule can use a list comprehension. List Comprehensions
no longer uses `sorted()` in `total.py`.
`str.lower` is deliberately not used as a key, to avoid confusion between a
method and a module-like name.

### Writing Modules

A cluster after Working with Dictionaries, in `writing-modules/`. Adapted from
<https://notes.pipal.in/2024/zeomega-python/writing-custom-modules.html>,
without the type hints. Assumes `def` and `return` are already taught. Keep
the reference's prose and examples; changes beyond the house lesson shape
need approval.

1. Writing Your Own Modules (`own-modules.qmd`) - draft for review. A file is
   a module, an import runs it once, `importlib.reload()`.
2. Running a Module as a Script (`module-as-script.qmd`) - draft for review. `__name__`,
   `if __name__ == "__main__":` and `main()`.
3. Docstrings - not started. `help()`, function and module docstrings. No
   `>>>` examples, so doctest is not implied.

### Testing Programs

A one-lesson cluster after Writing Modules, in `testing/`. Adapted from
<https://notes.pipal.in/2024/zeomega-python/testing.html>.

1. Testing with pytest - not started. `assert`, `test_` functions, running
   `pytest`, and a separate `test_*.py` file as the last section. Needs pytest
   in the students' setup; not yet checked.

### Working with APIs

A cluster in `api/`, before students start Rajdhani. It needs only
dictionaries, lists of records and Reading JSON, so it could also sit right
after Working with Dictionaries. Adapted from
<https://notes.pipal.in/2024/zeomega-sqlalchemy/working-with-apis.html>.

Every example uses two of our own servers: figlet (`figlet.apps.pipal.in`) and
the numbers API (`numbers.apps.pipal.in`, source in `~/numbers-api`). Changes
needed on the numbers API are listed in `~/numbers-api/TASKS.md`. Rajdhani
endpoints are not used, because Rajdhani is the exercise that comes after.
`requests` is installed by the craft setup since v21.

1. Fetching from the Web (`fetching.qmd`) - draft for review.
   `requests.get()` on figlet with the text written into the URL by hand,
   `.text` and `.status_code`, a 404 that returns an error page instead of
   raising, and the figlet web page against the API by `Content-Type`.
   The same request with `curl` and `curl -v`, reading the `>` request and
   `<` response lines. curl was used in class but not in the notes, so the
   lesson introduces it. The TLS lines of `curl -v` are elided with `...`.
   Outputs for the figlet API are from the local `figlet`, and the 200
   response headers in `curl -v` are modelled on its real 404, because the
   API was down when the lesson was written. Re-run them once it is up.
2. Query Parameters (`query-parameters.qmd`) - draft for review. Outputs are
   from figlet-web and numbers-api run locally, since both servers were down.
   `text` and `font`
   on figlet, then `params=` so requests builds the URL and encodes `&`, `#` and `+`.
   `response.url` shows the URL it built. `/fibs` with `a`, `b` and `n` as
   plain text. Practice: `/random` with `min`, `max` and `count`; it returns
   different numbers on each call.
   Done when students can call an endpoint with several params from a dict
   and explain the URL requests built.
3. JSON APIs (`json-apis.qmd`) - draft for review. `/fibs?format=json` against the
   plain text from the same endpoint, `response.json()`, and using the result
   as a dict and a list. Builds on Reading JSON and does not reteach
   `json.loads()` or `json.dumps()`.
   Done when students can call a JSON API and use the result without
   touching the raw text.
4. Sending Data with POST (`post-requests.qmd`) - draft for review. Data is sent in
   the body of a POST request.
   `/product` with `json={"numbers": [...]}` is the main example, `/stats`
   returns a dict, and `/range` takes several named fields. A missing field
   gives a 400 with an error message; `requests.get()` on a POST-only
   endpoint gives a 405. Practice: `/sum`, `/average` and `/sort`.
   Done when students can send a POST with a JSON body and explain how a
   body differs from query params.
5. Authentication (`authentication.qmd`) - draft for review. `/me` without
   a token gives a 401. The token is sent in an
   `Authorization: Bearer <token>` header, written in the code; reading it
   from an environment variable was dropped to keep the focus on APIs. `/me`
   shows who the token belongs to.
   Everyone uses the same `/store` URLs and gets their own values, because
   the token says who they are. POST creates a value, PUT updates it and
   DELETE removes it.
   Done when students can create, update and delete values in their own
   store and explain why a request without a token is refused.

Left out: other auth schemes (basic auth, API keys in the URL, OAuth),
sessions and cookies, `requests.Session`, and retries.

Lessons 3-5 outputs are from numbers-api run locally, with the uncommitted
token and store changes; re-run them once it is deployed.

### Later

1. Defining Functions

Defining Functions begins function problems and returned-value verification.

## The If Statement

Covers `if`, `else` and `elif`, the indented block, and an `if` inside a
function and inside a loop.

It depends on a lesson that teaches `def`, to be added before this cluster.
Until then, `def` is first taught in String Art, which comes after it.

## Boolean Expressions

One idea: a boolean expression is an expression whose value is `True` or
`False`. A condition is a boolean expression used in an `if` statement.
Covers `bool`, then sections by what is asked about: numbers (a table of the
six comparison operators), strings (`==`, `in`, `startswith()`,
`endswith()`), lists (`in`), and files (`os.path.exists()`,
`os.path.isfile()`).

The `os.path` examples are static blocks from a real run, because their output
depends on the directory. Truthiness, `is`, chained comparisons and `not in`
are left out.

## Combining Boolean Expressions

`and`, `or` and `not`, including `not in`, the mistake
`day == "Saturday" or "Sunday"`, and parentheses when `and` and `or` are mixed.

## The argparse Module

One idea: a script declares its arguments with `add_argument()`, and
`parse_args()` reads the command line, converts and checks the values, and
provides the help and the error messages. Covers a positional argument, an
option with `type=int` and `default`, a flag with `action="store_true"`, and
`description=` and `help=`.

The running example is `hello.py`. Real tools were tried first, but each
needed something taught later: slicing for `head.py`, a counter for `grep.py`.
The real tools are in practice: `square.py`, `ls.py` with `-e`, and `grep.py`
with `-i` and `-c`. Two of them carry a hint for something not taught yet: a
default of `""` for the `ls.py` option, and `print(line, end="")` in
`grep.py`.

The lesson defines keyword arguments in one sentence, because `type=int`
needs the term. Sorting Lists, which comes later in the sidebar, defines the
term again. Decide which lesson owns the definition.

`main()` and `if __name__ == "__main__":` are left out. They belong with a
lesson on importing your own modules. `choices`, `nargs` and subcommands are
left out too.

Help output was checked on Python 3.10 and 3.12, which agree. Python 3.13
prints an option with a value differently, as `-r, --repeat REPEAT`.

This lesson replaces the follow-up once planned for
`command-line-arguments.qmd`, a section that checks `len(sys.argv) < 2` and
displays a usage message. The parser does that check. That lesson still says
"A later lesson will introduce a way to check for this case".

## Calling Functions

Begin with `print()` so the first call has one simple string argument. Explain
that built-in functions are available without an import, then use `int()`,
`str()`, and `round()` with simple arguments:

- Parentheses call a function.
- Values passed to a function are arguments.
- Functions such as `int()`, `str()`, and `round()` return useful values.
- A returned value can be assigned or used in another expression.
- Calls can be combined with arithmetic, variables, and other calls, as in
  `len(names) + 1`, `round(n / 3, 4)`, and
  `round(sum(marks) / len(marks), 1)`.
- Practice can ask students to try `sorted(names)` and print the returned list.

## Using Methods

Introduce a method as a function attached to a value:

```python
name = "Python"
name.upper()
name.lower()
```

String methods return new strings; they do not change the original string.

Use `split()` to connect methods to lists:

```python
sentence = "Python is easy to read"
words = sentence.split()
len(words)
```

This prepares students to count words without defining a function.

## Using Modules

Introduce `import` and qualified names with the `os` and `time` modules:

```python
import os
os.getcwd()
os.listdir()
```

```python
import time
time.asctime()
```

Its practice is scripts: `pwd.py`, `date.py` and `ls.py`. It also shows that a
script must import the modules it uses; an import in the notebook does not
reach the script.

These results depend on the machine and the time, so the examples are static
`python` blocks with output from a real run, written for `/home/anand/python`.
Avoid modules that need dictionaries, such as `os.environ`, until dictionaries
are taught. Avoid `os.getlogin()`; it fails in most Linux terminals.

## Writing Scripts

Writing Scripts is one lesson. Keep it focused on:

- Creating a `.py` file from a notebook with `%%file filename.py`.
- Running it from a notebook with `!python filename.py`.
- Distinguishing Jupyter instructions (`%%file` and `!`) from code stored in
  the script.
- Python executing statements from top to bottom.
- Using `print()` for visible output.
- Editing and rerunning the `%%file` cell, then running the script again.

Use a small script as the main example. Keep the first script simple enough
that the file-writing and execution workflow remains the focus.

## Reading Files

Reading Files follows methods naturally:

```python
file = open("notes.txt")
text = file.read()
file.close()
```

`open()` returns a file object. `read()` and `close()` are methods on that
object. `readlines()` returns a list. Do not leave a file open in an example.
Use explicit `close()` until a lesson deliberately introduces `with`.

Do not call `read()` and then `readlines()` on the same file object without
explaining the file position. Use separate examples or reopen the file.

## Command-Line Arguments

This lesson follows modules, lists, and scripts:

- `sys.argv` is a list of strings.
- `sys.argv[0]` is the script name.
- Later elements are command-line arguments.
- A missing argument can produce the already-familiar `IndexError`.

The failure caused by a missing argument creates a reason to introduce
conditionals later.

## Word Count

A word-count script combines files, methods, lists, and command-line arguments.
It is the first natural place for a verified script problem.

Initially call the script `wordcount.py`, not a complete implementation of
`wc`. The Unix `wc` command has precise rules for lines, words, bytes, and
characters that a simple use of `len()` and `split()` does not reproduce.

## Practice and verification

No interactive browser practice or quizzes have been added. Current practice
is plain Markdown and is self-checked by running the code.

The installed Sigma magics, `%load_problem` and `%verify_problem`, support
function and script problems. They do not reliably verify the output of an
arbitrary earlier notebook cell.

Use Sigma when students begin Writing Scripts:

- Provide an input file when the script needs one.
- Run the submitted script.
- Compare its standard output with the expected output.

Use returned-value verification after Defining Functions. Do not retrofit Sigma
verification into the introductory values, variables, types, lists, or loops
lessons.

## Open decisions

- When to unlink the legacy `python-basics.qmd` page.
- The final syntax and renderer for interactive practice.
- How executable source and output should be visually connected.

An experimental bordered source-and-output card design was rejected and
reverted. Do not assume that cards are the desired direction.

## Verification status

The completed lesson markup and examples were checked individually. A full
`make build` was blocked in the current environment because Jupyter's
`nbformat` package is missing. A separate no-execute render encountered a
missing generated `cmdline/working-with-files_files/mediabag` path. Check the
environment before treating either failure as a lesson-source defect.

## Next step

Review the three **Making Decisions** lessons and the two **Working with
Dictionaries** drafts. A Sigma-backed script
problem is still to be added.
