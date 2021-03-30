"""Utilities for PyBryt annotation tests"""

import time
import numpy as np

from functools import lru_cache


def check_obj_attributes(obj, attrs):
    """
    """
    for k, v in attrs.items():
        if k.endswith("__len"):
            assert len(getattr(obj, k[:-5])) == v, \
                f"Attr '{k}' is wrong: expected {v} but got {len(getattr(obj, k))}"
        else:
            is_eq = getattr(obj, k) == v
            if isinstance(is_eq, np.ndarray):
                assert is_eq.all(), f"Attr '{k}' is wrong: expected {v} but got {getattr(obj, k)}"
            else:
                assert is_eq, f"Attr '{k}' is wrong: expected {v} but got {getattr(obj, k)}"


@lru_cache(1)
def generate_memory_footprint():
    """
    """
    np.random.seed(42)    
    return [
        (np.random.uniform(-100, 100, size=(100, 100)), time.time_ns()),
        (4.0, time.time_ns()),
        (list(range(100))[::-1], time.time_ns()),
        (1, time.time_ns()),
        (np.e, time.time_ns()),
        (None, time.time_ns()),
        (None, time.time_ns()),
        (np.random.normal(size=102), time.time_ns()),
        (4.0, time.time_ns()),
    ]