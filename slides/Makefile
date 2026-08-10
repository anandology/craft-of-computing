.PHONY: all pdf html open clean

SOURCES=$(wildcard *.md)
HTML_TARGETS=$(SOURCES:%.md=html/%.html)
PDF_TARGETS=$(SOURCES:%.md=pdf/%.pdf)

TARGETS=$(HTML_TARGETS) $(PDF_TARGETS)

MARP  := $(shell command -v marp || echo "npx --yes @marp-team/marp-cli")
CHROME ?= $(shell command -v chromium || command -v google-chrome || command -v chrome || echo "")
export CHROME_PATH := $(CHROME)

all: $(TARGETS)

html/%.html: %.md
	@mkdir -p html
	$(MARP) $< -o $@

pdf/%.pdf: %.md
	@mkdir -p pdf
	$(MARP) $< -o $@

clean:
	rm -f $(TARGETS)

.PHONY: all clean
