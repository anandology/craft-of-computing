#! /bin/bash

set -euo pipefail

FILE=accounts.py

# Students write their code in ~/rajdhani, so a rerun of the update must not
# replace a file that is already there.
copy_accounts() {
    if [ ! -d ~/rajdhani ]; then
        echo "No ~/rajdhani found, skipping $FILE"
    elif [ -e ~/rajdhani/"$FILE" ]; then
        echo "Keeping your ~/rajdhani/$FILE"
    else
        echo "Copying $FILE to ~/rajdhani"
        cp "$FILE" ~/rajdhani/
    fi
}

# checks.json was shipped in the v23 zip by mistake. It is written on the
# server and submit.sh leaves it out, so the student copy is unused.
remove_checks_json() {
    if [ -e ~/rajdhani/checks.json ]; then
        echo "Removing ~/rajdhani/checks.json"
        rm -f ~/rajdhani/checks.json
    fi
}

copy_accounts
remove_checks_json
