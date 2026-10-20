#! /bin/bash

set -euo pipefail

# The class works from ~/python, so ~/python/rajdhani points at ~/rajdhani,
# where students already have their code. Anything already at
# ~/python/rajdhani is left alone.
link_rajdhani() {
    if [ ! -d ~/rajdhani ]; then
        echo "No ~/rajdhani found, skipping the link"
    elif [ -e ~/python/rajdhani ] || [ -L ~/python/rajdhani ]; then
        echo "Keeping your ~/python/rajdhani"
    else
        echo "Linking ~/python/rajdhani to ~/rajdhani"
        mkdir -p ~/python
        ln -s ~/rajdhani ~/python/rajdhani
    fi
}

NOTEBOOK=rajdhani.ipynb
STARTER=rajdhani-starter.ipynb

# A student may already have their own ~/python/rajdhani.ipynb, so ours goes
# next to it as rajdhani-starter.ipynb instead of replacing it.
copy_rajdhani_notebook() {
    mkdir -p ~/python
    if [ ! -e ~/python/"$NOTEBOOK" ]; then
        echo "Copying $NOTEBOOK to ~/python"
        cp "$NOTEBOOK" ~/python/
    elif cmp -s "$NOTEBOOK" ~/python/"$NOTEBOOK"; then
        echo "~/python/$NOTEBOOK is already up to date"
    elif [ -e ~/python/"$STARTER" ]; then
        echo "Keeping your ~/python/$STARTER"
    else
        echo "Keeping your ~/python/$NOTEBOOK, copying ours as ~/python/$STARTER"
        cp "$NOTEBOOK" ~/python/"$STARTER"
    fi
}

link_rajdhani
copy_rajdhani_notebook
