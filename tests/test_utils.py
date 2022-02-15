""""""

import pytest
import random
import tempfile

from textwrap import dedent
from unittest import mock

from pybryt.utils import *

from .test_reference import generate_reference_notebook


def test_filter_pickleable_list():
    """
    """
    l = [1, 2, 3]
    filter_pickleable_list(l)
    assert len(l) == 3

    with mock.patch("dill.dumps") as mocked_dill:
        mocked_dill.side_effect = Exception()
        filter_pickleable_list(l)
        assert len(l) == 0


def test_notebook_to_string():
    """
    """
    ref = generate_reference_notebook()
    s = notebook_to_string(ref)
    assert s.strip() == dedent("""\
        import pybryt

        def median(S):
            sorted_S = sorted(S) 
            pybryt.Value(sorted_S, name="sorted", group="median", limit=5, success_message="SUCCESS: Sorted the sample correctly", 
                        failure_message="ERROR: The sample was not sorted")

            size_of_set = len(S) 
            pybryt.Value(size_of_set, name="size", group="median", success_message = "SUCCESS: Computed the size of the sample", 
                        failure_message="ERROR: Did not capture the size of the set to determine if it is odd or even")

            middle = size_of_set // 2
            is_set_size_even = (size_of_set % 2) == 0

            if is_set_size_even:
                return (sorted_S[middle-1] + sorted_S[middle]) / 2
            else:
                return sorted_S[middle]

        import numpy as np
        np.random.seed(42)
        for _ in range(10):
            vals = [np.random.randint(-1000, 1000) for _ in range(np.random.randint(1, 1000))]
            val = median(vals)
            pybryt.Value(val, name="median", group="median", success_message="SUCCESS: computed the correct median", 
                failure_message="ERROR: failed to compute the median")
    """).strip()

    with pytest.raises(TypeError, match="invalid notebook type"):
        notebook_to_string(1)


def test_make_secret():
    """
    """
    random.seed(42)
    s = make_secret()
    assert s == "HBRPOI"


def test_save_notebook():
    """
    """
    with mock.patch("pybryt.utils.get_ipython") as mocked_get:
        with mock.patch("pybryt.utils.publish_display_data") as mocked_pub:
            mocked_get.return_value = True
            with tempfile.NamedTemporaryFile(suffix=".ipynb") as ntf:
                v = save_notebook(ntf.name, timeout=1)
                mocked_pub.assert_called()
                assert not v
