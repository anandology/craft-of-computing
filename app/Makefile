# Build the quiz JSON the app serves from its markdown source.
#
#     make            rebuild every quiz whose markdown is newer than its json
#     make clean      delete the generated json
#
# Run it from this directory, or `make -C app` from the top of the repo.

PYTHON ?= python3

# A quiz's roll size is a property of the class, not of the questions, so the
# markdown has nowhere to put it. Set ROLL_<name> for any quiz that wants the
# dashboard's "of 60 on the roll" line.
ROLL_command-line = 60

sources := $(wildcard quizzes/*.md)
targets := $(sources:.md=.json)

.PHONY: all clean
all: $(targets)

quizzes/%.json: quizzes/%.md md2quiz.py
	$(PYTHON) md2quiz.py $< $(if $(ROLL_$*),--roll $(ROLL_$*))

clean:
	rm -f $(targets)
