#! /bin/bash

set -euo pipefail

# craft.sh runs this from the version's own directory.
VERSION_ROOT=$(pwd)

setup_sudo_without_password() {
    # Allow sudo without password. The file is checked first, because a
    # broken file in /etc/sudoers.d breaks sudo for the whole machine.
    run_on_linux "sudo visudo -cf etc/sudoers.d/craft && sudo install -m 0440 -o root -g root etc/sudoers.d/craft /etc/sudoers.d/craft"
}

install_uv() {
    brew_install uv
    run_on_linux "curl -LsSf https://astral.sh/uv/install.sh | sh"

    # The installer puts uv in ~/.local/bin, which only new shells have on
    # PATH. The rest of this script needs it now.
    export PATH="$HOME/.local/bin:$PATH"
}

# add_block FILE NAME
# Appends the text on stdin to FILE, between "# >>> craft NAME >>>" and
# "# <<< craft NAME <<<". Does nothing if the block is already there, so
# running this again does not add it twice.
add_block() {
    local file="$1" name="$2" text

    text=$(cat)
    touch "$file"

    if ! grep -qF "# >>> craft $name >>>" "$file"
    then
        printf '\n# >>> craft %s >>>\n%s\n# <<< craft %s <<<\n' "$name" "$text" "$name" >> "$file"
    fi
}

setup_bashrc_d() {
    mkdir -p ~/.bashrc.d/

    # Load every file in ~/.bashrc.d from ~/.bashrc.
    add_block ~/.bashrc bashrc.d <<'EOF'
for f in ~/.bashrc.d/*; do
    [ -f "$f" ] && . "$f"
done
unset f
EOF

    if [ "$(uname -s)" == "Darwin" ]
    then
        # bash on a mac starts as a login shell, which reads ~/.bash_profile
        # and not ~/.bashrc.
        add_block ~/.bash_profile bashrc <<'EOF'
[ -f ~/.bashrc ] && . ~/.bashrc
EOF
    fi
}

setup_venv() {
    uv venv --clear ~/craft/venv
    cp .bashrc.d/craft-venv ~/.bashrc.d/
}

install_jupyterlab() {
    source ~/craft/venv/bin/activate
    uv pip install jupyterlab

    # jupyter config to disable pw, start in ~/python
    mkdir -p ~/.jupyter ~/python
    cp .jupyter/jupyter_lab_config.py ~/.jupyter/
}

source $VERSION_ROOT/common.sh

setup_sudo_without_password
setup_bashrc_d
install_uv
setup_venv
install_jupyterlab