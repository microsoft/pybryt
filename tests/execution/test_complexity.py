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

    assert len(footprint.values) == 8
    assert all(isinstance(t[0], pybryt.TimeComplexityResult) for t in footprint.values)

    footprint.values.clear()

    for e in range(1, 9):
        n = float(10 ** e)
        with pybryt.check_time_complexity("foo", n):
            do_work(n, np.log2)

        n = np.random.uniform(size=int(n))
        with pybryt.check_time_complexity("bar", n):
            do_work(n, len)

    assert len(footprint.values) == 16
    assert all(isinstance(t[0], pybryt.TimeComplexityResult) for t in footprint.values)
    assert [t[0].name for t in footprint.values] == ["foo", "bar"] * 8

    # test error
    n = lambda v: v
    with pytest.raises(TypeError, match=f"n has invalid type {type(n)}"):
        with pybryt.check_time_complexity("foo", n):
            pass

    # check that tracking is disabled
    frame = generate_mocked_frame("<ipython-abc-123>", "bar", 1)
    with pybryt.check_time_complexity("foo", 10):
        cir(frame, "return", 10)
        assert len(footprint.values) == 16
