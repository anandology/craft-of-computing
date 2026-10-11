#! /bin/bash

set -euo pipefail

# The v14 notebook carried its images as notebook attachments, which
# JupyterLab does not show. This one links them from the course server.
NOTEBOOK=Activity-2-stringart.ipynb

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

copy_activity_notebook
