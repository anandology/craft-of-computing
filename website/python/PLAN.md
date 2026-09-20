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
| Writing Programs | Writing Scripts | `writing-scripts.qmd` |
| Writing Programs | Reading Files | `reading-files.qmd` |
| Writing Programs | Command-Line Arguments | `command-line-arguments.qmd` |
| Writing Programs | Word Count | `word-count.qmd` |

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

### Later

1. Conditionals
2. Defining Functions

Conditionals are motivated by handling missing command-line arguments.
Defining Functions begins function problems and returned-value verification.

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

Introduce `import` and qualified names. Use the `math` module so every rendered
result is deterministic:

```python
import math
math.sqrt(81)
```

```python
math.ceil(3.2)
```

```python
math.pi
```

Avoid naming a script `pwd.py`; Python has a standard-library module named
`pwd`. Use `where.py` or `cwd.py` instead.

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

Add a Sigma-backed script problem, then draft **Conditionals** using a missing
command-line argument as its motivating case.
