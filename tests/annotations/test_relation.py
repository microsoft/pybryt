"""Tests for PyBryt relational annotations"""

from pybryt import *

from .utils import *


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
