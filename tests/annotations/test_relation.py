"""Tests for relational annotations"""

import pytest

import pybryt

from .utils import assert_object_attrs, generate_memory_footprint


def test_before_annotation():
    """
    """
    footprint = generate_memory_footprint()
    pybryt.Annotation.reset_tracked_annotations()

    val1 = footprint.get_value(0).value
    val2, ts2 = footprint.get_value(1).value, footprint.get_value(1).timestamp

    v1 = pybryt.Value(val1)
    v2 = pybryt.Value(val2)
    
    v = v1.before(v2)
    res = v.check(footprint)

    # check attributes of BeforeAnnotation and AnnotationResult
    assert_object_attrs(v, {"children": (v1, v2)})
    assert_object_attrs(res, {
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
    res = v.check(footprint)

    # check attributes of BeforeAnnotation and AnnotationResult
    assert_object_attrs(v, {"children": (v1, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v = v1.after(v2)
    res = v.check(footprint)

    # check attributes of BeforeAnnotation and AnnotationResult
    assert_object_attrs(v, {"children": (v2, v1)})
    assert_object_attrs(res, {
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
    footprint = generate_memory_footprint()

    val1 = footprint.get_value(0).value
    val2, ts2 = footprint.get_value(1).value, footprint.get_value(1).timestamp

    v1 = pybryt.Value(val1)
    v2 = pybryt.Value(val2)
    
    v = v1 & v2
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v3 = pybryt.Value([])
    v = v1 & v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, v3)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v4 = pybryt.Value(6.02e+23)
    v = v4 & v2
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v4, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v = v4 & v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v4, v3)})
    assert_object_attrs(res, {
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
    footprint = generate_memory_footprint()

    val1, ts1 = footprint.get_value(0).value, footprint.get_value(0).timestamp
    val2, ts2 = footprint.get_value(1).value, footprint.get_value(1).timestamp

    v1 = pybryt.Value(val1)
    v2 = pybryt.Value(val2)
    
    v = v1 | v2
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v3 = pybryt.Value([])
    v = v1 | v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, v3)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts1,
    })

    v4 = pybryt.Value(6.02e+23)
    v = v4 | v2
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v4, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v = v4 | v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v4, v3)})
    assert_object_attrs(res, {
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
    footprint = generate_memory_footprint()

    val1, ts1 = footprint.get_value(0).value, footprint.get_value(0).timestamp
    val2, ts2 = footprint.get_value(1).value, footprint.get_value(1).timestamp

    v1 = pybryt.Value(val1)
    v2 = pybryt.Value(val2)
    
    v = v1 ^ v2
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v3 = pybryt.Value([])
    v = v1 ^ v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, v3)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts1,
    })

    v4 = pybryt.Value(6.02e+23)
    v = v4 ^ v2
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v4, v2)})
    assert_object_attrs(res, {
        "children__len": 2,
        "satisfied": True,
        "_satisfied": True,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": ts2,
    })

    v = v4 ^ v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v4, v3)})
    assert_object_attrs(res, {
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
    footprint = generate_memory_footprint()

    val1 = footprint.get_value(0).value

    v1 = pybryt.Value(val1)
    v = ~v1
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v1, )})
    assert_object_attrs(res, {
        "children__len": 1,
        "satisfied": False,
        "_satisfied": False,
        "annotation": v,
        "timestamp": -1,
        "satisfied_at": -1,
    })

    v3 = pybryt.Value([])
    v = ~v3
    res = v.check(footprint)

    assert_object_attrs(v, {"children": (v3, )})
    assert_object_attrs(res, {
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
        pybryt.AndAnnotation([pybryt.Value(1), "not an annotation"])
