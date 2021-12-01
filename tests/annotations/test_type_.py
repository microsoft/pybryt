"""Tests for type annotations"""

import numpy as np
import pytest

from unittest import mock

import pybryt

from .utils import assert_object_attrs, generate_memory_footprint


def test_forbid_type():
    """
    """
    footprint = generate_memory_footprint()
    pybryt.Annotation.reset_tracked_annotations()

    a = pybryt.ForbidType(bool)
    res = a.check(footprint)

    assert_object_attrs(a, {"children__len": 0})
    assert_object_attrs(res, {
        "children": [],
        "satisfied": True,
        "_satisfied": True,
        "annotation": a,
        "timestamp": -1,
        "value": None,
    })

    assert a.to_dict() == {
        "name": "Annotation 1",
        "children": [],
        "success_message": None,
        "failure_message": None,
        "limit": None,
        "group": None,
        "type": "forbidtype",
        "type_": "<class 'bool'>",
    }

    a = pybryt.ForbidType(np.ndarray)
    res = a.check(footprint)
    assert_object_attrs(res, {
        "children": [],
        "satisfied": False,
        "_satisfied": False,
        "annotation": a,
        "timestamp": -1,
        "value": None,
    })

    # check constructor errors
    with pytest.raises(TypeError, match=f"1 is not a type"):
        pybryt.ForbidType(1)

    with mock.patch("pybryt.annotations.type_.dill") as mocked_dill:
        mocked_dill.dumps.side_effect = Exception()

        with pytest.raises(ValueError, match="Types must be serializable but the following error was thrown during serialization:\n"):
            pybryt.ForbidType(np.ndarray)
