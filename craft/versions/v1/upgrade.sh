#! /bin/bash

set -euo pipefail

# craft.sh runs this from the version's own directory.
VERSION_ROOT=$(pwd)

source $VERSION_ROOT/common.sh

packages=$(cat $VERSION_ROOT/apt-packages.txt)
apt_install $packages

mkdir -p ~/craft