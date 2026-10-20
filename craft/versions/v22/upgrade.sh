#! /bin/bash

set -euo pipefail

NOTEBOOK=working-with-apis.ipynb

# Students write in the class notebook, so a rerun of the update must not
# replace it.
copy_class_notebook() {
    mkdir -p ~/python
    if [ -e ~/python/"$NOTEBOOK" ]; then
        echo "Keeping your ~/python/$NOTEBOOK"
    else
        echo "Copying $NOTEBOOK to ~/python"
        cp "$NOTEBOOK" ~/python/
    fi
}

# Publishes the problems fixed and added since v21.
bash ~/.craft/lib/update-problems.sh
copy_class_notebook
