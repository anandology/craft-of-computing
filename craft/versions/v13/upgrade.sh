#! /bin/bash

set -euo pipefail

# v12 installed uv into ~/.local/bin on Linux. When v12 and v13 run in the
# same update, that is not on PATH yet.
export PATH="$HOME/.local/bin:$PATH"

find_username() {
    echo "finding your username on coc.apucomputing.in"
    username=$(ssh coc.apucomputing.in whoami)
    echo $username > ~/.craft/username.txt
}

install_sigma() {
    echo "Installing magic functions for the course"
    source ~/craft/venv/bin/activate

    # --reinstall-package makes a retry replace sigma even though the
    # version number has not changed.
    uv pip install --reinstall-package sigma ./sigma-0.1.0-py3-none-any.whl
}

install_jupyterlab_execute_time() {
    # Shows how long each notebook cell took to run.
    echo "Installing jupyterlab_execute_time"
    source ~/craft/venv/bin/activate
    uv pip install jupyterlab_execute_time
}

setup_ipython_startup() {
    # Registers the sigma magics in every IPython kernel.
    echo "Setting up IPython startup"
    mkdir -p ~/.ipython/profile_default/startup
    cp .ipython/profile_default/startup/startup.py ~/.ipython/profile_default/startup/
}

setup_jupyterlab_settings() {
    # Turns on autosave every 5 seconds.
    echo "Setting up JupyterLab settings"
    local dir=.jupyter/lab/user-settings/@jupyterlab/docmanager-extension
    mkdir -p ~/"$dir"
    cp "$dir/plugin.jupyterlab-settings" ~/"$dir/"

    # Runs a hook every time a notebook is saved.
    cp .jupyter/jupyter_server_config.py ~/.jupyter/
}

add_all_problems() {
    echo "Adding problems to ~/craft/problems"
    local zip
    zip=$(mktemp)
    curl -fsS -o "$zip" "$BASE_URL/problems/all_problems.zip"

    # -n keeps files that already exist, so a retry doesn't overwrite a
    # student's work on a problem.
    mkdir -p ~/craft/problems
    unzip -q -n "$zip" -d ~/craft/problems
    rm -f "$zip"
}

copy_notebooks() {
    mkdir -p ~/python
    cp python/*.ipynb ~/python
}

find_username
install_sigma
install_jupyterlab_execute_time
setup_ipython_startup
setup_jupyterlab_settings
add_all_problems
copy_notebooks
