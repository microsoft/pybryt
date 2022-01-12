# Makefile for PyBryt
# -------------------
# To generate a release, use `make release` with the `VERSION` argument:
#   $ make release VERSION=0.0.1
#
# To run tests, use `make test` with the `TESTPATH` and/or `PYTESTOPTS` arguments:
#   $ make test
#
# The `testcov` target can be used to build a local copy of the code coverage in HTML:
#   $ make testcov
#
# To build the docs, use `make docs`:
#   $ make docs

PYTEST        = pytest
TESTPATH      = tests
PYTESTOPTS    = -v
COVERAGE      = coverage
DATE         := $(shell date "+%F")

release:
	rm dist/* || :
	echo '__version__ = "$(VERSION)"' > pybryt/version.py
	sed -i "s/date-released: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/date-released: $(DATE)/" CITATION.cff
	sed -i "s/^version: [0-9]\{1,\}\.[0-9]\{1,\}\.[0-9]\{1,\}/version: $(VERSION)/" CITATION.cff
	git add pybryt/version.py
	git add CITATION.cff
	git commit -m "update version info for v$(VERSION)"
	python3 setup.py sdist bdist_wheel
	hub release create -a dist/*.tar.gz -a dist/*.whl -m 'v$(VERSION)' $(VERSION)
	python3 -m twine upload dist/*

test:
	$(PYTEST) $(TESTPATH) $(PYTESTOPTS)

testcov:
	$(COVERAGE) run -m pytest $(TESTPATH) $(PYTESTOPTS) 
	$(COVERAGE) combine

htmlcov: testcov
	$(COVERAGE) html

.PHONY: docs
docs:
	$(MAKE) -C docs html
