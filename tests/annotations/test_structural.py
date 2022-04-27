"""Tests for structural patterns"""

import pandas as pd
import pytest

from unittest import mock

from pybryt import structural
from pybryt.annotations.structural import _StructuralPattern

from .structural_helpers import AttrContainer, Container


def test__getattr__():
    """
    Tests for ``_StructuralPattern.__getattr__``.
    """
    assert isinstance(structural.tests, _StructuralPattern)

    pat = structural.tests.annotations.structural_helpers.AttrContainer()
    assert isinstance(pat, _StructuralPattern)

    # test errors to make sure dill works
    with pytest.raises(AttributeError):
        pat.__getstate__

    with pytest.raises(AttributeError):
        pat.__setstate__

    with pytest.raises(AttributeError):
        pat.__slots__


def test_named_attribute_checking():
    """
    Tests for named attribute checking.
    """
    expected_attrs = dict(a=1, b=2, c=3)
    pat = structural.tests.annotations.structural_helpers.AttrContainer(**expected_attrs)

    obj = AttrContainer(**expected_attrs)
    assert pat == obj

    obj = AttrContainer(**expected_attrs, d=1)
    assert pat == obj

    obj = AttrContainer(**{**expected_attrs, "c": 4})
    assert pat != obj

    expected_attrs.pop("b")
    obj = AttrContainer(**expected_attrs)
    assert pat != obj

    expected_attrs["df"] = structural.pandas.DataFrame(shape=(2, 1))
    pat = structural.tests.annotations.structural_helpers.AttrContainer(**expected_attrs)
    obj = AttrContainer(**{**expected_attrs, "df": pd.DataFrame({"a": [1, 2]})})
    assert pat == obj

    obj = AttrContainer(**{**expected_attrs, "df": pd.DataFrame({"a": [1, 2], "b": [3, 4]})})
    assert pat != obj


def test_unnamed_attribute_checking():
    """
    Tests for unnamed attribute checking.
    """
    expected_attrs = dict(a=1, b=2, c=3)
    pat = structural.tests.annotations.structural_helpers.AttrContainer(*expected_attrs.values())

    obj = AttrContainer(**expected_attrs)
    assert pat == obj

    obj = AttrContainer(**expected_attrs, d=1)
    assert pat == obj

    obj = AttrContainer(**{**expected_attrs, "c": 4})
    assert pat != obj

    expected_attrs.pop("b")
    obj = AttrContainer(**expected_attrs)
    assert pat != obj


def test_contains():
    """
    Tests for patterns checking whether an object is contained in a matching object.
    """
    expected_elems = [1, 2, 3]
    pat = structural.tests.annotations.structural_helpers.Container().contains_(*expected_elems)

    obj = Container(*expected_elems)
    assert pat == obj

    obj = Container(*expected_elems, 4)
    assert pat == obj

    obj = Container(*expected_elems[:-1])
    assert pat != obj

    with mock.patch.object(Container, "__contains__") as mocked_contains:
        mocked_contains.side_effect = TypeError()
        obj = Container(*expected_elems)
        assert pat != obj


def test___repr__():
    """
    Tests for ``_StructuralPattern.__repr__``.
    """
    expected_attrs = dict(a=1, b=2, c=3)
    pat = structural.tests.annotations.structural_helpers.AttrContainer(**expected_attrs)
    pat_repr = repr(pat)
    assert pat_repr.startswith("pybryt.structural.tests.annotations.structural_helpers.AttrContainer(")
    for k, v in expected_attrs.items():
        assert f"{k}={v}" in pat_repr

