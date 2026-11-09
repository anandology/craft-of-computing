# Run through uv so quarto uses the project's .venv, which has Jupyter for
# the pages that run Python. The system python3 does not.
QUARTO = uv run quarto

build: zips craft
	$(QUARTO) render

# The practice session downloads. Built before the render, so quarto has the
# zips to copy into _site.
zips:
	$(MAKE) -C files

craft:
	cd ../craft && make build

.PHONY: build push zips craft quick quick-push

push: build
	cd _site && rsync -av * anand@anandology.com:/var/www/craft-of-computing.anandology.com/2026

# Renders only the pages changed since they were last rendered: a .qmd newer
# than its .html in _site. Each page takes a few seconds, against minutes for
# the whole site, so a fix can go out in the middle of a class.
#
# A change to a file every page shares -- the sidebar and navbar in
# _quarto.yml, the styles, the session filter -- needs every page rendered
# again, so then it falls back to the full render. The schedule page is built
# from schedule.yml, so a change there renders that page.
SHARED = _quarto.yml theme.scss styles.css session.lua _fonts.html

quick:
	@if [ ! -f _site/index.html ] || [ -n "$$(find $(SHARED) -newer _site/index.html)" ]; then \
		echo "Shared files changed: rendering the whole site."; \
		$(QUARTO) render; \
	else \
		pages=$$(find . -name '*.qmd' -not -path './_site/*' -not -path './drafts/*' | sed 's|^\./||' | \
			while read f; do html="_site/$${f%.qmd}.html"; \
				if [ ! -f "$$html" ] || [ "$$f" -nt "$$html" ]; then echo "$$f"; fi; done); \
		if [ ! -f _site/overview/schedule.html ] || [ schedule.yml -nt _site/overview/schedule.html ]; then pages="$$pages overview/schedule.qmd"; fi; \
		if [ -z "$$pages" ]; then echo "No changed pages."; fi; \
		for f in $$pages; do $(QUARTO) render "$$f" || exit 1; done; \
	fi

quick-push: quick
	cd _site && rsync -av * anand@anandology.com:/var/www/craft-of-computing.anandology.com/2026
