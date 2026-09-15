#!/bin/bash
#
# summary: set up your login to the course server
#
# craft.sh setup-ssh [email]
#
# Sets up everything needed to log in to the course server:
#
#   1. an SSH key, which is how the server knows it is you
#   2. telling the server about the public half of that key
#   3. a few lines in ~/.ssh/config, so that "ssh HOST" is all you type
#
# Running it a second time is harmless. Each step notices what is already
# done and leaves it alone.

set -eu

# The machine you log in to for the course.
SSH_HOST="${CRAFT_SSH_HOST:-coc.apucomputing.in}"

# The course API, which is where your public key is sent. The token says
# which class you are from; it is the same for everyone here, and is not
# a password.
API_URL="${CRAFT_API_URL:-https://craft-of-computing.anandology.com/api}"
API_TOKEN="${CRAFT_API_TOKEN:-craft-2026-8f3a91c47d5e}"

# Your college email ends with this, and your login name on the server is
# the rest of it, with dots turned into dashes:
#
#     firstname.lastname26_ug@apu.edu.in  ->  firstname-lastname
#
SSH_SUFFIX="26_ug@apu.edu.in"

SSH_KEY="$HOME/.ssh/id_ed25519"
SSH_CONFIG="$HOME/.ssh/config"

# Where we note down what we last told the server, so that running the
# command again does not ask it to do the same work twice.
SSH_STAMP="$HOME/.ssh/craft-registered"

# The lines around the part of ~/.ssh/config that this tool owns. Anything
# outside them is yours, and is left alone.
SSH_BLOCK_START="# >>> craft >>>"
SSH_BLOCK_END="# <<< craft <<<"

say() {
    echo "$@"
}

die() {
    echo "craft.sh: $*" >&2
    exit 1
}

main() {
    local email username

    email="${1:-}"
    if [ -z "$email" ]; then
        printf 'Your APU email: '
        read -r email
    fi

    # Addresses are not case sensitive, and the server keeps them in lower
    # case, so a capital letter here should not turn into a different name.
    email=$(printf '%s' "$email" | tr '[:upper:]' '[:lower:]')

    # A typo here would register the wrong name, so we check the shape of
    # the address before doing anything with it.
    case "$email" in
        ?*"$SSH_SUFFIX") ;;
        *) die "'$email' is not an APU email -- it should look like firstname.lastname$SSH_SUFFIX" ;;
    esac

    username=$(printf '%s' "${email%"$SSH_SUFFIX"}" | tr '.' '-')

    # ssh refuses to use a key that other people on the machine can read,
    # so the directory has to be private before we put a key in it.
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"

    make_ssh_key "$email"
    register_ssh_key "$email" "$username"
    write_ssh_config "$username"

    say ""
    say "You can now run:"
    say ""
    say "    ssh $SSH_HOST"
}

# A key is a pair of files: id_ed25519 is the private half, which never
# leaves this machine, and id_ed25519.pub is the public half, which is
# what the server gets. There is no passphrase, so ssh does not stop to
# ask for one.
make_ssh_key() {
    local email="$1"

    if [ -f "$SSH_KEY" ]; then
        say "Using the SSH key you already have at $SSH_KEY."
        return 0
    fi

    ssh-keygen -t ed25519 -N '' -C "$email" -f "$SSH_KEY" >/dev/null \
        || die "could not create an SSH key"

    say "Created a new SSH key at $SSH_KEY."
}

# The server only needs to hear about a key once. We write down what we
# sent, and skip the trip if nothing has changed since.
register_ssh_key() {
    local email="$1" username="$2" stamp response

    stamp="$username $(cut -d ' ' -f 2 "$SSH_KEY.pub")"

    if [ -f "$SSH_STAMP" ] && [ "$(cat "$SSH_STAMP")" = "$stamp" ]; then
        say "Your key is already registered as $username."
        return 0
    fi

    # The API takes JSON. Nothing here needs escaping: the address has
    # already been checked, and a public key is only letters, digits and
    # a little punctuation, all on one line.
    if ! response=$(printf '{"email": "%s", "username": "%s", "ssh_key": "%s"}' \
            "$email" "$username" "$(cat "$SSH_KEY.pub")" \
        | curl -fsS "$API_URL/keys" \
            -H "Authorization: Bearer $API_TOKEN" \
            -H "Content-Type: application/json" \
            --data-binary @- 2>&1)
    then
        die "could not register your key with $API_URL/keys: $response"
    fi

    printf '%s\n' "$stamp" > "$SSH_STAMP"

    say "Registered your key as $username."
}

# ~/.ssh/config is where ssh looks up the details of a host. We keep our
# few lines between two markers, so that running this again replaces them
# instead of adding a second copy -- and so that anything you write there
# yourself is never touched.
write_ssh_config() {
    local username="$1" tmp

    tmp=$(mktemp "$HOME/.ssh/config.XXXXXX")

    if [ -f "$SSH_CONFIG" ]; then
        awk -v start="$SSH_BLOCK_START" -v end="$SSH_BLOCK_END" '
            $0 == start { skipping = 1 }
            !skipping   { print }
            $0 == end   { skipping = 0 }
        ' "$SSH_CONFIG" > "$tmp"
    fi

    cat >> "$tmp" <<EOF
$SSH_BLOCK_START
Host $SSH_HOST
    HostName $SSH_HOST
    User $username
    IdentityFile $SSH_KEY
$SSH_BLOCK_END
EOF

    # Move the finished file into place in one step, so the config is
    # never half-written, even if something goes wrong above.
    chmod 600 "$tmp"
    mv "$tmp" "$SSH_CONFIG"

    say "Added $SSH_HOST to $SSH_CONFIG."
}

main "$@"
