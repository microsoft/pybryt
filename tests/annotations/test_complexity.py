"""Tests for complexity annotations"""

from typing import Type
import numpy as np
from numpy.lib.arraysetops import isin
import pytest

import pybryt
import pybryt.complexities as cplx

from pybryt.execution import MemoryFootprintValue

from .utils import assert_object_attrs


def generate_complexity_footprint(name, t_transform, max_exp=8):
    values = []
    for i, e in enumerate(range(1, max_exp + 1)):
        n = 10 ** e
        t = t_transform(n)
        values.append(MemoryFootprintValue(pybryt.TimeComplexityResult(name, n, 0, t), i, None))
    return pybryt.MemoryFootprint.from_values(*values)


def test_complexity_abc():
    """
    """
    pybryt.Annotation.reset_tracked_annotations()

    a =  pybryt.TimeComplexity(cplx.constant, name="foo")
    assert_object_attrs(a, {
        "name": "foo",
        "complexity": cplx.constant,
    })

    b =  pybryt.TimeComplexity(cplx.constant, name="foo")
    assert a == b

    b.complexity = cplx.linear
    assert a != b

    b.name = "bar"
    assert a != b

    b.complexity = cplx.constant
    assert a != b

    # test constructor errors
    with pytest.raises(ValueError, match="Complexity annotations require a 'name' kwarg"):
         pybryt.TimeComplexity(cplx.constant)

    with pytest.raises(ValueError, match="Invalid valid for argument 'complexity': 1"):
         pybryt.TimeComplexity(1, name="foo")


def test_time_complexity():
    pybryt.Annotation.reset_tracked_annotations()

    a =  pybryt.TimeComplexity(cplx.constant, name="foo")

    footprint = generate_complexity_footprint("foo", lambda v: 1012)
    res = a.check(footprint)
    assert res.satisfied
    assert res.value == cplx.constant

    footprint.add_value(np.random.uniform(size=100), 9)
    footprint.add_value( pybryt.TimeComplexityResult("bar", 10, 0, 10 ** 3), 10)
    res = a.check(footprint)
    assert res.satisfied
    assert res.value == cplx.constant

    footprint = generate_complexity_footprint("foo", np.log2)
    res = a.check(footprint)
    assert not res.satisfied
    assert res.value == cplx.logarithmic

    footprint = generate_complexity_footprint("foo", lambda v: v * np.log2(v))
    res = a.check(footprint)
    assert not res.satisfied
    assert res.value == cplx.linearithmic

    a.complexity = cplx.exponential
    res = a.check(footprint)
    assert not res.satisfied
    assert res.value == cplx.linearithmic


def test_alias():
    from pybryt.annotations.complexity import complexities as cplx2
    assert cplx.complexity_classes is cplx2.complexity_classes


def test_complexity_union():
    """
    Tests for complexity unions.
    """
    union = cplx.logarithmic | cplx.linear
    assert isinstance(union, cplx.ComplexityUnion)
    assert set(union.get_complexities()) == {cplx.logarithmic, cplx.linear}

    union2 = union | cplx.constant
    assert isinstance(union2, cplx.ComplexityUnion)
    assert set(union2.get_complexities()) == {cplx.logarithmic, cplx.linear, cplx.constant}

    union3 = cplx.constant | union
    assert isinstance(union3, cplx.ComplexityUnion)
    assert set(union3.get_complexities()) == {cplx.logarithmic, cplx.linear, cplx.constant}

    union4 = union2 | union
    assert isinstance(union4, cplx.ComplexityUnion)
    assert set(union4.get_complexities()) == {cplx.logarithmic, cplx.linear, cplx.constant}

    union.add_complexity(cplx.linearithmic)
    assert set(union.get_complexities()) == {cplx.logarithmic, cplx.linear, cplx.linearithmic}

    assert union == cplx.logarithmic | cplx.linear | cplx.linearithmic
    assert union != cplx.logarithmic | cplx.linear

    # test whether the union works with annotations
    a = pybryt.TimeComplexity(cplx.constant | cplx.logarithmic, name="foo")
    footprint = generate_complexity_footprint("foo", lambda v: 1012)
    res = a.check(footprint)
    assert res.satisfied
    assert res.value == cplx.constant

    footprint = generate_complexity_footprint("foo", lambda v: v)
    res = a.check(footprint)
    assert not res.satisfied
    assert res.value == cplx.linear

    # test errors
    with pytest.raises(TypeError):
        cplx.constant | 1

    with pytest.raises(TypeError):
        cplx.ComplexityUnion.from_or(1, cplx.constant)
