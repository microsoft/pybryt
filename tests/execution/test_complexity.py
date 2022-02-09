"""Tests for complexity checking internals"""

import numpy as np
import pytest

import pybryt
import pybryt.execution

from .utils import generate_mocked_frame


def test_time_complexity():
    def do_work(n, transform):
        n = int(transform(n))
        for _ in range(n):
            2 * 2
        return n

    footprint, cir = pybryt.execution.create_collector()

    for e in range(1, 9):
        n = 10 ** e
        with pybryt.check_time_complexity("foo", n):
            do_work(n, lambda v: v)

    assert len(footprint) == 8
    assert all(isinstance(mfp_val.value, pybryt.TimeComplexityResult) for mfp_val in footprint)

    footprint.clear()

    for e in range(1, 9):
        n = float(10 ** e)
        with pybryt.check_time_complexity("foo", n):
            do_work(n, np.log2)

        n = np.random.uniform(size=int(n))
        with pybryt.check_time_complexity("bar", n):
            do_work(n, len)

    assert len(footprint) == 16
    assert all(isinstance(mfp_val.value, pybryt.TimeComplexityResult) for mfp_val in footprint)
    assert [mfp_val.value.name for mfp_val in footprint] == ["foo", "bar"] * 8

    # test error
    n = lambda v: v
    with pytest.raises(TypeError, match=f"n has invalid type {type(n)}"):
        with pybryt.check_time_complexity("foo", n):
            pass

    # check that tracking is disabled
    frame = generate_mocked_frame("<ipython-abc-123>", "bar", 1)
    with pybryt.check_time_complexity("foo", 10):
        cir(frame, "return", 10)
        assert len(footprint) == 16
