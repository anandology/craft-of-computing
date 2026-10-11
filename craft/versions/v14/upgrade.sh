#! /bin/bash

set -euo pipefail

# uv lives in ~/.local/bin on Linux, which is not on PATH in this shell.
export PATH="$HOME/.local/bin:$PATH"

NOTEBOOK=Activity-2-stringart.ipynb

install_stringart() {
    echo "Installing stringart"
    source ~/craft/venv/bin/activate
    uv pip install stringart
}

# Prints the student's username on the course server, or fails if it
# cannot be found. v13 saved it in ~/.craft/username.txt; ask the server
# again if that file is not there.
find_username() {
    local name

    if [ -s ~/.craft/username.txt ]; then
        head -n 1 ~/.craft/username.txt
        return 0
    fi

    name=$(ssh coc.apucomputing.in whoami 2>/dev/null) || return 1
    [ -n "$name" ] || return 1

    echo "$name" > ~/.craft/username.txt
    echo "$name"
}

copy_activity_notebook() {
    local username

    echo "Copying $NOTEBOOK to ~/python"

    if ! username=$(find_username); then
        # The notebook still gets copied, with the problem written where
        # the name should be, so the student sees it and can ask for help.
        username="ERROR: could not find your username on coc.apucomputing.in. Run 'craft.sh setup-ssh', then 'craft.sh update' again."
        echo "$username" >&2
    fi

    mkdir -p ~/python
    sed "s|USERNAME|$username|g" "$NOTEBOOK" > ~/python/"$NOTEBOOK"
}

install_stringart
copy_activity_notebook
