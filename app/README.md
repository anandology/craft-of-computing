# Craft of Computing API

A small Flask app serving the course API at
`https://craft-of-computing.anandology.com/api`.

Right now it collects ssh public keys from students. More endpoints will be
added under `/api` as the course needs them.

## Endpoints

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

## Running locally

    uv run --with flask python app/app.py

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

Keep the keys outside the app directory so a deploy can never overwrite them:

    sudo mkdir -p /var/lib/craft-of-computing/ssh-keys
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
that same server block so the API lives on the same domain:

    server {
        server_name craft-of-computing.anandology.com;

        root /var/www/craft-of-computing.anandology.com/2026;

        location /api {
            proxy_pass http://127.0.0.1:8081;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # ... existing listen / ssl_certificate directives ...
    }

There is no trailing slash on `proxy_pass`, so nginx passes the path through
unchanged and the app sees `/api/keys` as its own route.

Reload and check:

    sudo nginx -t && sudo systemctl reload nginx
    curl https://craft-of-computing.anandology.com/api/health

## Collecting the keys

On the server:

    ls /var/lib/craft-of-computing/ssh-keys
    cat /var/lib/craft-of-computing/ssh-keys/*.key >> ~/.ssh/authorized_keys

Or pull them down to look at locally:

    rsync -av anandology.com:/var/lib/craft-of-computing/ssh-keys/ ./ssh-keys/
