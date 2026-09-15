#!/bin/bash
#
# craft.sh -- the course tool for The Craft of Computing.
#
# This script is meant to be read. If you are curious about what happens
# when you type "craft.sh update", the answer is all in this file.
#
# Commands:
#
#     craft.sh update     get the latest course updates
#     craft.sh version    print the installed version
#     craft.sh help       list all commands
#
# Every other command is a script in ~/.craft/commands: "craft.sh foo"
# runs ~/.craft/commands/foo.sh. Updates add new commands there, so this
# file does not need to change when they do.
#
# Everything the tool owns lives in ~/.craft. Each update is a numbered
# version with an upgrade.sh; they are kept in ~/.craft/versions, so you
# can read exactly what ran on your machine.

set -eu

# Where updates are published.
BASE_URL="${CRAFT_URL:-https://coc.apucomputing.in/~anand/craft}"

# Where everything lives on this machine.
CRAFT="$HOME/.craft"
VERSIONS="$CRAFT/versions"
COMMANDS="$CRAFT/commands"

# Commands are separate scripts, and they need to know these too.
export CRAFT BASE_URL

# The downloaded zip, removed when the script exits however it exits.
ZIP=""
trap 'rm -f "$ZIP"' EXIT

# ---------------------------------------------------------------- helpers

say() {
    echo "$@"
}

die() {
    echo "craft.sh: $*" >&2
    exit 1
}

# The version installed right now. A fresh install has no version file yet,
# so we call that 0 -- older than any version.
installed_version() {
    if [ -f "$CRAFT/version.txt" ]; then
        cat "$CRAFT/version.txt"
    else
        echo 0
    fi
}

# The latest version published on the server.
latest_version() {
    curl -fsS -H 'Cache-Control: no-cache' "$BASE_URL/latest-version.txt"
}

# ----------------------------------------------------------------- update

cmd_update() {
    local current latest n

    command -v unzip >/dev/null 2>&1 \
        || die "unzip is not installed -- install it with: sudo apt install unzip"

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

    # Versions are applied one at a time, in order. Each one only knows how
    # to get from the version before it, so none can be skipped.
    for n in $(seq $((current + 1)) "$latest"); do
        apply_version "$n"
    done

    say ""
    say "Now at version $latest."
}

# Download one version, run its upgrade.sh, and note it down as done. If
# upgrade.sh fails we stop here, and the next update starts again from
# this same version.
apply_version() {
    local n="$1" dir="$VERSIONS/v$1"

    say ""
    say "Applying version $n..."

    ZIP=$(mktemp -t craft-XXXXXX.zip)

    curl -fsS -o "$ZIP" "$BASE_URL/versions/v$n.zip" \
        || die "could not download version $n"

    # Start from a clean directory, so a retry does not see leftovers from
    # the attempt that failed.
    rm -rf "$dir"
    mkdir -p "$dir"
    unzip -q "$ZIP" -d "$dir" || die "the download of version $n was damaged -- try again"
    rm -f "$ZIP"

    (cd "$dir" && bash ./upgrade.sh) || {
        say ""
        say "Version $n did not finish. Run 'craft.sh update' again, and if it"
        say "keeps happening, show your instructor the output above."
        exit 1
    }

    echo "$n" > "$CRAFT/version.txt"
}

# ---------------------------------------------------------------- version

cmd_version() {
    say "craft $(installed_version)"
}

# ------------------------------------------------------------------- help

# Lists the commands built into this file, then the ones in ~/.craft/commands.
# A command script describes itself with a line like:
#
#     # summary: set up your login to the course server
#
cmd_help() {
    local file name summary

    say "usage: craft.sh <command>"
    say ""
    say "    update     get the latest course updates"
    say "    version    print the installed version"

    for file in "$COMMANDS"/*.sh; do
        [ -f "$file" ] || continue
        name=$(basename "$file" .sh)
        summary=$(sed -n 's/^# summary: *//p' "$file" | head -n 1)
        printf '    %-10s %s\n' "$name" "$summary"
    done
}

# ------------------------------------------------------------------- main

# Anything that is not built in is looked up in ~/.craft/commands. Only
# plain names are allowed, so "craft.sh ../something" cannot reach outside.
run_command() {
    local name="$1"
    shift

    case "$name" in
        ''|*[!a-z0-9-]*) ;;
        *)
            if [ -f "$COMMANDS/$name.sh" ]; then
                exec bash "$COMMANDS/$name.sh" "$@"
            fi
            ;;
    esac

    echo "craft.sh: don't know how to '$name'" >&2
    echo "" >&2
    cmd_help >&2
    exit 1
}

case "${1:-help}" in
    update)         cmd_update ;;
    version)        cmd_version ;;
    help|-h|--help) cmd_help ;;
    *)              run_command "$@" ;;
esac
