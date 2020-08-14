build-book:
	rm -rf docs
	rm -rf book/_build
	# list folders with notebooks here. Notebooks must be present in _toc.yml.
	cp -r infrastructure book/
	cp -r vector_data book/code
	jupyter-book build book
	cp -r book/_build/html docs
	rm -rf book/code
	rm -rf book/infrastructure
	touch docs/.nojekyll
