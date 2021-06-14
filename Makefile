# Makefile for PyBryt
# to generate a release, use `make release` with the `VERSION` argument:
#   $ make release VERSION=0.0.1
# to run tests, use `make test` with the `TESTPATH` and/or `PYTESTOPTS` arguments:
#   $ make test
# the `testcov` target can be used to build a local copy of the code coverage in HTML
#   $ make testcov

PYTEST        = pytest
TESTPATH      = tests
PYTESTOPTS    = -v
COVERAGE      = coverage

release:
	rm dist/* || :
	echo '__version__ = "$(VERSION)"' > pybryt/version.py
	git add pybryt/version.py
	git commit -m "update pybryt.__version__ for v$(VERSION)"
	python3 setup.py sdist bdist_wheel
	hub release create -a dist/*.tar.gz -a dist/*.whl -m 'v$(VERSION)' $(VERSION)
	python3 -m twine upload dist/*

test:
	$(PYTEST) $(TESTPATH) $(PYTESTOPTS)

testcov:
	$(COVERAGE) run -m pytest $(TESTPATH) $(PYTESTOPTS) 
	$(COVERAGE) combine

covhtml: testcov
	$(COVERAGE) html
