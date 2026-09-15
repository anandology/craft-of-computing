#!/bin/bash
#
# install.sh -- one-time setup for The Craft of Computing.
#
# Run it with:
#
#     curl -fsSL https://craft-of-computing.anandology.com/2026/install.sh | bash
#
# It does very little: installs the basic tools craft.sh needs, puts
# craft.sh in place, adds it to your PATH, and then hands over to
# "craft.sh update", which does the rest.

set -eu

BASE_URL="${CRAFT_URL:-https://coc.apucomputing.in/~anand/craft}"
SCRIPT="craft.sh"

CRAFT="$HOME/.craft"
MARKER_START="# >>> craft >>>"
MARKER_END="# <<< craft <<<"

# The tools craft.sh itself needs. A mac has them already.
BASIC_TOOLS="curl unzip"

# Running this with sudo would set up the course for the root user instead
# of you, and leave files you cannot edit. sudo is used only where needed.
if [ "$(id -u)" = 0 ]; then
    echo "Please run this without sudo, as yourself." >&2
    exit 1
fi

if [ "$(uname -s)" = Linux ]; then
    missing=""
    for tool in $BASIC_TOOLS; do
        command -v "$tool" >/dev/null 2>&1 || missing="$missing $tool"
    done

    if [ -n "$missing" ]; then
        echo "Installing basic tools:$missing"
        echo "This needs your password, because installing software affects the"
        echo "whole machine and not just your own files."
        sudo apt-get update -qq
        sudo apt-get install -y -qq $missing
    fi
fi

echo "Installing the craft tool..."

mkdir -p "$CRAFT/bin" "$CRAFT/commands"
curl -fsS -o "$CRAFT/bin/$SCRIPT" "$BASE_URL/$SCRIPT"
chmod +x "$CRAFT/bin/$SCRIPT"

# Add ~/.craft/bin to PATH, and load the course shell settings. The block
# is marked so that running this installer twice does not add it twice.
if ! grep -qF "$MARKER_START" "$HOME/.bashrc" 2>/dev/null; then
    echo "Adding craft to your PATH in ~/.bashrc..."
    cat >> "$HOME/.bashrc" <<EOF

$MARKER_START
export PATH="\$HOME/.craft/bin:\$PATH"
[ -f "\$HOME/.craft/profile.sh" ] && . "\$HOME/.craft/profile.sh"
$MARKER_END
EOF
fi

# Make craft.sh usable in this shell too, not just in new terminals.
export PATH="$CRAFT/bin:$PATH"

echo ""
"$CRAFT/bin/$SCRIPT" update

echo ""
echo "Done. Open a new terminal, then run:"
echo ""
echo "    $SCRIPT help"
echo ""
