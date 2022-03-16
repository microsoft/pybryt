"""Tests for initial conditions"""

import numpy as np
import operator

from unittest import mock

import pytest

from pybryt import InitialCondition
from pybryt.execution.memory_footprint import MemoryFootprint, MemoryFootprintValue

from .utils import assert_object_attrs


def test_constructor():
    """
    Tests for the ``InitialCondition`` constructor.
    """
    name = "foo"
    transforms = [lambda x: 2 * x, lambda x: np.cos(x)]
    ic = InitialCondition(name, transforms)
    assert_object_attrs(ic, {
        "name": name,
        "transforms": transforms,
    })

    # test errors
    with pytest.raises(TypeError):
        InitialCondition(2)


def test_apply():
    """
    Tests for ``InitialCondition.apply``.
    """
    name = "foo"
    transforms = [lambda x: 2 * x, lambda x: np.cos(x)]
    ic = InitialCondition(name, transforms)

    new_transform = lambda x: np.sin(x)
    ic2 = ic.apply(new_transform)

    assert isinstance(ic2, InitialCondition) and ic2 is not ic
    assert_object_attrs(ic2, {
        "name": name,
        "transforms": transforms + [new_transform],
    })


def test_supply_value():
    """
    Tests for ``InitialCondition.supply_value``.
    """
    name = "foo"
    transforms = [mock.MagicMock() for _ in range(10)]
    ic = InitialCondition(name, transforms)

    val = 2
    res = ic.supply_value(val)

    expected_arg = val
    for t in transforms:
        t.assert_called_once_with(expected_arg)
        expected_arg = t.return_value

    assert res == transforms[-1].return_value


def test_supply_footprint_and_supply_values():
    """
    Tests for ``InitialCondition.supply_footprint`` and ``InitialCondition.supply_values``.
    """
    name = "foo"
    transforms = [mock.MagicMock() for _ in range(10)]
    ic = InitialCondition(name, transforms)

    val = 2
    mocked_fp = mock.MagicMock()
    mocked_fp.get_initial_conditions.return_value = {name: val}

    res = ic.supply_footprint(mocked_fp)

    mocked_fp.get_initial_conditions.assert_called_once()

    expected_arg = val
    for t in transforms:
        t.assert_called_once_with(expected_arg)
        expected_arg = t.return_value

    assert res == transforms[-1].return_value

    # test nested initial conditions
    n1, n2, v1, v2 = "foo", "bar", 2, 3
    ic1, ic2 = InitialCondition(n1), InitialCondition(n2)
    vals = {n1: v1, n2: v2}
    ic3 = ic1 + ic2
    assert ic3.supply_values(vals) == v1 + v2

    # test errors
    with pytest.raises(ValueError, match=f"The provided values do not have key '{name}'"):
        ic.supply_values({"bar": 1})


def test_eq():
    """
    Tests for ``==`` comparisons on ``InitialCondition``s.
    """
    ic1, ic2, ic3 = InitialCondition("foo"), InitialCondition("foo"), InitialCondition("bar")

    assert ic1 == ic2
    assert ic1 != ic3

    t = lambda v: 2 * v
    ic2 = ic2.apply(t)
    assert ic1 != ic2

    ic1 = ic1.apply(t)
    assert ic1 == ic2


def test_operators():
    """
    Tests for the use of operators on ``InitialCondition``s.
    """
    ic = InitialCondition("foo")
    l, r, m = 2, 3, 4

    def test_op(op, right, use_m=False):
        if right:
            if use_m:
                op_ic = op(l, ic, m)
            else:
                op_ic = op(l, ic)

        else:
            if use_m:
                op_ic = op(ic, r, m)
            else:
                op_ic = op(ic, r)

        if use_m:
            exp = op(l, r, m)
        else:
            exp = op(l, r)

        assert isinstance(op_ic, InitialCondition)

        eq = op_ic.supply_value(r if right else l) == exp
        if isinstance(exp, np.ndarray):
            assert eq.all()
        else:
            assert eq

    # test binary ops
    bin_ops = [
        operator.add, operator.sub, operator.mul, operator.truediv, operator.floordiv, operator.mod,\
        operator.pow, operator.lshift, operator.rshift, operator.and_, operator.xor, operator.or_,
        divmod,
    ]
    for op in bin_ops:
        test_op(op, False)
        test_op(op, True)

    # test ternary pow
    test_op(pow, False, use_m=True)

    # test unary ops
    unary_ops = [operator.neg, operator.pos, operator.abs, operator.invert]
    for op in unary_ops:
        op_ic = op(ic)
        assert isinstance(op_ic, InitialCondition)
        assert op_ic.supply_value(l) == op(l)

    # test matmul
    l, r = mock.MagicMock(), mock.MagicMock()
    test_op(operator.matmul, False)
    l.__matmul__.assert_called_with(r)

    l = mock.Mock()
    test_op(operator.matmul, True)
    r.__rmatmul__.assert_called_with(l)
