"""Tests for memory footprint objects"""

import nbformat
import pytest

from copy import deepcopy
from itertools import chain
from unittest import mock

from pybryt.execution.memory_footprint import (
    Counter, Event, MemoryFootprint, MemoryFootprintIterator, MemoryFootprintValue)


def generate_values():
    """
    Generate a list of memory footprint values for use in constructing memory footprints.

    Returns:
        ``list[MemoryFootprintValue]``: the values
    """
    return [MemoryFootprintValue(o, i + 1, None) for i, o in \
        enumerate([10, "", True, None, 10039, 1e-4])]


def test_counter():
    """
    Test the ``pybryt.execution.memory_footprint.Counter`` class.
    """
    counter = Counter()
    assert counter.get_value() == 0
    counter.increment()
    assert counter.get_value() == 1
    offset = 10
    counter.offset(offset)
    assert counter.get_value() == 1 + offset


def test_memory_footprint_constructor():
    """
    Test the constructor for ``pybryt.execution.memory_footprint.MemoryFootprint``.
    """
    footprint = MemoryFootprint()
    assert footprint.counter is not None
    assert len(footprint) == 0
    assert len(footprint.calls) == 0
    assert len(footprint.imports) == 0

    counter = Counter()
    counter.offset(50)
    footprint = MemoryFootprint(counter)
    assert footprint.counter is counter
    assert len(footprint) == 0
    assert len(footprint.calls) == 0
    assert len(footprint.imports) == 0


def test_from_values():
    """
    Test the ``pybryt.execution.memory_footprint.MemoryFootprint.from_values`` method.
    """
    vals = generate_values()
    footprint = MemoryFootprint.from_values(*vals)
    assert list(footprint) == vals
    assert footprint.num_steps == len(vals)
    assert footprint.counter.get_value() == len(vals)

    # check errors
    with pytest.raises(TypeError):
        MemoryFootprint.from_values(MemoryFootprintValue(1, 1, None), 2)


def test_combine():
    """
    Test the ``pybryt.execution.memory_footprint.MemoryFootprint.combine`` method.
    """
    vals = generate_values()
    v1, v2 = vals[:3], vals[3:]
    v2.extend(v1)

    f1, f2 = MemoryFootprint.from_values(*v1), MemoryFootprint.from_values(*v2)
    footprint = MemoryFootprint.combine(f1, f2)

    sorted_fp_vals = sorted(list(footprint), key=lambda mfp_val: mfp_val.timestamp)
    assert list(map(lambda mfp_val: mfp_val.value, sorted_fp_vals)) == list(map(lambda mfp_val: mfp_val.value, vals))
    assert footprint.counter.get_value() == len(v1) + len(v2)


def test_counter_manipulation():
    """
    Test counter manipulations for the ``MemoryFootprint`` class.
    """
    footprint = MemoryFootprint()
    footprint.increment_counter()
    assert footprint.counter.get_value() == 1
    footprint.offset_counter(50)
    assert footprint.counter.get_value() == 51


def test_values():
    """
    Test value updates and accesses for the ``MemoryFootprint`` class.
    """
    footprint = MemoryFootprint()
    footprint.add_value(1)
    assert len(footprint) == 1
    assert footprint.get_value(0).value == 1
    assert footprint.get_value(0).timestamp == 0

    footprint.increment_counter()
    footprint.add_value(2)
    assert len(footprint) == 2
    assert footprint.get_value(1).value == 2
    assert footprint.get_value(1).timestamp == 1
    assert footprint.get_value(1).event is None

    footprint.add_value(3, 10)
    assert len(footprint) == 3
    assert footprint.get_value(2).value == 3
    assert footprint.get_value(2).timestamp == 10

    footprint.increment_counter()
    footprint.add_value(2, event=Event.LINE)
    assert len(footprint) == 3
    assert footprint.get_value(1).event == Event.LINE

    footprint.add_value(2)
    assert len(footprint) == 3
    assert footprint.get_value(1).event == Event.LINE

    footprint.add_value(2, event=Event.RETURN)
    assert len(footprint) == 3
    assert footprint.get_value(1).event == Event.LINE_AND_RETURN


def test_calls():
    """
    Test call tracking for the ``MemoryFootprint`` class.
    """
    footprint = MemoryFootprint()
    footprint.add_call("foo", "bar")
    assert footprint.calls == [("foo", "bar")]


def test_imports():
    """
    Test import tracking for the ``MemoryFootprint`` class.
    """
    footprint = MemoryFootprint()
    imports = {"a", "b", "c", "d"}
    footprint.add_imports(*imports)
    assert footprint.imports == imports

    footprint.add_imports("a")
    assert footprint.imports == imports
    assert sum(i == "a" for i in footprint.imports) == 1


def test_set_executed_notebook():
    """
    Test executed notebook tracking for the ``MemoryFootprint`` class.
    """
    footprint = MemoryFootprint()
    assert footprint.executed_notebook == None

    nb = nbformat.v4.new_notebook()
    footprint.set_executed_notebook(nb)
    assert footprint.executed_notebook is nb


def test_filter_out_unpickleable_values():
    """
    Test pickleable value filtering tracking for the ``MemoryFootprint`` class.
    """
    vals = generate_values()
    footprint = MemoryFootprint.from_values(*vals)

    with mock.patch("pybryt.execution.memory_footprint.filter_pickleable_list") as mocked_filter:
        footprint.filter_out_unpickleable_values()
        mocked_filter.assert_called_once_with(footprint.values)


def test_eq():
    """
    Test ``MemoryFootprint`` equals comparisons.
    """
    vals = generate_values()
    f1, f2 = MemoryFootprint.from_values(*vals), MemoryFootprint()
    f3 = deepcopy(f1)

    assert f1 != f2
    assert f1 == f3


def test_misc_dunder_methods():
    """
    Tests for misc. dunder methods of ``MemoryFootprint``.
    """
    vals = generate_values()
    fp = MemoryFootprint.from_values(*vals)

    assert len(fp) == len(vals)

    fpi = iter(fp)
    assert isinstance(fpi, MemoryFootprintIterator)
    for e, a in zip(vals, fp):
        assert isinstance(a, MemoryFootprintValue)
        assert e == a


