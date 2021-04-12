# Makefile for PyBryt
# to generate a release, use `make release` with the `VERSION` argument:
#   $ make release VERSION=0.0.1

release:
	rm dist/* || :
	echo '__version__ = "$(VERSION)"' > pybryt/version.py
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	hub release create -a dist/*.tar.gz -a dist/*.whl -m 'v$(VERSION)' $(VERSION)

TESTPATH="tests"
PYTESTOPTS="-v"

test:
	pytest $(TESTPATH) $(PYTESTOPTS)

testcov:
	coverage run --source=. -m pytest $(TESTPATH) $(PYTESTOPTS) && coverage html
