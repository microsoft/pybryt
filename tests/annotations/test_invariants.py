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


def test_matrix_transpose():
    np.random.seed(42)
    arr = np.random.uniform(size=(10,10))
    values = ["someString", "some_otherO!I(I*$NDdnnfkf", 120484, ["hi", "there"], arr, [[1, 2, 3], [4, 5, 6]]]
    print(matrix_transpose(values))
    expected_values = ["someString", "some_otherO!I(I*$NDdnnfkf", 120484, ["hi", "there"], ["hi", "there"], \
        arr, arr.T, [[1, 2, 3], [4, 5, 6]], [[1, 4], [2, 5], [3, 6]]]
    np.testing.assert_equal(matrix_transpose(values), expected_values)


def test_list_permutation():
    np.random.seed(42)
    arr = np.random.uniform(size=(10,10))
    values = ["someString", "some_otherO!I(I*$NDdnnfkf", 120484, ["there", "hi", "z"], arr, [[1, 2, 3], [4, 5, 6]]]
    expected_values = ["someString", "some_otherO!I(I*$NDdnnfkf", 120484, ["hi", "there", "z"], np.sort(arr),  \
        [[1, 2, 3], [4, 5, 6]]]
    np.testing.assert_equal(list_permutation(values), expected_values)


def test_alias():
    import pybryt.invariants as inv2
    assert inv2.string_capitalization is string_capitalization
