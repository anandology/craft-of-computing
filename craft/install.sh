#!/bin/bash
#
# install.sh -- one-time setup for The Craft of Computing.
#
# Run it with:
#
#     curl -fsSL https://craft-of-computing.anandology.com/2026/install.sh | bash
#
# It does very little: puts craft.sh in place, adds it to your PATH, and
# then hands over to "craft.sh update", which fetches the actual course
# files. Everything after this is done by craft.sh.

set -eu

BASE_URL="${CRAFT_URL:-https://craft-of-computing.anandology.com/2026}"
CRAFT="$HOME/.craft"
MARKER_START="# >>> craft >>>"
MARKER_END="# <<< craft <<<"

# Running this with sudo would set up the course for the root user instead
# of you, and leave files you cannot edit. Nothing here needs root.
if [ "$(id -u)" = 0 ]; then
    echo "Please run this without sudo, as yourself." >&2
    exit 1
fi

command -v curl >/dev/null || { echo "install.sh: curl is required." >&2; exit 1; }

echo "Installing the craft tool..."

mkdir -p "$CRAFT/bin"
curl -fsS -o "$CRAFT/bin/craft.sh" "$BASE_URL/craft.sh"
chmod +x "$CRAFT/bin/craft.sh"

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
"$CRAFT/bin/craft.sh" update

echo ""
echo "Done. Open a new terminal, then run:"
echo ""
echo "    craft.sh version"
echo ""
