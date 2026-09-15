# Building sigma.
#
#     make build    build the wheel into dist/
#     make clean    remove dist/ and the files left behind by the build
#
# To ship sigma to students, copy the wheel into a craft version, e.g.
# ../craft/versions/v13/, and install it from that version's upgrade.sh.

.PHONY: build clean

build:
	uv build --wheel --out-dir dist
	@ls dist/*.whl

clean:
	rm -rf dist build src/*.egg-info
