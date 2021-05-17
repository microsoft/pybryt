""""""

import pytest
import numpy as np

from pybryt import *
from pybryt import complexities as cplx
from pybryt.execution.complexity import TimeComplexityResult

from .utils import check_obj_attributes


def generate_complexity_footprint(name, t_transform, max_exp=8):
    footprint = []
    for i, e in enumerate(range(1, max_exp + 1)):
        n = 10 ** e
        t = t_transform(n)
        footprint.append((TimeComplexityResult(name, n, 0, t), i))
    return footprint


def test_complexity_abc():
    """
    """
    Annotation.reset_tracked_annotations()

    a = TimeComplexity(cplx.constant, name="foo")
    check_obj_attributes(a, {
        "name": "foo",
        "complexity": cplx.constant,
    })

    b = TimeComplexity(cplx.constant, name="foo")
    assert a == b

    b.complexity = cplx.linear
    assert a != b

    b.name = "bar"
    assert a != b

    b.complexity = cplx.constant
    assert a != b

    # test constructor errors
    with pytest.raises(ValueError, match="Complexity annotations require a 'name' kwarg"):
        TimeComplexity(cplx.constant)

    with pytest.raises(ValueError, match="Invalid valid for argument 'complexity': 1"):
        TimeComplexity(1, name="foo")


def test_time_complexity():
    Annotation.reset_tracked_annotations()

    a = TimeComplexity(cplx.constant, name="foo")

    footprint = generate_complexity_footprint("foo", lambda v: 1012)
    res = a.check(footprint)
    assert res.satisfied
    assert res.value == cplx.constant

    footprint.append((np.random.uniform(size=100), 9))
    footprint.append((TimeComplexityResult("bar", 10, 0, 10 ** 3), 10))
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
    import pybryt.complexities as cplx2
    assert cplx.complexity_classes is cplx2.complexity_classes
