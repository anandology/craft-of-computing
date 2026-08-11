# profile.sh -- course settings for your shell.
#
# This file is loaded by ~/.bashrc every time you open a terminal. It is
# part of the course tool, so it is replaced whenever you run
# "craft.sh update". If you want settings of your own, put them in
# ~/.bashrc instead -- those will not be overwritten.
#
# It is a normal shell file. Read it whenever you want to know what your
# terminal is doing on your behalf.

export CRAFT_HOME="$HOME/.craft"

# Course material is copied into your home directory, one folder per week.
# CRAFT_CONTENT points at the original, untouched copy -- useful if you
# want to compare against it, or get a fresh copy of a file you changed:
#
#     cp "$CRAFT_CONTENT/week2/notes.md" ~/week2/
#
export CRAFT_CONTENT="$HOME/.craft/content"
