"""Tests for PyBryt execution internals"""

import re
import dill
import pathlib
import random
import tempfile
import nbformat
import numpy as np

from unittest import mock

from pybryt.execution import execute_notebook


def generate_test_notebook():
    """
    """
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(
        "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n%matplotlib inline"
        ))
    nb.cells.append(nbformat.v4.new_code_cell(
        "np.random.seed(42)\nx = np.random.uniform(size=1000)\ny = np.random.normal(size=1000)"
    ))
    nb.cells.append(nbformat.v4.new_code_cell("df = pd.DataFrame({'x': x, 'y': y})"))
    return nb


def test_notebook_execution():
    """
    """
    random.seed(42)
    nb = generate_test_notebook()

    observed_fn = str(pathlib.Path(__file__).parent.parent / 'files' / 'expected_observed.pkl')
    with open(observed_fn, "rb") as f:
        expected_observed = dill.load(f)

    with tempfile.NamedTemporaryFile("w+") as ntf:
        with tempfile.NamedTemporaryFile(delete=False) as observed_ntf:
            with mock.patch("pybryt.execution.mkstemp") as mocked_tempfile:
                mocked_tempfile.return_value = (None, observed_ntf.name)

                n_steps, observed, calls, _ = execute_notebook(nb, "", output=ntf.name)
                assert len(ntf.read()) > 0
                assert n_steps == max(t[1] for t in observed)
                assert isinstance(calls, list) and isinstance(calls[0], tuple) and \
                    isinstance(calls[0][0], str) and isinstance(calls[0][1], str)
