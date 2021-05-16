"""Tests for PyBryt execution internals"""

import os
import re
import dill
import pathlib
import random
import tempfile
import nbformat
import numpy as np
import pkg_resources

from unittest import mock

from pybryt.execution import create_collector, execute_notebook, NBFORMAT_VERSION

from ..utils import AttrDict


def generate_mocked_frame(co_filename, co_name, f_lineno, f_globals={}, f_locals={}, f_back=None):
    """
    Factory for generating objects with the instance variables of an ``inspect`` frame that are 
    needed by PyBryt's trace function.
    """
    code = AttrDict({
        "co_filename": co_filename,
        "co_name": co_name,
    })
    return AttrDict({
        "f_lineno": f_lineno,
        "f_globals": f_globals,
        "f_locals": f_locals,
        "f_back": f_back,
        "f_code": code,
    })


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


def test_trace_function():
    """
    """
    np.random.seed(42)
    
    tracked_filepath = "/path/to/tracked/file.py"

    frame = generate_mocked_frame("<ipython-abc123>", "foo", 3)
    observed, cir = create_collector(addl_filenames=[tracked_filepath])

    arr = np.random.uniform(-100, 100, size=(100, 100))
    cir(frame, "return", arr)
    assert len(observed) == 1
    assert np.allclose(observed[0][0], arr)
    assert observed[0][1] == 1

    # test value in skip_types
    cir(frame, "return", type(1))
    assert len(observed) == 1

    # test pickling error
    with mock.patch("dill.dumps") as mocked_dumps:
        mocked_dumps.side_effect = Exception()
        cir(frame, "return", 1)
    
    assert len(observed) == 1

    frame = generate_mocked_frame(
        "<ipython-abc123>", "foo", 3, {"data": arr}
    )

    # check line processing working
    with mock.patch("linecache.getline") as mocked_linecache:

        # check eval call for attributes
        mocked_linecache.return_value = "data.T"
        cir(frame, "line", None)
        assert len(observed) == 2
        assert np.allclose(observed[1][0], arr.T)
        assert observed[1][1] == 4

        # check failed eval call for attributes
        mocked_linecache.return_value = "data.doesnt_exist"
        cir(frame, "line", None)
        assert len(observed) == 2

        # check looking in frame locals + globals
        frame.f_globals["more_data"] = np.random.uniform(-100, 100, size=(100, 100))
        frame.f_locals["more_data"] = np.random.uniform(-100, 100, size=(100, 100))
        mocked_linecache.return_value = "more_data"
        cir(frame, "line", None)
        assert len(observed) == 3
        assert np.allclose(observed[2][0], frame.f_locals["more_data"])
        assert observed[2][1] == 6

        # check that we track assignment statements on function return
        mocked_linecache.return_value = "even_more_data = more_data ** 2"
        cir(frame, "line", None)
        assert len(observed) == 3

        mocked_linecache.return_value = "even_more_data_2 = more_data ** 3"
        cir(frame, "line", None)
        assert len(observed) == 3

        frame.f_locals["even_more_data"] = frame.f_locals["more_data"] ** 2
        frame.f_globals["even_more_data_2"] = frame.f_locals["more_data"] ** 3
        mocked_linecache.return_value = ""
        cir(frame, "return", None)
        assert len(observed) == 6
        assert observed[3][0] is None
        assert observed[3][1] == 9
        assert np.allclose(observed[4][0], frame.f_locals["more_data"] ** 2)
        assert observed[4][1] == 7
        assert np.allclose(observed[5][0], frame.f_locals["more_data"] ** 3)
        assert observed[5][1] == 8

        # check that skip_types respected
        frame.f_locals["none_type"] = type(None)
        mocked_linecache.return_vaue = "none_type"
        cir(frame, "line", None)
        assert len(observed) == 6

        # check that addl_filenames respected
        frame = generate_mocked_frame(tracked_filepath, "bar", 100, f_back=frame)
        frame.f_locals["data"] = arr
        mocked_linecache.return_value = "arr = -1 * data"
        cir(frame, "line", None)
        frame.f_locals["arr"] = -1 * arr
        cir(frame, "return", None) # run a return since arr shows up in vars_not_found
        assert len(observed) == 7
        assert np.allclose(observed[6][0], -1 * arr)
        assert observed[6][1] == 12
    
    # check that IPython child frame return values are tracked
    frame = generate_mocked_frame("/path/to/file.py", "bar", 100, f_back=frame)
    cir(frame, "line", None)
    assert len(observed) == 7

    cir(frame, "return", np.exp(arr))
    assert len(observed) == 8
    assert np.allclose(observed[7][0], np.exp(arr))
    assert observed[7][1] == 12


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

                n_steps, observed = execute_notebook(nb, "", output=ntf.name)
                assert len(ntf.read()) > 0
                assert n_steps == max(t[1] for t in observed)
