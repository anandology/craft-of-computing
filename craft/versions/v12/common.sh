
run_on_linux() {
    if [ "$(uname -s)" == "Linux" ]
    then
        eval "$@"
    fi
}

run_on_mac() {
    if [ "$(uname -s)" == "Darwin" ]
    then
        eval "$@"
    fi
}

# apt_install pkg...
# Installs packages with apt. Does nothing when not on Linux.
apt_install() {
    [ "$(uname -s)" == "Linux" ] || return 0

    if ! command -v apt-get >/dev/null 2>&1
    then
        echo "error: apt-get is needed to install: $*" >&2
        echo "This course supports Ubuntu (including WSL). Please ask your instructor for help." >&2
        return 1
    fi

    echo "Installing with apt: $*"
    sudo apt-get update -qq || {
        echo "error: 'sudo apt-get update' failed. Check your internet connection and try again." >&2
        return 1
    }
    sudo apt-get install -y -qq "$@" || {
        echo "error: could not install with apt: $*" >&2
        return 1
    }
}

# brew_install pkg...
# Installs packages with Homebrew. Does nothing when not on a mac.
brew_install() {
    [ "$(uname -s)" == "Darwin" ] || return 0

    if ! command -v brew >/dev/null 2>&1
    then
        echo "error: Homebrew is needed to install: $*" >&2
        echo "Install it by following the instructions at https://brew.sh," >&2
        echo "then open a new terminal and run 'craft.sh update' again." >&2
        return 1
    fi

    echo "Installing with brew: $*"
    HOMEBREW_NO_ASK=1 brew install "$@" || {
        echo "error: could not install with brew: $*" >&2
        return 1
    }
}
