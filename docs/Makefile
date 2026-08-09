
build:
	mdbook build

push: build
	cd book && rsync -av * anandology.com:/var/www/craft-of-computing.anandology.com/2026
