# Craft of Computing app

A small Flask app behind `https://craft-of-computing.anandology.com`, doing two
jobs:

- `/api` collects ssh public keys from students.
- `/quiz` runs the in-class quizzes and shows their progress live.

Both live in one process and one deploy. There is no database anywhere in here;
everything is files in a directory.

## API endpoints

| Method | Path          | Auth | Description                            |
|--------|---------------|------|----------------------------------------|
| GET    | `/api/health` | no   | Liveness check, returns `{"ok": true}` |
| POST   | `/api/keys`   | yes  | Record an email and ssh public key     |
| GET    | `/api/keys`   | yes  | List everything recorded so far        |

Authenticated endpoints expect the token in an `Authorization` header:

    Authorization: Bearer <token>

The token is hardcoded as `API_TOKEN` at the top of `app.py`. Change it there.
Requests without it get a `401`.

## How keys are stored

Each key is a file in `ssh-keys/`, named after the student's email:

    ssh-keys/
        anand@pipal.in.key
        student@example.com.key

A file holds exactly one line — the key as submitted — so the directory can be
turned into an `authorized_keys` file directly:

    cat ssh-keys/*.key > ~/.ssh/authorized_keys

There is no database. To see who has submitted, list the directory. To remove
someone, delete their file.

Because the email becomes a filename, it is validated strictly: ordinary email
characters only, no slashes, and no leading dot (a leading dot would create a
file that `ssh-keys/*.key` silently skips). The key itself is checked to be a
real ssh public key — the base64 blob has to decode and declare the same key
type as its prefix, so `ssh-rsa <an-ed25519-blob>` is rejected.

`POST /api/keys` takes `{"email": ..., "ssh_key": ...}`. The email is
lowercased. Posting an email that already has a file replaces it, so a student
who regenerates a key can just submit again — `201` means a new key, `200` an
updated one. The write goes to a temporary file and is renamed into place, so a
concurrent `cat ssh-keys/*.key` never sees a half-written key.

## Quizzes

A quiz is one URL. `https://craft-of-computing.anandology.com/quiz/command-line`
shows `app/quizzes/command-line.json`, one question at a time, and
`/quiz/command-line/dashboard` shows who is where in it while the class is
running.

There is no login. Students type their name and email on the first screen, and
nothing stops someone typing a name that is not theirs. For a quiz you are
watching live in a room, that is the right trade.

### Writing a quiz

Drop a JSON file in `app/quizzes/`. The filename is the URL: `command-line.json`
is served at `/quiz/command-line`. Names may use lowercase letters, digits and
hyphens.

    {
      "title": "Command line quiz",
      "roll": 60,
      "description": "Ten questions on the shell commands we have used so far.",
      "questions": [
        {
          "id": "uniq-count",
          "question": "What does the last command print?\n\n```\n$ sort names.txt | uniq | wc -l\n```",
          "options": ["`1`", "`2`", "`3`", "`uniq: command not found`"],
          "answer": 1
        }
      ]
    }

- `question` and every option are **markdown**. A fenced code block inside a
  question becomes the terminal panel; an option written as `` `like this` ``
  comes out in the monospace face.
- `answer` is a **0-based** index into `options`, so the `1` above picks the
  second option. It never leaves the server: the page sent to the browser has
  no answer key in it at all.
- `id` is optional and defaults to `q1`, `q2`, ... Give a real one if you can.
  Changing a question's id after students have started orphans the answers
  already recorded against the old id.
- `roll` is optional, and only feeds the "of 60 on the roll" line on the
  dashboard.

A quiz file that cannot work — an `answer` outside its options, a question with
one option, two questions sharing an id — is reported on the page itself,
naming the question, rather than failing quietly.

`app/quizzes/command-line.json` is a complete ten-question example.

### What the student sees

One question per screen, with the question number in the URL fragment, so
`#q4` is question four. Reload, Back and Forward all behave, and answers are
kept in the browser as well as on the server — a student whose laptop sleeps
mid-quiz comes back to the question they were on.

Next stays disabled until the current question is answered, so nothing can be
skipped, and typing a larger number into the URL only gets you as far as you
had actually reached. Answers can be changed by going back, until Finish.

Keyboard: `A`–`D` to choose, `Enter` to continue.

### What gets recorded

Under `quiz-data/` (set `CRAFT_QUIZ_DATA` to move it):

    quiz-data/
        events/command-line/20260902T101533412876-meera_apu.edu.in-7f3c1a.json
        results/command-line/meera_apu.edu.in.json

An **event** is written when a student starts, each time they press Next, and
when they finish. Every event is its own file, named so that a later event
sorts after an earlier one, which is what makes forty students answering at
once safe without a lock or a database: no two writes ever touch the same file.
Each file is written under a temporary name and renamed into place, so a reader
never catches one half-written.

Every event carries the student's **whole answer set**, not just the newest
answer. A ping lost to classroom wifi therefore costs nothing — the next one
says everything the lost one would have. It also means a student's state is
their newest file, with no merging.

    {
      "quiz": "command-line",
      "kind": "next",
      "name": "Meera Nair",
      "email": "meera@apu.edu.in",
      "index": 3,
      "answers": {"uniq-count": 1, "grep": 1, "cd-dotdot": 0, "redirect-overwrite": 1},
      "at": "2026-09-02T10:15:33Z"
    }

The `at` is the server's clock, not the student's. Because an event is written
each time a question is left, the gap between consecutive files is how long
that student spent on that question.

A **result** is written on Finish: one file per student, graded, since the
answer key is right there:

    {
      "name": "Meera Nair",
      "email": "meera@apu.edu.in",
      "submitted_at": "2026-09-02T10:22:07Z",
      "answers": {"uniq-count": 1, ...},
      "correct": {"uniq-count": true, ...},
      "score": 8,
      "out_of": 10
    }

Scores, highest first:

    cd quiz-data/results/command-line
    python3 -c '
    import glob, json
    rows = [json.load(open(f)) for f in glob.glob("*.json")]
    for r in sorted(rows, key=lambda r: -r["score"]):
        print(r["score"], r["out_of"], r["name"], r["email"], sep="\t")
    '

Which questions the class found hard:

    python3 -c '
    import collections, glob, json
    wrong = collections.Counter()
    for f in glob.glob("*.json"):
        for qid, right in json.load(open(f))["correct"].items():
            if not right: wrong[qid] += 1
    for qid, n in wrong.most_common(): print(n, qid)
    '

### The dashboard

`/quiz/<name>/dashboard` polls every two seconds and shows how many have
started, how many have finished, how many have not moved in three minutes, how
far the class has got through each question, and a row per student. Finished
students are at the top, then whoever is active, then whoever has gone quiet —
so the people to walk over to are at the bottom of the list.

It is not protected. Anyone with the URL can open it, students included. It
shows names, emails and progress, never answers or scores.

If the server goes away mid-class the page keeps the last picture it had and
says how stale it is, rather than blanking.

### Configuration

| Variable            | Default          | What it does                        |
|---------------------|------------------|-------------------------------------|
| `CRAFT_QUIZ_DIR`    | `app/quizzes`    | Where the quiz JSON files are read  |
| `CRAFT_QUIZ_DATA`   | `app/quiz-data`  | Where events and results are written |

## Running locally

    uv run python app/app.py

That serves on `http://127.0.0.1:8081` and writes to `app/ssh-keys/`. Set
`CRAFT_KEYS_DIR` to put the keys elsewhere.

Try it:

    TOKEN=craft-2026-8f3a91c47d5e

    curl -X POST http://127.0.0.1:8081/api/keys \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"student@example.com\", \"ssh_key\": \"$(cat ~/.ssh/id_ed25519.pub)\"}"

    curl http://127.0.0.1:8081/api/keys -H "Authorization: Bearer $TOKEN"

## Deploying

Copy the app to the server and install its dependencies:

    rsync -av --exclude ssh-keys --exclude __pycache__ app/ \
        anandology.com:/opt/craft-of-computing-api/

    ssh anandology.com
    cd /opt/craft-of-computing-api
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt

Keep the keys and the quiz data outside the app directory so a deploy can never
overwrite them:

    sudo mkdir -p /var/lib/craft-of-computing/ssh-keys
    sudo mkdir -p /var/lib/craft-of-computing/quiz-data
    sudo chown -R www-data:www-data /var/lib/craft-of-computing

### systemd unit

`/etc/systemd/system/craft-api.service`:

    [Unit]
    Description=Craft of Computing API
    After=network.target

    [Service]
    User=www-data
    Group=www-data
    WorkingDirectory=/opt/craft-of-computing-api
    Environment=CRAFT_KEYS_DIR=/var/lib/craft-of-computing/ssh-keys
    Environment=CRAFT_QUIZ_DATA=/var/lib/craft-of-computing/quiz-data
    ExecStart=/opt/craft-of-computing-api/.venv/bin/gunicorn \
        --workers 2 --bind 127.0.0.1:8081 app:app
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target

Then:

    sudo systemctl daemon-reload
    sudo systemctl enable --now craft-api
    curl http://127.0.0.1:8081/api/health

### nginx

The static site is already served from
`/var/www/craft-of-computing.anandology.com/2026`. Add an `/api` location to
that same server block so the API and the quizzes live on the same domain:

    server {
        server_name craft-of-computing.anandology.com;

        root /var/www/craft-of-computing.anandology.com/2026;

        location ~ ^/(api|quiz) {
            proxy_pass http://127.0.0.1:8081;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # ... existing listen / ssl_certificate directives ...
    }

There is no trailing slash on `proxy_pass`, so nginx passes the path through
unchanged and the app sees `/api/keys` and `/quiz/command-line` as its own
routes.

Reload and check:

    sudo nginx -t && sudo systemctl reload nginx
    curl https://craft-of-computing.anandology.com/api/health
    curl -sI https://craft-of-computing.anandology.com/quiz/command-line | head -1

## Collecting the answers

    rsync -av anandology.com:/var/lib/craft-of-computing/quiz-data/ ./quiz-data/

## Collecting the keys

On the server:

    ls /var/lib/craft-of-computing/ssh-keys
    cat /var/lib/craft-of-computing/ssh-keys/*.key >> ~/.ssh/authorized_keys

Or pull them down to look at locally:

    rsync -av anandology.com:/var/lib/craft-of-computing/ssh-keys/ ./ssh-keys/
