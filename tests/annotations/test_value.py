"""Tests for PyBryt value annotations"""

import time
import pytest

from unittest import mock

from pybryt import *
from pybryt.utils import pickle_and_hash

from .utils import *


def test_value_annotation():
    """
    """
    mfp = generate_memory_footprint()
    Annotation.reset_tracked_annotations()

    seen = {}
    for val, ts in mfp:
        v = Value(val)
        res = v.check(mfp)

        assert repr(res) == "AnnotationResult(satisfied=True, annotation=pybryt.Value)"

        h = pickle_and_hash(val)

        # check attributes of BeforeAnnotation and AnnotationResult
        check_obj_attributes(v, {"children__len": 0})
        check_obj_attributes(res, {
            "children": [],
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

    assert v.to_dict() == {
        "name": "Annotation 11",
        "children": [],
        "success_message": None,
        "failure_message": None,
        "limit": None,
        "group": None,
        "invariants": [],
        "atol": None,
        "rtol": None,
        "type": "value",
    }
    assert repr(res) == "AnnotationResult(satisfied=False, annotation=pybryt.Value)"

    # check __repr__
    assert repr(v) == "pybryt.Value", "wrong __repr__"

    # check attributes of BeforeAnnotation and AnnotationResult
    check_obj_attributes(v, {"children__len": 0})
    check_obj_attributes(res, {
        "children": [],
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

    # test with invariants
    s = mfp[-1][0]
    v = Value(s.upper(), invariants=[invariants.string_capitalization])
    res = v.check(mfp)
    assert res.satisfied


def test_attribute_annotation():
    """
    """
    mfp = generate_memory_footprint()
    Annotation.reset_tracked_annotations()
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

    assert v.to_dict() == {
        "name": "Annotation 2",
        "children": [
            {
                'name': 
                'Annotation 1', 
                'group': None, 
                'limit': None, 
                'success_message': None, 
                'failure_message': None, 
                'children': [], 
                'invariants': [], 
                'atol': None,
                'rtol': None,
                "type": None,
            }
        ],
        "success_message": None,
        "failure_message": None,
        "limit": None,
        "group": None,
        "invariants": [],
        "atol": None,
        "rtol": None,
        "type": "attribute",
        "attributes": ['T'],
        "enforce_type": False,
    }

    # check enforce type
    class Foo:
        T = val.T

    mfp2 = [(Foo(), 1)]
    res = v.check(mfp2)
    assert res.satisfied

    v = Attribute(val, "T", enforce_type=True)
    res = v.check(mfp2)
    assert not res.satisfied

    res = v.check(mfp + mfp2)
    assert res.satisfied

    # check error raising
    with pytest.raises(TypeError):
        Attribute(val, ["T", 1])
    
    with pytest.raises(TypeError):
        Attribute(val, 1)

    with pytest.raises(AttributeError):
        Attribute(val, "foo")