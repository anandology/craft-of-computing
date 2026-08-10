
build:
	quarto render

push: build
	cd _site && rsync -av * anandology.com:/var/www/craft-of-computing.anandology.com/2026
