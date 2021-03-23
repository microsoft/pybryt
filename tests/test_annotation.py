"""
Tests for PyBryt annotations
"""

import time
import pytest
import numpy as np

from collections.abc import Iterable
from functools import lru_cache
from unittest import mock

from pybryt import Attribute, Value
from pybryt.utils import pickle_and_hash


START_TIMESTAMP = 1614904732.51892


def check_obj_attributes(obj, attrs):
    """
    """
    for k, v in attrs.items():
        if k.endswith("__len"):
            assert len(getattr(obj, k[:-5])) == v
        else:
            is_eq = getattr(obj, k) == v
            if isinstance(is_eq, np.ndarray):
                assert is_eq.all()
            else:
                assert is_eq


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


def test_value_annotation():
    """
    """
    mfp = generate_memory_footprint()

    seen = {}
    for val, ts in mfp:
        v = Value(val)
        res = v.check(mfp)

        h = pickle_and_hash(val)

        # check attributes of BeforeAnnotation and AnnotationResult
        check_obj_attributes(v, {"children__len": 0})
        check_obj_attributes(res, {
            "children": None,
            "satisfied": True,
            "_satisfied": True,
            "annotation": v,
            "timestamp": seen[h] if h in seen else ts,
            "value": val,
        })

        if h not in seen:
            seen[h] = ts

    v = Value(-1) # does not occur in mfp
    res = v.check(mfp)

    # check attributes of BeforeAnnotation and AnnotationResult
    check_obj_attributes(v, {"children__len": 0})
    check_obj_attributes(res, {
        "children": None,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "value": None,
    })

    # test pickling error
    with mock.patch("dill.dumps") as mocked_dumps:
        mocked_dumps.side_effect = Exception()
        with pytest.raises(ValueError):
            v = Value(-1)


def test_attribute_annotation():
    """
    """
    mfp = generate_memory_footprint()
    val, ts = mfp[0]

    v = Attribute(val, "T")
    res = v.check(mfp)

    # check attributes of BeforeAnnotation and AnnotationResult
    check_obj_attributes(v, {"children__len": 1})
    check_obj_attributes(res, {
        "children__len": 1,
        "satisfied": True,
        "_satisfied": None,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts,
        "value": val,
    })


def test_before_annotation():
    """
    """
    mfp = generate_memory_footprint()

    val1, ts1 = mfp[0]
    val2, ts2 = mfp[1]

    v1 = Value(val1)
    v2 = Value(val2)
    v = v1.before(v2)

    res = v.check(mfp)

    # check attributes of BeforeAnnotation and AnnotationResult
    check_obj_attributes(v, {"children": (v1, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })
