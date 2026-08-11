# Building and publishing releases of the craft tool.
#
#     make test       build a release and install it into a scratch HOME
#     make release    bump the version and build into ../website/dist/
#
# After "make release", publish with the usual website deploy.

VERSION  := $(shell cat version.txt)
DIST     := ../website/dist
SITE     := ../website
SCRATCH  := /tmp/craft-test

# Files that make up a release. install.sh is not among them: it is
# published on its own, and students fetch it before they have anything.
SOURCES  := version.txt packages.txt profile.sh post-update.sh bin content

.PHONY: build release test clean

# Build the tarball for the current version into the published directory.
build:
	@mkdir -p $(DIST)
	tar -czf $(DIST)/craft-$(VERSION).tar.gz $(SOURCES)
	@echo $(VERSION) > $(DIST)/version.txt
	@cp bin/craft.sh $(DIST)/craft.sh
	@cp install.sh $(SITE)/install.sh
	@echo "built version $(VERSION) -> $(DIST)/craft-$(VERSION).tar.gz"
	@du -h $(DIST)/craft-$(VERSION).tar.gz

# Bump the version, then build. Kept separate from build so that testing
# does not burn version numbers.
release:
	@echo $$(( $(VERSION) + 1 )) > version.txt
	@$(MAKE) --no-print-directory build
	@echo ""
	@echo "Now publish the website to put version $$(cat version.txt) live."

# Install a release into a scratch home directory and run it, without
# touching your own setup or the real server. Serves the release over a
# local web server, so the whole path is exercised.
test: build
	@rm -rf $(SCRATCH)
	@mkdir -p $(SCRATCH)
	@python3 -m http.server 8123 --directory $(DIST) >/dev/null 2>&1 & \
	  server=$$!; \
	  sleep 1; \
	  HOME=$(SCRATCH) CRAFT_URL=http://localhost:8123 bash install.sh; \
	  status=$$?; \
	  kill $$server; \
	  echo ""; \
	  echo "scratch home is at $(SCRATCH)"; \
	  exit $$status

clean:
	rm -rf $(SCRATCH)
