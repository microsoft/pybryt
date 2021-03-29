# Makefile for PyBryt
# to generate a release, use `make release` with the `VERSION` argument:
#   $ make release VERSION=0.0.1

release:
	rm dist/* || :
	echo '__version__ = "$(VERSION)"' > pybryt/version.py
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	hub release create -a dist/*.tar.gz -a dist/*.whl -m 'v$(VERSION)' $(VERSION)

test:
	pytest tests

testcov:
	coverage run --source=. -m pytest tests && coverage html
