#!/usr/bin/env python3
"""Turn a markdown quiz into the JSON that the quiz app serves.

    python app/md2quiz.py app/quizzes/0.md

writes app/quizzes/0.json next to it. See "Writing a quiz" in app/README.md
for the shape of the markdown.
"""

import argparse
import json
import os
import re
import sys

FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
ITEM = re.compile(r"^\s*[-*+]\s+(.*)$")
CHECKBOX = re.compile(r"^\[([ xX])\]\s*(.*)$")
QUESTION_ID = re.compile(r"\{#([a-z0-9][a-z0-9-]*)\}")


class Bad(Exception):
    """Markdown that cannot be turned into a quiz."""


def fenced(lines):
    """Mark the lines that sit inside a fenced code block.

    Options are found by reading up from the end of a question, and a code
    block is entitled to contain lines that look exactly like list items.
    """
    inside, mask, closing = False, [], None
    for line in lines:
        m = FENCE.match(line)
        if m and not inside:
            inside, closing = True, m.group(1)
            mask.append(True)
        elif m and inside and line.strip().startswith(closing):
            inside = False
            mask.append(True)
        else:
            mask.append(inside)
    return mask


def sections(lines, mask):
    """Split into (title, intro lines, [(heading, body lines)])."""
    title, intro, out = None, [], []
    for line, in_code in zip(lines, mask):
        m = None if in_code else HEADING.match(line)
        level = len(m.group(1)) if m else 0
        if level == 2:                       # ## starts a question
            out.append((m.group(2).strip(), []))
        elif level == 1 and not out and title is None:
            title = m.group(2).strip()
        elif out:
            out[-1][1].append(line)
        else:
            intro.append(line)
    return title, intro, out


def split_options(body, mask):
    """Take the run of list items that ends a question as its options.

    Everything before them is the question itself, so it can be as long as it
    likes and hold code blocks, images or a list of its own.
    """
    end = len(body)
    while end and not body[end - 1].strip():
        end -= 1

    start = end
    while start:
        line, in_code = body[start - 1], mask[start - 1]
        if not in_code and ITEM.match(line):
            start -= 1
        elif not line.strip() and start < end:   # a blank line inside a loose list
            start -= 1
        else:
            break

    while start < end and not body[start].strip():
        start += 1
    return body[:start], [ITEM.match(l).group(1).strip() for l in body[start:end] if l.strip()]


def parse_option(text):
    """Return (text, is_answer). A `- [x]` item is the correct one."""
    m = CHECKBOX.match(text)
    if not m:
        return text, False
    return m.group(2).strip(), m.group(1).lower() == "x"


def parse(markdown, roll=None):
    lines = markdown.splitlines()
    mask = fenced(lines)
    title, intro, found = sections(lines, mask)
    if not found:
        raise Bad("no questions: a question starts at a '## ' heading")

    quiz = {"title": title or "Quiz"}
    if roll:
        quiz["roll"] = roll
    quiz["description"] = "\n".join(intro).strip()
    quiz["questions"] = []

    seen = set()
    for n, (heading, body) in enumerate(found, start=1):
        where = f"question {n}" + (f" ({heading})" if heading else "")
        body_mask = fenced(body)
        text, options = split_options(body, body_mask)

        if len(options) < 2:
            raise Bad(f"{where} has {len(options)} options; it needs at least two, "
                      "written as a '- ' list at the end of the question")

        parsed = [parse_option(o) for o in options]
        answers = [i for i, (_, right) in enumerate(parsed) if right]
        if len(answers) > 1:
            raise Bad(f"{where} marks {len(answers)} answers as correct; "
                      "only one option may be '- [x]'")

        # An explicit id in the heading survives questions being added or
        # reordered later; without one, answers already recorded against q3
        # would silently belong to a different question.
        m = QUESTION_ID.search(heading or "")
        qid = m.group(1) if m else f"q{n}"
        if qid in seen:
            raise Bad(f"{where} repeats the id {qid!r}")
        seen.add(qid)

        question = {"id": qid, "question": "\n".join(text).strip(),
                    "options": [t for t, _ in parsed]}
        if not question["question"]:
            raise Bad(f"{where} has no text above its options")
        if answers:
            question["answer"] = answers[0]
        quiz["questions"].append(question)

    return quiz


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("source", help="the markdown quiz")
    p.add_argument("-o", "--output", help="where to write (default: alongside, as .json)")
    p.add_argument("--roll", type=int, help="how many students are on the roll")
    args = p.parse_args(argv)

    with open(args.source) as f:
        try:
            quiz = parse(f.read(), roll=args.roll)
        except Bad as e:
            sys.exit(f"{args.source}: {e}")

    out = args.output or os.path.splitext(args.source)[0] + ".json"
    with open(out, "w") as f:
        json.dump(quiz, f, indent=2, ensure_ascii=False)
        f.write("\n")

    ungraded = [q["id"] for q in quiz["questions"] if "answer" not in q]
    print(f"{out}: {len(quiz['questions'])} questions", file=sys.stderr)
    if ungraded:
        print(f"  no correct answer marked for: {', '.join(ungraded)}", file=sys.stderr)


if __name__ == "__main__":
    main()
