"""
Tests for PyBryt annotations
"""

import time
import pytest
import numpy as np

from collections.abc import Iterable
from functools import lru_cache
from unittest import mock

from pybryt import Annotation, Attribute, Value
from pybryt.utils import pickle_and_hash


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


def test_value_annotation():
    """
    """
    mfp = generate_memory_footprint()

    seen = {}
    for val, ts in mfp:
        v = Value(val)
        res = v.check(mfp)

        assert repr(res) == "AnnotationResult(satisfied=True, annotation=pybryt.Value)"

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

    assert repr(res) == "AnnotationResult(satisfied=False, annotation=pybryt.Value)"

    # check __repr__
    assert repr(v) == "pybryt.Value", "wrong __repr__"

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

    # check error raising
    with pytest.raises(TypeError):
        Attribute(val, ["T", 1])
    
    with pytest.raises(TypeError):
        Attribute(val, 1)

    with pytest.raises(AttributeError):
        Attribute(val, "foo")


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

    v = v2.after(v1)
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

    v = v1.after(v2)
    res = v.check(mfp)

    # check attributes of BeforeAnnotation and AnnotationResult
    check_obj_attributes(v, {"children": (v2, v1)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })


def test_name_group_limit():
    """
    """
    mfp = generate_memory_footprint()
    val, ts = mfp[2]

    Annotation.reset_tracked_annotations()
    vs = []
    for _ in range(100):
        vs.append(Value(val, name="foo", limit=11))
    
    tracked = Annotation.get_tracked_annotations()
    assert len(tracked) == 11, "Too many tracked annotations"
    assert tracked == vs[:11], "Wrong tracked annotations"
    assert all(v.name == "foo" and v.limit == 11 for v in vs)

    res = vs[-1].check(mfp)
    check_obj_attributes(res, {
        "name": "foo",
        "group": None,
    })

    v1 = Value(mfp[0][0], group="bar")
    v2 = Value(mfp[1][0], group="bar")
    check_obj_attributes(v1, {"group": "bar"})
    check_obj_attributes(v2, {"group": "bar"})

    res = v1.check(mfp)
    check_obj_attributes(res, {
        "name": None,
        "group": "bar",
    })

    # check error raising
    with pytest.raises(TypeError):
        Value(1, limit=5)


def test_get_reset_tracked_annotations():
    """
    """
    tracked = Annotation.get_tracked_annotations()
    Annotation.reset_tracked_annotations()
    assert len(tracked) == 0

    v1 = Value(1)
    v2 = Value(2)
    assert len(tracked) == 2

    v3 = Value(3)
    assert len(tracked) == 3

    v4 = v3.before(v2)
    assert len(tracked) == 2
    
    assert v1 in tracked
    assert v2 not in tracked
    assert v3 not in tracked
    assert v4 in tracked

    Annotation.reset_tracked_annotations()
    assert len(tracked) == 0
