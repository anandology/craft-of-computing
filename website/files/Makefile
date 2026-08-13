# Builds one zip per practice session.
#
# practice/resize-images/ becomes resize-images.zip, holding the paths
# practice/resize-images/... -- students unzip in their home directory, so what
# is in practice/ here is what appears in their home directory there.
#
# The zips are gitignored and rebuilt from these sources.

SESSIONS := $(notdir $(wildcard practice/*))
ZIPS := $(addsuffix .zip,$(SESSIONS))

all: $(ZIPS)

# Rebuilt every time. Make can only see the timestamp of practice/<name>
# itself, which does not change when a file inside it is edited -- so a
# dependency on the directory would leave the zip stale after exactly the
# edit that matters. Rezipping a few small images costs nothing.
.PHONY: all clean $(ZIPS)

$(ZIPS): %.zip:
	rm -f $@
	zip -q -r $@ practice/$*

clean:
	rm -f $(ZIPS)
