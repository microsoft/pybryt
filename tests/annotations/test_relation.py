"""Tests for PyBryt relational annotations"""

import pytest

from pybryt import *

from .utils import *


def test_before_annotation():
    """
    """
    mfp = generate_memory_footprint()
    Annotation.reset_tracked_annotations()

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

    assert v.to_dict() == {
        'name': 'Annotation 3', 
        'group': None, 
        'limit': None, 
        'success_message': None, 
        'failure_message': None, 
        'children': [
            {
                'name': 'Annotation 1', 
                'group': None, 
                'limit': None, 
                'success_message': None, 
                'failure_message': None, 
                'children': [], 
                'type': 'value', 
                'invariants': [], 
                'atol': None,
                'rtol': None,
            }, {
                'name': 
                'Annotation 2', 
                'group': None, 
                'limit': None, 
                'success_message': None, 
                'failure_message': None, 
                'children': [], 
                'type': 'value', 
                'invariants': [], 
                'atol': None,
                'rtol': None,
            }
        ], 
        'type': 'before',
    }

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


def test_and_annotation():
    """
    """
    mfp = generate_memory_footprint()

    val1, ts1 = mfp[0]
    val2, ts2 = mfp[1]

    v1 = Value(val1)
    v2 = Value(val2)
    
    v = v1 & v2
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v3 = Value([])
    v = v1 & v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, v3)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v4 = Value(6.02e+23)
    v = v4 & v2
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v4, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v = v4 & v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v4, v3)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })


def test_or_annotation():
    """
    """
    mfp = generate_memory_footprint()

    val1, ts1 = mfp[0]
    val2, ts2 = mfp[1]

    v1 = Value(val1)
    v2 = Value(val2)
    
    v = v1 | v2
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v3 = Value([])
    v = v1 | v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, v3)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts1,
    })

    v4 = Value(6.02e+23)
    v = v4 | v2
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v4, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v = v4 | v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v4, v3)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })


def test_xor_annotation():
    """
    """
    mfp = generate_memory_footprint()

    val1, ts1 = mfp[0]
    val2, ts2 = mfp[1]

    v1 = Value(val1)
    v2 = Value(val2)
    
    v = v1 ^ v2
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v3 = Value([])
    v = v1 ^ v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, v3)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts1,
    })

    v4 = Value(6.02e+23)
    v = v4 ^ v2
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v4, v2)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v = v4 ^ v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v4, v3)})
    check_obj_attributes(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })


def test_not_annotation():
    """
    """
    mfp = generate_memory_footprint()

    val1, ts1 = mfp[0]
    val2, ts2 = mfp[1]

    v1 = Value(val1)
    v = ~v1
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v1, )})
    check_obj_attributes(res, {
        "children__len": 1,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v3 = Value([])
    v = ~v3
    res = v.check(mfp)

    check_obj_attributes(v, {"children": (v3, )})
    check_obj_attributes(res, {
        "children__len": 1,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })


def test_constructor_errors():
    """
    """
    with pytest.raises(ValueError):
        AndAnnotation([Value(1), "not an annotation"])
