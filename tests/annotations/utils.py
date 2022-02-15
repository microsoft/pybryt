"""Utilities for PyBryt annotation tests"""

import numpy as np

from functools import lru_cache
from itertools import chain

from pybryt.execution import MemoryFootprint, MemoryFootprintValue


def assert_object_attrs(obj, attrs):
    """
    """
    for k, v in attrs.items():
        if k.endswith("__len"):
            assert len(getattr(obj, k[:-5])) == v, \
                f"Attr '{k}' length is wrong: expected {v} but got {len(getattr(obj, k[:-5]))}"
        else:
            attr = getattr(obj, k)
            if isinstance(attr, (np.ndarray, float, np.generic, int)):
                is_eq = np.allclose(attr, v)
            else:
                is_eq = attr == v
            if isinstance(is_eq, np.ndarray):
                assert is_eq.all(), f"Attr '{k}' is wrong: expected {v} but got {getattr(obj, k)}"
            else:
                assert is_eq, f"Attr '{k}' is wrong: expected {v} but got {getattr(obj, k)}"


@lru_cache(1)
def generate_memory_footprint() -> MemoryFootprint:
    """
    """
    np.random.seed(42)
    objs = [
        np.random.uniform(-100, 100, size=(100, 100)),
        4.0,
        list(range(100))[::-1],
        1,
        np.e,
        None,
        None,
        np.random.normal(size=102),
        4.0,
        "some CasE insenSITIve StrINg!",
    ]
    return MemoryFootprint.from_values(*[MemoryFootprintValue(o, i, None) for i, o in enumerate(objs)])
