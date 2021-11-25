"""Tests for abstract annotations and annotation results"""

import pybryt
from pybryt.execution.memory_footprint import MemoryFootprint

from .utils import assert_object_attrs, generate_memory_footprint


def test_name_group_limit():
    """
    """
    footprint = generate_memory_footprint()  # TODO: check all calls to this
    val, _ = footprint.get_value(2)

    pybryt.Annotation.reset_tracked_annotations()
    vs = []
    for _ in range(100):
        vs.append(pybryt.Value(val, name="foo", limit=11))
    
    tracked = pybryt.Annotation.get_tracked_annotations()
    assert len(tracked) == 11, "Too many tracked annotations"
    assert tracked == vs[:11], "Wrong tracked annotations"
    assert all(v.name == "foo" and v.limit == 11 for v in vs)

    res = vs[-1].check(footprint)
    assert_object_attrs(res, {
        "name": "foo",
        "group": None,
    })

    v1 = pybryt.Value(footprint.get_value(0)[0], group="bar")
    v2 = pybryt.Value(footprint.get_value(1)[0], group="bar")
    assert_object_attrs(v1, {"group": "bar"})
    assert_object_attrs(v2, {"group": "bar"})

    res = v1.check(footprint)
    print(res.name)
    assert_object_attrs(res, {
        "name": "Annotation 101",
        "group": "bar",
    })


def test_get_reset_tracked_annotations():
    """
    """
    tracked = pybryt.Annotation.get_tracked_annotations()
    pybryt.Annotation.reset_tracked_annotations()
    assert len(tracked) == 0

    v1 = pybryt.Value(1)
    v2 = pybryt.Value(2)
    assert len(tracked) == 2

    v3 = pybryt.Value(3)
    assert len(tracked) == 3

    v4 = v3.before(v2)
    assert len(tracked) == 2
    
    assert v1 in tracked
    assert v2 not in tracked
    assert v3 not in tracked
    assert v4 in tracked

    pybryt.Annotation.reset_tracked_annotations()
    assert len(tracked) == 0


def test_messages():
    """
    """
    footprint = generate_memory_footprint()
    pybryt.Annotation.reset_tracked_annotations()

    val1, _ = footprint.get_value(0)
    val2, _ = footprint.get_value(1)

    v1 = pybryt.Value(val1, success_message="m1", failure_message="m2")
    v2 = pybryt.Value(val2)
    
    v = v1.before(v2)
    res = v.check(footprint)

    assert len(res.messages) == 1, "Too many messages"
    assert res.messages[0] == ("m1", 'Annotation 1', True), "Wrong message"

    v.failure_message = "m3"
    res = v.check(footprint)

    assert len(res.messages) == 1, "Too many messages"
    assert res.messages[0] == ("m1", 'Annotation 1', True), "Wrong message"

    res = v.check(MemoryFootprint.from_values([]))

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
    a1, a2 = pybryt.Value(1), pybryt.Value(2)

    assert isinstance(a1 & a2, pybryt.AndAnnotation), "& operator returns wrong type"
    assert isinstance(a1 | a2, pybryt.OrAnnotation), "| operator returns wrong type"
    assert isinstance(a1 ^ a2, pybryt.XorAnnotation), "^ operator returns wrong type"
    assert isinstance(~a1, pybryt.NotAnnotation), "~ operator returns wrong type"
