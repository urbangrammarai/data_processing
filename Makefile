build-book:
	rm -rf docs
	# list folders with notebooks here. Notebooks must be present in _toc.yml.
	cp -r building_footprints book/code
	jupyter-book build book
	cp -r book/_build/html docs
	rm -rf book/code
	touch docs/.nojekyll
