"""Tests for value annotation invariants"""

import numpy as np

from unittest import mock

from pybryt.annotations.invariants import *


def test_call_structure():
    with mock.patch.object(invariant, "run") as mocked_run:
        invariant()
        mocked_run.assert_called()

    assert invariant([]) is None


def test_string_capitalization():
    np.random.seed(42)
    values = ["someString", "some_otherO!I(I*$NDdnnfkf", 120484, ["hi", "there"], np.random.uniform(size=100)]
    expected_values = [s.lower() if isinstance(s, str) else s for s in values]
    np.testing.assert_equal(string_capitalization(values), expected_values)


def test_alias():
    import pybryt.invariants as inv2
    assert inv2.string_capitalization is string_capitalization
