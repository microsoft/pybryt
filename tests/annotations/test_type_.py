"""Tests for PyBryt type annotations"""

import time
import pytest
import numpy as np

from unittest import mock

from pybryt import *
from pybryt.utils import pickle_and_hash

from .utils import *


def test_forbid_type():
    """
    """
    mfp = generate_memory_footprint()
    Annotation.reset_tracked_annotations()

    a = ForbidType(bool)
    res = a.check(mfp)

    check_obj_attributes(a, {"children__len": 0})
    check_obj_attributes(res, {
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

    a = ForbidType(np.ndarray)
    res = a.check(mfp)
    check_obj_attributes(res, {
        "children": [],
        "satisfied": False,
        "_satisfied": False,
        "annotation": a,
        "timestamp": -1,
        "value": None,
    })

    # check constructor errors
    with pytest.raises(TypeError, match=f"1 is not a type"):
        ForbidType(1)

    with mock.patch("pybryt.annotations.type_.dill") as mocked_dill:
        mocked_dill.dumps.side_effect = Exception()

        with pytest.raises(ValueError, match="Types must be serializable but the following error was thrown during serialization:\n"):
            ForbidType(np.ndarray)
