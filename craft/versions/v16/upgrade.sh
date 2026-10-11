#! /bin/bash

set -euo pipefail

# Later versions run update-problems.sh whenever they publish new problems.
install_update_problems() {
    echo "Installing update-problems.sh"
    mkdir -p ~/.craft/lib
    cp update-problems.sh ~/.craft/lib/
}

install_update_problems
bash ~/.craft/lib/update-problems.sh
