"""Tests for memory footprint objects"""

import nbformat
import pytest

from copy import deepcopy
from itertools import chain
from unittest import mock

from pybryt.execution.memory_footprint import Counter, MemoryFootprint

from ..annotations.utils import generate_memory_footprint


def generate_values():
    return [(o, i + 1) for i, o in enumerate([10, "", True, None, 10039, 1e-4])]


def test_counter():
    """
    """
    counter = Counter()
    assert counter.get_value() == 0
    counter.increment()
    assert counter.get_value() == 1
    offset = 10
    counter.offset(offset)
    assert counter.get_value() == 1 + offset


def test_memory_footprint_constructor():
    footprint = MemoryFootprint()
    assert footprint.counter is not None
    assert len(footprint.values) == 0
    assert len(footprint.calls) == 0
    assert len(footprint.imports) == 0

    counter = Counter()
    counter.offset(50)
    footprint = MemoryFootprint(counter)
    assert footprint.counter is counter
    assert len(footprint.values) == 0
    assert len(footprint.calls) == 0
    assert len(footprint.imports) == 0


def test_from_values():
    vals = generate_values()
    footprint = MemoryFootprint.from_values(*chain.from_iterable(vals))
    assert footprint.values == vals
    assert footprint.num_steps == len(vals)
    assert footprint.counter.get_value() == len(vals)

    # check errors
    with pytest.raises(ValueError):
        MemoryFootprint.from_values(1, 1, 1)

    with pytest.raises(TypeError):
        MemoryFootprint.from_values([1], 1, True, 2.0)


def test_combine():
    vals = generate_values()
    v1, v2 = vals[:3], vals[3:]
    v2.extend(v1)

    f1, f2 = MemoryFootprint.from_values(*chain.from_iterable(v1)), MemoryFootprint.from_values(*chain.from_iterable(v2))
    footprint = MemoryFootprint.combine(f1, f2)

    sorted_fp_vals = sorted(footprint.values, key=lambda t: t[1])
    assert list(map(lambda t: t[0], sorted_fp_vals)) == list(map(lambda t: t[0], vals))
    assert footprint.counter.get_value() == len(v1) + len(v2)


def test_counter_manipulation():
    footprint = MemoryFootprint()
    footprint.increment_counter()
    assert footprint.counter.get_value() == 1
    footprint.offset_counter(50)
    assert footprint.counter.get_value() == 51


def test_values():
    footprint = MemoryFootprint()
    footprint.add_value(1)
    assert len(footprint.values) == 1
    assert footprint.get_value(0) == 1
    assert footprint.get_timestamp(0) == 0

    footprint.increment_counter()
    footprint.add_value(2)
    assert len(footprint.values) == 2
    assert footprint.get_value(1) == 2
    assert footprint.get_timestamp(1) == 1

    footprint.add_value(3, 10)
    assert len(footprint.values) == 3
    assert footprint.get_value(2) == 3
    assert footprint.get_timestamp(2) == 10


def test_calls():
    footprint = MemoryFootprint()
    footprint.add_call("foo", "bar")
    assert footprint.calls == [("foo", "bar")]


def test_imports():
    footprint = MemoryFootprint()
    imports = {"a", "b", "c", "d"}
    footprint.add_imports(*imports)
    assert footprint.imports == imports

    footprint.add_imports("a")
    assert footprint.imports == imports
    assert sum(i == "a" for i in footprint.imports) == 1


def test_set_executed_notebook():
    footprint = MemoryFootprint()
    assert footprint.executed_notebook == None

    nb = nbformat.v4.new_notebook()
    footprint.set_executed_notebook(nb)
    assert footprint.executed_notebook is nb


def test_filter_out_unpicklable_values():
    vals = generate_values()
    footprint = MemoryFootprint.from_values(*chain.from_iterable(vals))

    with mock.patch("pybryt.execution.memory_footprint.filter_picklable_list") as mocked_filter:
        footprint.filter_out_unpicklable_values()
        mocked_filter.assert_called_once_with(footprint.values)


def test_eq():
    vals = generate_values()
    f1, f2 = MemoryFootprint.from_values(*chain.from_iterable(vals)), MemoryFootprint()
    f3 = deepcopy(f1)

    assert f1 != f2
    assert f1 == f3
