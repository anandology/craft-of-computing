"""Quizzes for the Craft of Computing course.

A quiz is a JSON file in QUIZ_DIR. One URL serves the whole quiz: GET renders
the page, POST records an event. There is no database. Every event is written
as its own file, so two students answering at the same instant never contend
for anything, and every event carries the student's full answer set rather
than a delta -- a ping lost to a flaky classroom network heals itself on the
next one, and reading a student's state is "open their newest file".
"""

import datetime
import json
import os
import re
import secrets

import markdown as markdown_lib
from flask import Blueprint, abort, jsonify, render_template, request

APP_DIR = os.path.dirname(os.path.abspath(__file__))
QUIZ_DIR = os.environ.get("CRAFT_QUIZ_DIR", os.path.join(APP_DIR, "quizzes"))
DATA_DIR = os.environ.get("CRAFT_QUIZ_DATA", os.path.join(APP_DIR, "quiz-data"))

# The quiz id and the email both become path segments, so both are checked
# strictly rather than sanitised.
QUIZ_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
EMAIL_RE = re.compile(r"^[a-z0-9][a-z0-9._%+-]*@[a-z0-9-]+(\.[a-z0-9-]+)+$")

KINDS = ("start", "next", "submit")
MAX_NAME = 80

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


class QuizError(Exception):
    """A quiz file that cannot be used as written."""


# ---------------------------------------------------------------- quiz files


def render_block(text):
    return markdown_lib.markdown(text or "", extensions=["fenced_code", "tables"])


def render_inline(text):
    """Render markdown for somewhere a paragraph would look wrong, like an option."""
    html = render_block(text)
    if html.startswith("<p>") and html.endswith("</p>") and "<p>" not in html[3:]:
        html = html[3:-len("</p>")]
    return html


def load_quiz(quiz_id):
    """Read a quiz file and render its markdown.

    Returns the quiz with the answer key alongside it, never inside it, so
    that handing the quiz to a template cannot leak the key by accident.
    """
    path = os.path.join(QUIZ_DIR, quiz_id + ".json")
    if not os.path.exists(path):
        return None

    with open(path) as f:
        try:
            raw = json.load(f)
        except ValueError as e:
            raise QuizError(f"{quiz_id}.json is not valid JSON: {e}")

    questions = raw.get("questions")
    if not isinstance(questions, list) or not questions:
        raise QuizError(f"{quiz_id}.json has no questions")

    out, answers, seen = [], [], set()
    for n, q in enumerate(questions, start=1):
        where = f"question {n} of {quiz_id}.json"
        options = q.get("options")
        if not isinstance(options, list) or len(options) < 2:
            raise QuizError(f"{where} needs at least two options")

        answer = q.get("answer")
        if not isinstance(answer, int) or isinstance(answer, bool):
            raise QuizError(f"{where} has no answer (a 0-based index into options)")
        if not 0 <= answer < len(options):
            raise QuizError(f"{where} has answer {answer}, outside its {len(options)} options")

        qid = q.get("id") or f"q{n}"
        if qid in seen:
            raise QuizError(f"{where} repeats the id {qid!r}")
        seen.add(qid)

        out.append({
            "id": qid,
            "question": render_block(q.get("question")),
            "options": [render_inline(o) for o in options],
        })
        answers.append(answer)

    return {
        "id": quiz_id,
        "title": raw.get("title") or quiz_id,
        "description": render_block(raw.get("description")),
        "roll": raw.get("roll"),
        "questions": out,
        "answers": answers,
    }


def get_quiz(quiz_id):
    if not QUIZ_ID_RE.match(quiz_id):
        abort(404)
    try:
        quiz = load_quiz(quiz_id)
    except QuizError as e:
        # A broken quiz file is the author's mistake, and saying so beats a 500.
        abort(500, str(e))
    if quiz is None:
        abort(404)
    return quiz


def for_browser(quiz):
    """The quiz as the student's browser sees it, with the answer key removed."""
    return {k: v for k, v in quiz.items() if k != "answers"}


# --------------------------------------------------------------- event files


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def isoformat(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def filestamp(dt):
    """A timestamp that sorts chronologically as text, down to the microsecond.

    Seconds are not enough: a student can answer two questions inside one, and
    the whole scheme rests on a later event having a later filename.
    """
    return dt.strftime("%Y%m%dT%H%M%S%f")


def slug(email):
    return re.sub(r"[^a-z0-9._-]", "_", email.lower())


def events_dir(quiz_id):
    return os.path.join(DATA_DIR, "events", quiz_id)


def results_dir(quiz_id):
    return os.path.join(DATA_DIR, "results", quiz_id)


def write_json(path, data):
    """Write a file a concurrent reader can never catch half-written."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{secrets.token_hex(4)}.tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def write_event(quiz_id, event, at):
    """Append an event by creating a file named so that newest sorts last."""
    name = f"{filestamp(at)}-{slug(event['email'])}-{secrets.token_hex(3)}.json"
    write_json(os.path.join(events_dir(quiz_id), name), event)


def read_events(quiz_id):
    """Yield (filename, event) for every event of a quiz, oldest first."""
    directory = events_dir(quiz_id)
    if not os.path.isdir(directory):
        return
    for name in sorted(f for f in os.listdir(directory) if f.endswith(".json")):
        try:
            with open(os.path.join(directory, name)) as f:
                yield name, json.load(f)
        except (OSError, ValueError):
            continue


# ------------------------------------------------------------------ progress

# Rebuilding every student's state means opening every event file, which is
# wasteful when the dashboard polls every couple of seconds and almost nothing
# has changed. Each worker remembers what it has already read; the files
# themselves stay the only source of truth, so a restart loses nothing.
_progress = {}


def progress(quiz_id):
    state = _progress.setdefault(quiz_id, {"seen": set(), "students": {}})
    seen, students = state["seen"], state["students"]

    directory = events_dir(quiz_id)
    names = sorted(f for f in os.listdir(directory) if f.endswith(".json")) \
        if os.path.isdir(directory) else []

    for name in names:
        if name in seen:
            continue
        seen.add(name)
        try:
            with open(os.path.join(directory, name)) as f:
                event = json.load(f)
        except (OSError, ValueError):
            continue

        email = event.get("email")
        if not email:
            continue
        # Filenames start with the timestamp, so a later name is a later
        # event. Answers are only ever added and a submitted quiz stays
        # submitted, so neither count can go backwards whatever the order.
        was = students.get(email)
        answered = len(event.get("answers") or {})
        finished = event.get("kind") == "submit"
        if was:
            answered = max(answered, was["answered"])
            finished = finished or was["finished"]
            if name < was["_file"]:
                was["answered"], was["finished"] = answered, finished
                continue
        students[email] = {
            "_file": name,
            "name": event.get("name") or email,
            "email": email,
            "answered": answered,
            "finished": finished,
            "last_seen": event.get("at"),
        }

    return [{k: v for k, v in s.items() if not k.startswith("_")}
            for s in students.values()]


# -------------------------------------------------------------------- routes


@bp.get("/<quiz_id>")
def show(quiz_id):
    quiz = get_quiz(quiz_id)
    return render_template("quiz/quiz.html", quiz=for_browser(quiz))


@bp.post("/<quiz_id>")
def record(quiz_id):
    """Record one event: the student starting, moving on, or submitting."""
    quiz = get_quiz(quiz_id)
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="expected a JSON object"), 400

    kind = payload.get("kind")
    if kind not in KINDS:
        return jsonify(error=f"kind must be one of {', '.join(KINDS)}"), 400

    name = " ".join(str(payload.get("name") or "").split())[:MAX_NAME]
    email = str(payload.get("email") or "").strip().lower()
    if not name:
        return jsonify(error="name is required"), 400
    if not EMAIL_RE.match(email):
        return jsonify(error=f"invalid email: {email!r}"), 400

    answers = payload.get("answers")
    if not isinstance(answers, dict):
        return jsonify(error="answers must be an object"), 400

    by_id = {q["id"]: q for q in quiz["questions"]}
    clean = {}
    for qid, choice in answers.items():
        if qid not in by_id:
            return jsonify(error=f"no such question: {qid!r}"), 400
        if not isinstance(choice, int) or isinstance(choice, bool):
            return jsonify(error=f"answer to {qid} is not a number"), 400
        if not 0 <= choice < len(by_id[qid]["options"]):
            return jsonify(error=f"answer to {qid} is out of range"), 400
        clean[qid] = choice

    if kind == "submit" and len(clean) != len(quiz["questions"]):
        return jsonify(error="every question must be answered before submitting"), 400

    now = utcnow()
    event = {
        "quiz": quiz_id,
        "kind": kind,
        "name": name,
        "email": email,
        "answers": clean,
        # The server's clock, because the student's cannot be trusted.
        "at": isoformat(now),
    }
    index = payload.get("index")
    if isinstance(index, int) and not isinstance(index, bool):
        event["index"] = index

    write_event(quiz_id, event, now)

    if kind == "submit":
        key = dict(zip((q["id"] for q in quiz["questions"]), quiz["answers"]))
        write_json(os.path.join(results_dir(quiz_id), slug(email) + ".json"), {
            "quiz": quiz_id,
            "name": name,
            "email": email,
            "submitted_at": isoformat(now),
            "answers": clean,
            # Graded here, where the key already is, so that reading the
            # results directory later needs nothing but a JSON parser.
            "correct": {qid: clean[qid] == key[qid] for qid in clean},
            "score": sum(1 for qid in clean if clean[qid] == key[qid]),
            "out_of": len(quiz["questions"]),
        })

    return jsonify(ok=True)


@bp.get("/<quiz_id>/dashboard")
def dashboard(quiz_id):
    quiz = get_quiz(quiz_id)
    return render_template("quiz/dashboard.html", quiz=quiz)


@bp.get("/<quiz_id>/progress")
def quiz_progress(quiz_id):
    quiz = get_quiz(quiz_id)
    return jsonify(
        quiz=quiz_id,
        title=quiz["title"],
        roll=quiz["roll"],
        questions=len(quiz["questions"]),
        students=progress(quiz_id),
    )


def init_app(app):
    app.register_blueprint(bp)
