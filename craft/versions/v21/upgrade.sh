#! /bin/bash

set -euo pipefail

# uv lives in ~/.local/bin on Linux, which is not on PATH in this shell.
export PATH="$HOME/.local/bin:$PATH"

install_python_packages() {
    echo "Installing requests, pytest and Pillow"
    source ~/craft/venv/bin/activate
    uv pip install requests pytest Pillow tabulate
}

# Students write in the class notebook, so a rerun of the update must not
# replace it.
copy_class_notebook() {
    local notebook=working-with-data.ipynb

    mkdir -p ~/python
    if [ -e ~/python/"$notebook" ]; then
        echo "Keeping your ~/python/$notebook"
    else
        echo "Copying $notebook to ~/python"
        cp "$notebook" ~/python/
    fi
}

install_python_packages

# Publishes the problems fixed and added since v20.
bash ~/.craft/lib/update-problems.sh
copy_class_notebook
