"""Tests for PyBryt execution internals"""

import dill
import nbformat
import numpy as np
import pathlib
import random
import tempfile

from unittest import mock

import pybryt.execution


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

    with tempfile.NamedTemporaryFile(delete=False) as observed_ntf:
        with mock.patch("pybryt.execution.mkstemp") as mocked_tempfile:
            mocked_tempfile.return_value = (None, observed_ntf.name)

            footprint = pybryt.execution.execute_notebook(nb, "")
            assert len(footprint) > 0
            assert all(i in footprint.imports for i in ["pandas", "numpy", "matplotlib"])
            assert len(footprint.calls) > 0
