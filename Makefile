# Makefile for PyBryt
# to generate a release, use `make release` with the `VERSION` argument:
#   $ make release VERSION=0.0.1
# to run tests, use `make test` with the `TESTPATH` and/or `PYTESTOPTS` arguments:
#   $ make test
# the `testcov` target can be used to build a local copy of the code coverage in HTML
#   $ make testcov

TESTPATH="tests"
PYTESTOPTS="-v"

release:
	rm dist/* || :
	echo '__version__ = "$(VERSION)"' > pybryt/version.py
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	hub release create -a dist/*.tar.gz -a dist/*.whl -m 'v$(VERSION)' $(VERSION)

test:
	pytest $(TESTPATH) $(PYTESTOPTS)

testcov:
	coverage run --source=. -m pytest $(TESTPATH) $(PYTESTOPTS) && coverage html
