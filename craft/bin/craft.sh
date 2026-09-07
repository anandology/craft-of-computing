#!/bin/bash
#
# craft.sh -- the course tool for The Craft of Computing.
#
# This script is meant to be read. If you are curious about what happens
# when you type "craft.sh update", the answer is all in this file.
#
# Commands:
#
#     craft.sh update     get the latest course files
#     craft.sh setup-ssh  set up your login to the course server
#     craft.sh version    print the installed version
#     craft.sh doctor     print setup details, useful when asking for help
#
# Everything the tool owns lives in ~/.craft, and that directory is exactly
# the contents of the release tarball -- nothing else is kept there. If it
# ever gets into a bad state, deleting it and installing again is safe.

set -eu

# Where releases are published.
BASE_URL="${CRAFT_URL:-https://craft-of-computing.anandology.com/2026/dist}"

# Where everything lives on this machine.
CRAFT="$HOME/.craft"
NEW="$HOME/.craft.new"
OLD="$HOME/.craft.old"

# The machine you log in to for the course.
SSH_HOST="${CRAFT_SSH_HOST:-coc.apucomputing.in}"

# The course API, which is where "setup-ssh" sends your public key. The
# token says which class you are from; it is the same for everyone here,
# and is not a password.
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

# The downloaded tarball, removed when the script exits however it exits.
TARBALL=""
trap 'rm -f "$TARBALL"' EXIT

# ---------------------------------------------------------------- helpers

say() {
    echo "$@"
}

die() {
    echo "craft.sh: $*" >&2
    exit 1
}

# The version installed right now. A fresh install has no version file yet,
# so we call that 0 -- older than any release.
installed_version() {
    if [ -f "$CRAFT/version.txt" ]; then
        cat "$CRAFT/version.txt"
    else
        echo 0
    fi
}

# The latest version published on the server.
latest_version() {
    curl -fsS -H 'Cache-Control: no-cache' "$BASE_URL/version.txt"
}

# ----------------------------------------------------------------- update

cmd_update() {
    local current latest

    current=$(installed_version)

    say "Checking for updates..."
    latest=$(latest_version) || die "could not reach $BASE_URL -- are you online?"

    # The server should send a plain integer. Anything else means we are
    # talking to the wrong thing, and we should not act on it.
    case "$latest" in
        ''|*[!0-9]*) die "server sent a bad version: '$latest'" ;;
    esac

    if [ "$latest" -le "$current" ]; then
        say "Already up to date (version $current)."
        return 0
    fi

    say "Updating from version $current to $latest..."

    # Download and unpack into a directory of its own. Nothing that is
    # already installed is touched until we have the whole thing.
    rm -rf "$NEW"
    mkdir -p "$NEW"

    TARBALL=$(mktemp -t craft-XXXXXX.tar.gz)

    curl -fsS -o "$TARBALL" "$BASE_URL/craft-$latest.tar.gz" \
        || die "could not download version $latest"

    # gzip carries a checksum, so a truncated or corrupt download fails
    # here rather than installing something broken.
    tar -xzf "$TARBALL" -C "$NEW" || die "the download was damaged -- try again"

    # Swap the new version into place. This is a rename, so there is no
    # moment where ~/.craft is half-written.
    rm -rf "$OLD"
    if [ -d "$CRAFT" ]; then
        mv "$CRAFT" "$OLD"
    fi
    mv "$NEW" "$CRAFT"

    install_packages

    run_post_update "$current" "$latest"

    rm -rf "$OLD"

    say ""
    say "Now at version $latest."
}

# Each release decides for itself what to put in the home directory. That
# logic lives in post-update.sh, inside the release, so it can differ from
# one week to the next.
run_post_update() {
    local from="$1" to="$2"

    [ -f "$CRAFT/post-update.sh" ] || return 0

    # The previous release is still on disk at this point, so post-update.sh
    # can compare against what it replaced.
    CRAFT_PREV="$OLD" bash "$CRAFT/post-update.sh" "$from" "$to" || {
        say ""
        say "Warning: the setup step for this release did not finish cleanly."
        say "Your files are at version $to. Try 'craft.sh update' again, and"
        say "if it keeps happening, show your teacher the output above."
    }
}

# --------------------------------------------------------------- packages

# The course expects a handful of command line tools to be present. The
# lists live in the release, so they can grow from one week to the next
# without changing this script: packages.txt for Linux, mac-packages.txt
# for a mac, because the two systems name the same tools differently.
#
# How you install them also depends on the machine, so there is one
# function per system and this picks the right one.
install_packages() {
    case "$(uname -s)" in
        Linux)  install_packages_linux ;;
        Darwin) install_packages_mac ;;
        *)      say "Skipping packages -- don't know how to install them on $(uname -s)." ;;
    esac
}

# The names in one of those files, one per line, with comments and blank
# lines dropped. A file that is not in this release gives nothing back.
package_list() {
    local file="$1"

    [ -f "$file" ] || return 0

    sed -e 's/#.*//' -e '/^[[:space:]]*$/d' "$file"
}

install_packages_linux() {
    local packages
    packages=$(package_list "$CRAFT/packages.txt")

    [ -n "$packages" ] || return 0

    say ""
    say "Installing packages: $(echo $packages)"
    say "This needs your password, because installing software affects the"
    say "whole machine and not just your own files."

    sudo apt-get update -qq \
        && sudo apt-get install -y -qq $packages \
        || say "Warning: some packages could not be installed."
}

# On a mac the tools come from Homebrew, which installs into a place you
# own, so there is no password to type here.
install_packages_mac() {
    local packages

    packages=$(package_list "$CRAFT/mac-packages.txt")

    [ -n "$packages" ] || return 0

    if ! command -v brew >/dev/null 2>&1; then
        say ""
        say "Skipping packages -- Homebrew is not installed."
        say "Install it from https://brew.sh and run 'craft.sh update' again."
        return 0
    fi

    say ""
    say "Installing packages: $(echo $packages)"

    HOMEBREW_NO_ASK=1 brew install $packages \
        || say "Warning: some packages could not be installed."
}

# --------------------------------------------------------------- setup-ssh

# Sets up everything needed to log in to the course server:
#
#   1. an SSH key, which is how the server knows it is you
#   2. telling the server about the public half of that key
#   3. a few lines in ~/.ssh/config, so that "ssh HOST" is all you type
#
# Running it a second time is harmless. Each step notices what is already
# done and leaves it alone.
cmd_setup_ssh() {
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

# ---------------------------------------------------------------- version

cmd_version() {
    say "craft $(installed_version)"
}

# ----------------------------------------------------------------- doctor

# Prints what someone helping you would want to know. When something is
# wrong, run this and share the output.
cmd_doctor() {
    say "version:   $(installed_version)"
    say "craft dir: $CRAFT"
    say "server:    $BASE_URL"

    if [ -r /etc/os-release ]; then
        say "system:    $(. /etc/os-release && echo "$PRETTY_NAME")"
    fi

    if grep -qi microsoft /proc/version 2>/dev/null; then
        say "wsl:       yes"
    fi

    case ":$PATH:" in
        *":$CRAFT/bin:"*) say "on PATH:   yes" ;;
        *)                say "on PATH:   NO -- open a new terminal, or run the install command again" ;;
    esac

    if [ -f "$SSH_KEY" ]; then
        say "ssh key:   yes, at $SSH_KEY"
    else
        say "ssh key:   no -- run 'craft.sh setup-ssh'"
    fi

    if grep -qF "$SSH_BLOCK_START" "$SSH_CONFIG" 2>/dev/null; then
        say "ssh host:  $SSH_HOST, as $(config_username)"
    else
        say "ssh host:  not set up -- run 'craft.sh setup-ssh'"
    fi

    if curl -fsS -m 10 -H 'Cache-Control: no-cache' "$BASE_URL/version.txt" >/dev/null 2>&1; then
        say "reachable: yes, latest release is $(latest_version)"
    else
        say "reachable: NO -- check your network"
    fi
}

# The login name in the part of ~/.ssh/config that this tool wrote. Only
# that part is looked at, so a Host you set up yourself is not reported.
config_username() {
    awk -v start="$SSH_BLOCK_START" -v end="$SSH_BLOCK_END" '
        $0 == start { inside = 1 }
        inside && $1 == "User" { print $2 }
        $0 == end   { inside = 0 }
    ' "$SSH_CONFIG"
}

# ------------------------------------------------------------------- main

cmd_help() {
    say "usage: craft.sh <command>"
    say ""
    say "    update     get the latest course files"
    say "    setup-ssh  set up your login to the course server"
    say "    version    print the installed version"
    say "    doctor     print setup details, useful when asking for help"
}

case "${1:-help}" in
    update)  cmd_update ;;
    setup-ssh) cmd_setup_ssh "${2:-}" ;;
    version) cmd_version ;;
    doctor)  cmd_doctor ;;
    help|-h|--help) cmd_help ;;
    *)
        echo "craft.sh: don't know how to '$1'" >&2
        echo "" >&2
        cmd_help >&2
        exit 1
        ;;
esac
