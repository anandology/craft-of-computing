#!/bin/bash
#
# post-update.sh -- decides what goes into the student's home directory.
#
# craft.sh runs this at the end of every update, after the new release is
# in place. It is part of the release, so each release can do whatever that
# week needs -- copy new material, fix a file that shipped wrong, nothing
# at all.
#
# Two rules to keep in mind while editing this file:
#
#   1. It runs on EVERY update, not once. Everything here must be safe to
#      run again.
#   2. It runs on every student's machine at the same time, and there is no
#      undo. Be careful with rm.
#
# Arguments:
#   $1  version being upgraded from (0 on a fresh install)
#   $2  version being upgraded to
#
# Environment:
#   CRAFT_PREV  the previous release's directory, still on disk, so this
#               script can compare against what it replaced. Empty on a
#               fresh install.

set -eu

from="$1"
to="$2"

CRAFT="$HOME/.craft"
CONTENT="$CRAFT/content"

[ -d "$CONTENT" ] || exit 0

# Copy course material into the home directory, so content/week2 shows up
# as ~/week2. The -n flag means "no clobber": a file that is already there
# is left alone, so nothing a student has written is ever overwritten.
cp -rn "$CONTENT"/. "$HOME"/ 2>/dev/null || true

# If this release changed a file that a student already has, say so. Their
# copy is kept -- but they get told, instead of quietly working from an old
# version. Silent on a fresh install, and silent for files nobody edited.
if [ -n "${CRAFT_PREV:-}" ] && [ -d "${CRAFT_PREV:-}/content" ]; then
    changed=$(cd "$CONTENT" && find . -type f | sed 's|^\./||' | while read -r file; do
        old="$CRAFT_PREV/content/$file"
        [ -f "$old" ] || continue                       # newly added, was just copied
        cmp -s "$old" "$CONTENT/$file" && continue      # unchanged this release
        cmp -s "$CONTENT/$file" "$HOME/$file" && continue  # student has the new one already
        [ -f "$HOME/$file" ] && echo "$file"
    done)

    if [ -n "$changed" ]; then
        echo ""
        echo "These files changed in this release, but you already have your own copy,"
        echo "so yours was left alone. The new versions are under ~/.craft/content/ :"
        echo ""
        echo "$changed" | sed 's|^|    |'
    fi
fi

# Version-specific fixes go here. Because $from is passed in, a fix can be
# written to run only for the students who need it, for example:
#
#     if [ "$from" -lt 3 ] && [ "$from" -gt 0 ]; then
#         rm -f "$HOME/week1/typo.txt"    # shipped by mistake in version 2
#     fi

: "$to"  # not used yet; here so the argument is documented and available
