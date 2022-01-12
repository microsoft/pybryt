"""Tests for import annotations"""

import pytest

from unittest import mock

import pybryt
from pybryt.execution.memory_footprint import MemoryFootprint

from .utils import assert_object_attrs


IMPORTED_MODULES = ["numpy", "pandas", "matplotlib"]


def generate_import_mfp():
    footprint = MemoryFootprint()
    footprint.add_imports(*IMPORTED_MODULES)
    return footprint


@mock.patch.multiple(pybryt.ImportAnnotation, __abstractmethods__=frozenset())
def test_import_init_behaviors():
    """
    """
    with mock.patch("pybryt.annotations.import_.importlib") as mocked_importlib, \
            mock.patch("pybryt.annotations.import_.sys") as mocked_sys:
        pybryt.ImportAnnotation("foo")
        mocked_importlib.import_module.assert_called_with("foo")
        mocked_sys.modules.pop.assert_called_with("foo")

        mocked_sys.modules = {"foo": None}
        pybryt.ImportAnnotation("foo")
        assert mocked_sys.modules == {"foo": None}

        with pytest.raises(TypeError):
            pybryt.ImportAnnotation(1)

        mocked_importlib.import_module.side_effect = ImportError()
        with pytest.raises(ValueError):
            pybryt.ImportAnnotation("foo")


def test_require_import():
    """
    """
    footprint = generate_import_mfp()
    pybryt.Annotation.reset_tracked_annotations()

    with mock.patch("pybryt.annotations.import_.importlib") as mocked_importlib, \
            mock.patch("pybryt.annotations.import_.sys") as mocked_sys:
        a = pybryt.RequireImport(IMPORTED_MODULES[0])
        b = pybryt.RequireImport("foo")

    res1 = a.check(footprint)

    assert_object_attrs(a, {"children__len": 0})
    assert_object_attrs(res1, {
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
        "type": "requireimport",
        "module": IMPORTED_MODULES[0],
    }

    res2 = b.check(footprint)
    assert not res2.satisfied



def test_forbid_import():
    """
    """
    footprint = generate_import_mfp()
    pybryt.Annotation.reset_tracked_annotations()

    with mock.patch("pybryt.annotations.import_.importlib") as mocked_importlib, \
            mock.patch("pybryt.annotations.import_.sys") as mocked_sys:
        a = pybryt.ForbidImport("foo")
        b = pybryt.ForbidImport(IMPORTED_MODULES[0])

    res1 = a.check(footprint)

    assert_object_attrs(a, {"children__len": 0})
    assert_object_attrs(res1, {
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
        "type": "forbidimport",
        "module": "foo",
    }

    res2 = b.check(footprint)
    assert not res2.satisfied
