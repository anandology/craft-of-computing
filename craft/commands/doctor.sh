#!/bin/bash
#
# summary: print setup details, useful when asking for help
#
# craft.sh doctor
#
# Prints what someone helping you would want to know. When something is
# wrong, run this and share the output.

set -eu

CRAFT="${CRAFT:-$HOME/.craft}"
BASE_URL="${BASE_URL:-https://coc.apucomputing.in/~anand/craft}"

SSH_HOST="${CRAFT_SSH_HOST:-coc.apucomputing.in}"
SSH_KEY="$HOME/.ssh/id_ed25519"
SSH_CONFIG="$HOME/.ssh/config"
SSH_BLOCK_START="# >>> craft >>>"
SSH_BLOCK_END="# <<< craft <<<"

say() {
    echo "$@"
}

# The login name in the part of ~/.ssh/config that setup-ssh wrote. Only
# that part is looked at, so a Host you set up yourself is not reported.
config_username() {
    awk -v start="$SSH_BLOCK_START" -v end="$SSH_BLOCK_END" '
        $0 == start { inside = 1 }
        inside && $1 == "User" { print $2 }
        $0 == end   { inside = 0 }
    ' "$SSH_CONFIG"
}

main() {
    local latest

    say "version:   $(cat "$CRAFT/version.txt" 2>/dev/null || echo 0)"
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
        *)                say "on PATH:   NO -- open a new terminal, or run: curl -fsSL https://craft-of-computing.anandology.com/2026/install.sh | bash" ;;
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

    if latest=$(curl -fsS -m 10 -H 'Cache-Control: no-cache' "$BASE_URL/latest-version.txt" 2>/dev/null); then
        say "reachable: yes, latest version is $latest"
    else
        say "reachable: NO -- check your network"
    fi
}

main "$@"
