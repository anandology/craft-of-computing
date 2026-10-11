#! /bin/bash
#
# update-problems.sh -- fetch the latest problems and their files.
#
# Installed by version 16 into ~/.craft/lib. Later versions run it when
# they publish new problems:
#
#     bash ~/.craft/lib/update-problems.sh
#
# Everything is overwritten, so fixes on the server always reach you:
#
#     ~/craft/problems   the problems, which you never edit
#     ~/craft/files      a clean copy of the files the problems use
#     ~/python/files     your copy, where you run the problems

set -euo pipefail

BASE_URL="${BASE_URL:-https://coc.apucomputing.in/~anand/craft}"

ZIP=$(mktemp)
trap 'rm -f "$ZIP"' EXIT

echo "Updating problems in ~/craft/problems"
curl -fsS -o "$ZIP" "$BASE_URL/problems/all_problems.zip"
mkdir -p ~/craft/problems
unzip -q -o "$ZIP" -d ~/craft/problems

# files.zip unzips to files/.
echo "Updating files in ~/craft/files and ~/python/files"
curl -fsS -o "$ZIP" "$BASE_URL/problems/files.zip"
unzip -q -o "$ZIP" -d ~/craft

mkdir -p ~/python/files
cp -r ~/craft/files/. ~/python/files/
