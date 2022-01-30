"""Tests for abstract annotations and annotation results"""

import pybryt
from pybryt.execution.memory_footprint import MemoryFootprint

from .utils import assert_object_attrs, generate_memory_footprint


def test_name_group_limit():
    """
    """
    footprint = generate_memory_footprint()
    val = footprint.get_value(2)

    pybryt.Annotation.reset_tracked_annotations()
    vs = []
    for _ in range(100):
        vs.append(pybryt.Value(val, name="foo", limit=11))
    
    tracked = pybryt.Annotation.get_tracked_annotations()
    assert len(tracked) == 100
    assert tracked == vs, "Wrong tracked annotations"

    res = vs[-1].check(footprint)
    assert_object_attrs(res, {
        "name": "foo",
        "group": None,
    })

    v1 = pybryt.Value(footprint.get_value(0).value, group="bar")
    v2 = pybryt.Value(footprint.get_value(1).value, group="bar")
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

    val1 = footprint.get_value(0).value
    val2 = footprint.get_value(1).value

    v1 = pybryt.Value(val1, success_message="m1", failure_message="m2")
    v2 = pybryt.Value(val2)
    
    v = v1.before(v2)
    res = v.check(footprint)

    assert len(res.messages) == 3
    assert_object_attrs(res.messages[0], {"message": "m1", "satisfied": True})

    v.failure_message = "m3"
    res = v.check(footprint)

    assert len(res.messages) == 3

    res = v.check(MemoryFootprint.from_values())

    assert len(res.messages) == 3
    assert_object_attrs(res.messages[0], {"message": "m2", "satisfied": False})
    assert_object_attrs(res.messages[1], {"message": None, "satisfied": False})
    assert_object_attrs(res.messages[2], {"message": "m3", "satisfied": False})

    v2.name = "v2"
    v2.failure_message = "m4"
    res = v.check(MemoryFootprint.from_values())

    assert len(res.messages) == 3
    assert_object_attrs(res.messages[1], {"message": "m4", "name": "v2", "satisfied": False})


def test_bitwise_ops():
    """
    """
    a1, a2 = pybryt.Value(1), pybryt.Value(2)

    assert isinstance(a1 & a2, pybryt.AndAnnotation), "& operator returns wrong type"
    assert isinstance(a1 | a2, pybryt.OrAnnotation), "| operator returns wrong type"
    assert isinstance(a1 ^ a2, pybryt.XorAnnotation), "^ operator returns wrong type"
    assert isinstance(~a1, pybryt.NotAnnotation), "~ operator returns wrong type"
