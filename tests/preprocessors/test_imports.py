"""Tests for the imports preprocessor"""

import nbformat

from textwrap import dedent

from pybryt.preprocessors import ImportFindingPreprocessor


def test_preprocessor():
    """
    """
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        import numpy
        import pandas as pd
        from random import choice
        from itertools import chain as c
        import statsmodels.api
        exec("import tqdm")
    """)))

    ifp = ImportFindingPreprocessor()

    nb2 = ifp.preprocess(nb)
    assert nb2 is nb
    assert ifp.imports == {"numpy", "pandas", "random", "itertools", "statsmodels"}
