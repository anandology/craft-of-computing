#! /bin/bash

set -euo pipefail

# Example JSON files for the class. A student may have edited one, so a
# rerun of the update keeps any file that is already there.
copy_data_files() {
    local file

    mkdir -p ~/python/files/data
    for file in data/*.json; do
        if [ -e ~/python/files/"$file" ]; then
            echo "Keeping your ~/python/files/$file"
        else
            echo "Copying $file to ~/python/files/data"
            cp "$file" ~/python/files/data/
        fi
    done
}

copy_data_files
