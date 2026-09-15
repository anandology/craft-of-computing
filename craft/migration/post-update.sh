#!/bin/bash
#
# post-update.sh -- moves an install from the old tarball releases to
# numbered versions.
#
# The old craft.sh has just replaced ~/.craft with this release, which has
# the new craft.sh in it. All that is left is making sure unzip is there,
# and letting the new craft.sh apply the versions from here on.

set -eu

if [ "$(uname -s)" = Linux ] && ! command -v unzip >/dev/null 2>&1; then
    echo ""
    echo "Installing unzip, which the new craft.sh needs."
    sudo apt-get update -qq
    sudo apt-get install -y -qq unzip
fi

echo ""
echo "Switching to the new update system..."
"$HOME/.craft/bin/craft.sh" update
