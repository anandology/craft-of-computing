"""Keep authorized_keys in step with the keys students have submitted.

Runs on the course server, as root. Every second it asks the API for the
keys collected so far and writes each one into that student's
~/.ssh/authorized_keys. A key that is already in place is left alone, so
the common case touches no files at all.

    sudo CRAFT_API_TOKEN=... python3 sync_keys.py

    --once      go round the loop a single time, then stop

A student's login name comes from their email, the same way craft.sh
works it out:

    firstname.lastname26_ug@apu.edu.in  ->  firstname-lastname

Students whose account does not exist yet are skipped, and named once in
the log. Create the account and the next pass picks them up.
"""

import json
import os
import pwd
import sys
import time
import urllib.error
import urllib.request

API_URL = os.environ.get("CRAFT_API_URL", "https://craft-of-computing.anandology.com/api")
API_TOKEN = os.environ.get("CRAFT_API_TOKEN", "craft-2026-8f3a91c47d5e")

DELAY = 1

EMAIL_SUFFIX = "26_ug@apu.edu.in"

# The lines around the part of authorized_keys that this script owns.
# ssh ignores lines starting with #, so the markers are safe to leave in
# the file, and anything outside them is the student's own.
BLOCK_START = "# >>> craft >>>"
BLOCK_END = "# <<< craft <<<"


def log(message):
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    # Unbuffered, so the output shows up in the journal as it happens
    # rather than in bursts when a buffer happens to fill.
    print(f"{stamp} {message}", flush=True)


def username_for(email):
    """The login name for a course email, or None if it is not one."""
    if not email.endswith(EMAIL_SUFFIX):
        return None

    local = email[: -len(EMAIL_SUFFIX)]
    if not local:
        return None

    return local.replace(".", "-")


def fetch_keys():
    request = urllib.request.Request(
        f"{API_URL}/keys", headers={"Authorization": f"Bearer {API_TOKEN}"}
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)["items"]


def block_for(ssh_key):
    return f"{BLOCK_START}\n{ssh_key}\n{BLOCK_END}\n"


def without_block(text):
    """Everything in authorized_keys except the part this script wrote."""
    kept = []
    skipping = False

    for line in text.splitlines(keepends=True):
        if line.strip() == BLOCK_START:
            skipping = True
        elif line.strip() == BLOCK_END:
            skipping = False
        elif not skipping:
            kept.append(line)

    return "".join(kept)


def install_key(username, ssh_key):
    """Put ssh_key in the user's authorized_keys. True if anything changed."""
    account = pwd.getpwnam(username)
    ssh_dir = os.path.join(account.pw_dir, ".ssh")
    path = os.path.join(ssh_dir, "authorized_keys")

    try:
        with open(path) as f:
            current = f.read()
    except FileNotFoundError:
        current = ""

    wanted = without_block(current) + block_for(ssh_key)
    if wanted == current:
        return False

    # ssh refuses to use a key from a directory or file that others can
    # write to, so both have to belong to the student and be private.
    os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
    os.chown(ssh_dir, account.pw_uid, account.pw_gid)
    os.chmod(ssh_dir, 0o700)

    # Write beside the real file and rename, so a login happening right
    # now never reads a half-written authorized_keys.
    tmp = path + ".craft-tmp"
    with open(tmp, "w") as f:
        f.write(wanted)
    os.chown(tmp, account.pw_uid, account.pw_gid)
    os.chmod(tmp, 0o600)
    os.replace(tmp, path)

    return True


def sync(skipped):
    """One pass over everything the API knows about."""
    for item in fetch_keys():
        email = item["email"]
        username = username_for(email)

        if username is None:
            if email not in skipped:
                skipped.add(email)
                log(f"skipping {email}: not a course address")
            continue

        try:
            changed = install_key(username, item["ssh_key"])
        except KeyError:
            # No such account yet. Say so once, and keep looking: the
            # account may be created while this is running.
            if username not in skipped:
                skipped.add(username)
                log(f"skipping {email}: no account named {username}")
            continue
        except OSError as e:
            log(f"could not update {username}: {e}")
            continue

        # Someone who was skipped and is now working should be reported
        # again if they ever break.
        skipped.discard(username)

        if changed:
            log(f"updated authorized_keys for {username} ({email})")


def main():
    once = "--once" in sys.argv[1:]

    if os.geteuid() != 0:
        log("warning: not running as root -- writing to other users' home directories will fail")

    log(f"watching {API_URL}/keys")

    # Names already reported, so a student who cannot be set up does not
    # fill the log with the same line every second.
    skipped = set()

    while True:
        try:
            sync(skipped)
        except urllib.error.HTTPError as e:
            log(f"api returned {e.code} {e.reason}")
        except Exception as e:
            log(f"could not reach the api: {e}")

        if once:
            return

        time.sleep(DELAY)


if __name__ == "__main__":
    main()
