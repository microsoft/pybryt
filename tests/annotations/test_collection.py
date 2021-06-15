"""Tests for annotation collections"""

import time
import pytest

from unittest import mock

from pybryt import *
from pybryt.utils import pickle_and_hash

from .utils import *


def test_collection():
    """
    """
    mfp = generate_memory_footprint()
    Annotation.reset_tracked_annotations()

    v1, v2 = Value(mfp[0][0]), Value(mfp[2][0])
    a = Collection(v1, v2, success_message="foo")

    res = a.check(mfp)
    check_obj_attributes(a, {"children__len": 2})
    check_obj_attributes(res, {
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

    a = Collection(v1, v2, enforce_order=True, success_message="foo")
    res = a.check(mfp)
    assert res.satisfied

    v3 = Value(mfp[1][0])
    a.add(v3)
    res = a.check(mfp)
    assert not res.satisfied

    a.remove(v3)
    res = a.check(mfp)
    assert res.satisfied

    a = Collection(v2, v1, enforce_order=True, success_message="foo")
    res = a.check(mfp)
    assert not res.satisfied

    # test errors
    with pytest.raises(ValueError, match="One of the arguments is not an annotation"):
        Collection(v1, 1, v2)
    
    with pytest.raises(TypeError, match="1 is not an annotation"):
        a.add(1)
