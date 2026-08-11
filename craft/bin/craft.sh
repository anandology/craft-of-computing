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

    if curl -fsS -m 10 -H 'Cache-Control: no-cache' "$BASE_URL/version.txt" >/dev/null 2>&1; then
        say "reachable: yes, latest release is $(latest_version)"
    else
        say "reachable: NO -- check your network"
    fi
}

# ------------------------------------------------------------------- main

cmd_help() {
    say "usage: craft.sh <command>"
    say ""
    say "    update     get the latest course files"
    say "    version    print the installed version"
    say "    doctor     print setup details, useful when asking for help"
}

case "${1:-help}" in
    update)  cmd_update ;;
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
