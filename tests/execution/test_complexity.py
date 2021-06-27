""""""

import pytest
import numpy as np

from pybryt import check_time_complexity
from pybryt.execution import create_collector, TimeComplexityResult

from .utils import generate_mocked_frame


def test_time_complexity():
    def do_work(n, transform):
        n = int(transform(n))
        for _ in range(n):
            2 * 2
        return n

    (observed, _), cir = create_collector()

    for e in range(1, 9):
        n = 10 ** e
        with check_time_complexity("foo", n):
            do_work(n, lambda v: v)

    assert len(observed) == 8
    assert all(isinstance(t[0], TimeComplexityResult) for t in observed)

    observed.clear()

    for e in range(1, 9):
        n = float(10 ** e)
        with check_time_complexity("foo", n):
            do_work(n, np.log2)

        n = np.random.uniform(size=int(n))
        with check_time_complexity("bar", n):
            do_work(n, len)

    assert len(observed) == 16
    assert all(isinstance(t[0], TimeComplexityResult) for t in observed)
    assert [t[0].name for t in observed] == ["foo", "bar"] * 8

    # test error
    n = lambda v: v
    with pytest.raises(TypeError, match=f"n has invalid type {type(n)}"):
        with check_time_complexity("foo", n):
            pass

    # check that tracking is disabled
    frame = generate_mocked_frame("<ipython-abc-123>", "bar", 1)
    with check_time_complexity("foo", 10):
        cir(frame, "return", 10)
        assert len(observed) == 16
