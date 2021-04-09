"""Tests for PyBryt execution internals"""

import numpy as np

from unittest import mock

from pybryt.execution import create_collector, execute_notebook

from .utils import AttrDict


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


def test_trace_function():
    """
    """
    np.random.seed(42)

    frame = generate_mocked_frame("<ipython-abc123>", "foo", 3)
    observed, cir = create_collector()

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
