# Building and publishing the craft tool.
#
#     make build      zip every version into dist/, with latest-version.txt
#     make push       build, then rsync the zips and latest-version.txt to the server
#     make migration  build the last tarball release, which moves old installs over
#     make test       build, then install into a scratch HOME from a local server
#
# To release a version, add versions/vN/, write N to latest-version.txt, and
# run "make push".

DIST     := dist
SITE     := ../website
SCRATCH  := /tmp/craft-test

# Where updates are published: https://coc.apucomputing.in/~anand/craft
SERVER   := anand@coc.apucomputing.in:public_html/craft

# Versions are immutable once published, but zipping again is harmless, so
# every version is rebuilt each time.
VERSIONS := $(sort $(notdir $(wildcard versions/v*)))

LATEST   := $(shell cat latest-version.txt)

# The old tarball system, still served from the website. Students on it
# check $(SITE)/dist/version.txt and download craft-N.tar.gz; release 11 is
# the one that moves them over.
MIGRATION_RELEASE := 11

.PHONY: build push migration test clean

build:
	@test -f versions/v$(LATEST)/upgrade.sh \
	  || { echo "latest-version.txt says $(LATEST), but versions/v$(LATEST)/upgrade.sh does not exist" >&2; exit 1; }
	@mkdir -p $(DIST)/versions
	@for v in $(VERSIONS); do \
	  rm -f $(DIST)/versions/$$v.zip; \
	  (cd versions/$$v && zip -q -r -X $(abspath $(DIST))/versions/$$v.zip .) || exit 1; \
	  echo "built $(DIST)/versions/$$v.zip"; \
	done
	@cp bin/craft.sh $(DIST)/craft.sh
	@cp latest-version.txt $(DIST)/latest-version.txt
	@cp install.sh $(SITE)/install.sh
	@echo "latest version is $(LATEST)"

push: build
	rsync -av $(DIST)/versions $(DIST)/latest-version.txt $(SERVER)/

# ~/.craft is replaced by the contents of this tarball, and then its
# post-update.sh hands over to the new craft.sh. Published with the website.
migration:
	@rm -rf build/migration
	@mkdir -p build/migration/bin build/migration/commands
	@cp bin/craft.sh build/migration/bin/
	@cp commands/*.sh build/migration/commands/
	@cp migration/version.txt migration/post-update.sh build/migration/
	tar -czf $(SITE)/dist/craft-$(MIGRATION_RELEASE).tar.gz -C build/migration .
	@echo $(MIGRATION_RELEASE) > $(SITE)/dist/version.txt
	@rm -rf build

# Install into a scratch home directory from a local web server, without
# touching your own setup or the real server.
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
	rm -rf $(SCRATCH) $(DIST) build
