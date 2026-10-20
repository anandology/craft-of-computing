#! /bin/bash

set -euo pipefail

# uv lives in ~/.local/bin on Linux, which is not on PATH in this shell.
export PATH="$HOME/.local/bin:$PATH"

install_python_packages() {
    echo "Installing geopy"
    source ~/craft/venv/bin/activate
    uv pip install geopy
}

# Students write their code in ~/rajdhani, so a rerun of the update must not
# replace it.
unzip_rajdhani() {
    if [ -e ~/rajdhani ]; then
        echo "Keeping your ~/rajdhani"
    else
        echo "Unzipping rajdhani to ~/rajdhani"
        unzip -q rajdhani.zip -d ~
    fi
}

NOTEBOOK=writing-modules.ipynb

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

install_python_packages
unzip_rajdhani
copy_class_notebook
