#!/bin/bash
#
# post-update.sh -- script run after every craft.sh update
#
# Updates the files in ~/craft/
#

set -eu

[ -d ~/.craft/content ] || exit 0

cp -r ~/.craft/content/craft ~/

