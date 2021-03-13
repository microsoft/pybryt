"""
Tests for PyBryt annotations
"""

import time
import numpy as np

from collections.abc import Iterable
from functools import lru_cache

from pybryt import Value
from pybryt.utils import pickle_and_hash


START_TIMESTAMP = 1614904732.51892


@lru_cache(1)
def generate_memory_footprint():
    """
    """
    np.random.seed(42)    
    return [
        (np.random.uniform(-100, 100, size=(100, 100)), time.time()),
        (4.0, time.time()),
        (list(range(100))[::-1], time.time()),
        (1, time.time()),
        (np.e, time.time()),
        (None, time.time()),
        (None, time.time()),
        (np.random.normal(size=102), time.time()),
        (4.0, time.time()),
    ]


def test_value_annotation():
    """
    """
    mfp = generate_memory_footprint()

    seen = {}
    for val, ts in mfp:
        v = Value(val)
        res = v.check(mfp)

        h = pickle_and_hash(val)

        # check attributes of values and results
        assert len(v.children) == 0, "Value annotation has children"
        assert res.satisfied is True, "Did not find value in memory footprint"
        assert res._satisfied is True, "Did not find value in memory footprint"
        assert res.annotation is v, "Wrong annotation in result"
        assert res.children is None, "Value annotation result has children"
        if h in seen:
            # check that we get the earliest timestamp for duplicate values
            assert np.isclose(res.timestamp, seen[h]), \
                "Wrong timestamp for duplicate value in value annotation result"
        else:
            assert np.isclose(res.timestamp, ts), "Wrong timestamp in value annotation result"
        
        if isinstance(val, Iterable) and hasattr(val, "all"): # for numpy arrays
            assert (res.value == val).all(), "Wrong value in value annotation result"
        else:
            assert res.value == val, "Wrong value in value annotation result"

        if h not in seen:
            seen[h] = ts

    v = Value(-1) # does not occur in mfp
    res = v.check(mfp)

    # check attributes of values and results
    assert len(v.children) == 0, "Value annotation has children"
    assert res.satisfied is False, "Did not find value in memory footprint"
    assert res._satisfied is False, "Did not find value in memory footprint"
    assert res.annotation is v, "Wrong annotation in result"
    assert res.children is None, "Value annotation result has children"
    assert res.timestamp == -1, "Wrong timestamp in value annotation result"
    assert res.value is None, "Wrong value in value annotation result"
