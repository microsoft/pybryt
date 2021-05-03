"""Tests for PyBryt abstract annotations and annotation results"""

import pytest

from unittest import mock

from pybryt import *

from .utils import *


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
    print(res.name)
    check_obj_attributes(res, {
        "name": "Annotation 101",
        "group": "bar",
    })


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


def test_messages():
    """
    """
    mfp = generate_memory_footprint()
    Annotation.reset_tracked_annotations()

    val1, ts1 = mfp[0]
    val2, ts2 = mfp[1]

    v1 = Value(val1, success_message="m1", failure_message="m2")
    v2 = Value(val2)
    
    v = v1.before(v2)
    res = v.check(mfp)

    assert len(res.messages) == 1, "Too many messages"
    assert res.messages[0] == ("m1", 'Annotation 1', True), "Wrong message"

    v.failure_message = "m3"
    res = v.check(mfp)

    assert len(res.messages) == 1, "Too many messages"
    assert res.messages[0] == ("m1", 'Annotation 1', True), "Wrong message"

    res = v.check([])

    assert len(res.messages) == 2, "Wrong number of messages"
    assert res.messages[0] == ("m2", 'Annotation 1', False), "Wrong message"
    assert res.messages[1] == ("m3", 'Annotation 3', False), "Wrong message"

    v2.name = "v2"
    v2.failure_message = "m4"
    res = v.check([])

    assert len(res.messages) == 3, "Wrong number of messages"
    assert res.messages[0] == ("m2", 'Annotation 1', False), "Wrong message"
    assert res.messages[1] == ("m4", "v2", False), "Wrong message"
    assert res.messages[2] == ("m3", 'Annotation 3', False), "Wrong message"


def test_bitwise_ops():
    """
    """
    a1, a2 = Value(1), Value(2)

    assert isinstance(a1 & a2, AndAnnotation), "& operator returns wrong type"
    assert isinstance(a1 | a2, OrAnnotation), "| operator returns wrong type"
    assert isinstance(a1 ^ a2, XorAnnotation), "^ operator returns wrong type"
    assert isinstance(~a1, NotAnnotation), "~ operator returns wrong type"
