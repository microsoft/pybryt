"""Tests for annotation collections"""

import pytest

import pybryt

from .utils import *


def test_collection():
    """
    """
    footprint = generate_memory_footprint()
    pybryt.Annotation.reset_tracked_annotations()

    v1, v2 = pybryt.Value(footprint.get_value(0).value), pybryt.Value(footprint.get_value(2).value)
    a = pybryt.Collection(v1, v2, success_message="foo")

    res = a.check(footprint)
    assert_object_attrs(a, {"children__len": 2})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": None,
        "annotation": a,
        "timestamp": -1,
        "satisfied_at": 2,
    })

    assert a.to_dict() == {
        "name": "Annotation 3",
        "children": [v1.to_dict(), v2.to_dict()],
        "success_message": "foo",
        "failure_message": None,
        "limit": None,
        "group": None,
        "type": "collection",
        "enforce_order": False,
    }

    a = pybryt.Collection(v1, v2, enforce_order=True, success_message="foo")
    res = a.check(footprint)
    assert res.satisfied

    v3 = pybryt.Value(footprint.get_value(1).value)
    a.add(v3)
    res = a.check(footprint)
    assert not res.satisfied

    a.remove(v3)
    res = a.check(footprint)
    assert res.satisfied

    a = pybryt.Collection(v2, v1, enforce_order=True, success_message="foo")
    res = a.check(footprint)
    assert not res.satisfied

    # test errors
    with pytest.raises(ValueError, match="One of the arguments is not an annotation"):
        pybryt.Collection(v1, 1, v2)
    
    with pytest.raises(TypeError, match="1 is not an annotation"):
        a.add(1)
