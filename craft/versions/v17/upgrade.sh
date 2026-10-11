#! /bin/bash

set -euo pipefail

NOTEBOOK=Activity-3.ipynb

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

# Students write in the class notebook, so a rerun of the update must not
# replace it.
copy_class_notebook() {
    local notebook=working-with-files.ipynb

    mkdir -p ~/python
    if [ -e ~/python/"$notebook" ]; then
        echo "Keeping your ~/python/$notebook"
    else
        echo "Copying $notebook to ~/python"
        cp "$notebook" ~/python/
    fi
}

# The activity uses problems added after v16, like cat and reverse-lines.
bash ~/.craft/lib/update-problems.sh
copy_activity_notebook
copy_class_notebook
