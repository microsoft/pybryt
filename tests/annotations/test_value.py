"""Tests for value annotations"""

import pytest

from itertools import chain
from unittest import mock

import pybryt
from pybryt.execution.memory_footprint import MemoryFootprint

from .utils import assert_object_attrs, generate_memory_footprint


def test_value_annotation():
    """
    """
    footprint = generate_memory_footprint()
    pybryt.Annotation.reset_tracked_annotations()

    seen = {}
    for val, ts in footprint.values:
        v = pybryt.Value(val)
        res = v.check(footprint)

        assert repr(res) == "AnnotationResult(satisfied=True, annotation=pybryt.Value)"

        h = pybryt.utils.pickle_and_hash(val)

        # check attributes of BeforeAnnotation and AnnotationResult
        assert_object_attrs(v, {"children__len": 0})
        assert_object_attrs(res, {
            "children": [],
            "satisfied": True,
            "_satisfied": True,
            "annotation": v,
            "timestamp": seen[h] if h in seen else ts,
            "value": val,
        })

        if h not in seen:
            seen[h] = ts

    v = pybryt.Value(-1)  # does not occur in footprint
    res = v.check(footprint)

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
    assert_object_attrs(v, {"children__len": 0})
    assert_object_attrs(res, {
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
            v = pybryt.Value(-1)

    # test with invariants
    s = footprint.get_value(-1)
    v = pybryt.Value(s.upper(), invariants=[pybryt.invariants.string_capitalization])
    res = v.check(footprint)
    assert res.satisfied

    # test that check_against correctly calls check
    with mock.patch.object(v, "check") as mocked_check:
        mocked_check.return_value = mock.MagicMock()
        mocked_check.return_value.satisfied = True
        assert v.check_against(s.lower())
        mocked_check.assert_called_with(MemoryFootprint.from_values(s.lower(), 0))

    # check custom equivalence function
    mocked_eq = mock.MagicMock()
    v = pybryt.Value(s, equivalence_fn=mocked_eq)
    mocked_eq.return_value = False
    assert not v.check_against("foo")
    mocked_eq.assert_called_with(s, "foo")
    mocked_eq.return_value = True
    assert v.check_against("")
    mocked_eq.assert_called_with(s, "")
    mocked_eq.side_effect = ValueError()
    assert not v.check_against("")

    # check for invalid return type error
    mocked_eq.return_value = 1
    mocked_eq.side_effect = None
    with pytest.raises(TypeError, match=f"Custom equivalence function returned value of invalid type: {type(1)}"):
        v.check_against(1)

    # check debug mode errors
    with pybryt.debug_mode():
        with pytest.raises(ValueError, match="Absolute or relative tolerance specified with an equivalence function"):
            pybryt.Value(1, atol=1e-5, equivalence_fn=lambda x, y: True)

        with pytest.raises(ValueError, match="Absolute or relative tolerance specified with an equivalence function"):
            pybryt.Value(1, rtol=1e-5, equivalence_fn=lambda x, y: True)

        class FooError(Exception):
            pass

        with pytest.raises(FooError):
            def raise_foo(x, y):
                raise FooError()

            v = pybryt.Value(1, equivalence_fn=raise_foo)
            v.check_against(1)


def test_attribute_annotation():
    """
    """
    footprint = generate_memory_footprint()
    pybryt.Annotation.reset_tracked_annotations()
    val, ts = footprint.get_value(0), footprint.get_timestamp(0)

    v = pybryt.Attribute(val, "T")
    res = v.check(footprint)

    # check attributes of BeforeAnnotation and AnnotationResult
    assert_object_attrs(v, {"children__len": 1})
    assert_object_attrs(res, {
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

    # test that check_against correctly calls check
    with mock.patch.object(v, "check") as mocked_check:
        mocked_check.return_value = mock.MagicMock()
        mocked_check.return_value.satisfied = False
        assert not v.check_against(val)
        mocked_check.assert_called_with(MemoryFootprint.from_values(val, 0))

    # check enforce type
    class Foo:
        T = val.T

    footprint2 = pybryt.MemoryFootprint.from_values(Foo(), 1)
    res = v.check(footprint2)
    assert res.satisfied

    v = pybryt.Attribute(val, "T", enforce_type=True)
    res = v.check(footprint2)
    assert not res.satisfied

    footprint3 = MemoryFootprint.from_values(*chain.from_iterable(footprint.values + footprint2.values))
    res = v.check(footprint3)
    assert res.satisfied

    # check error raising
    with pytest.raises(TypeError):
        pybryt.Attribute(val, ["T", 1])
    
    with pytest.raises(TypeError):
        pybryt.Attribute(val, 1)

    with pytest.raises(AttributeError):
        pybryt.Attribute(val, "foo")