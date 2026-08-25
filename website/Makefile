
build: zips craft
	quarto render

# The practice session downloads. Built before the render, so quarto has the
# zips to copy into _site.
zips:
	$(MAKE) -C files

craft:
	cd ../craft && make build

.PHONY: build push zips craft

push: build
	cd _site && rsync -av * anand@anandology.com:/var/www/craft-of-computing.anandology.com/2026
