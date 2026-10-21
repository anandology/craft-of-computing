#! /bin/bash

set -euo pipefail

# New repositories start on main, the name GitHub and the class use,
# instead of git's default of master.
set_default_branch() {
    echo "Setting git's default branch to main"
    git config --global init.defaultBranch main
}

set_default_branch
