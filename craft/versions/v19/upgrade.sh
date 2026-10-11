#! /bin/bash

set -euo pipefail

NOTEBOOK=working-with-lists.ipynb

# Students write in the class notebook, so a rerun of the update must not
# replace it.
mkdir -p ~/python
if [ -e ~/python/"$NOTEBOOK" ]; then
    echo "Keeping your ~/python/$NOTEBOOK"
else
    echo "Copying $NOTEBOOK to ~/python"
    cp "$NOTEBOOK" ~/python/
fi
