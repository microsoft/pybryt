""""""

import os
import dill
import base64
import tempfile
import nbformat
import numpy as np
import pkg_resources
import pytest

from functools import lru_cache
from textwrap import dedent
from unittest import mock

from pybryt import ReferenceImplementation, Value


@lru_cache(1)
def generate_reference_notebook():
    """
    """
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        import pybryt
    """)))
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        def median(S):
            sorted_S = sorted(S) 
            pybryt.Value(sorted_S, name="sorted", limit=5, success_message="SUCCESS: Sorted the sample correctly", 
                        failure_message="ERROR: The sample was not sorted")
            
            size_of_set = len(S) 
            pybryt.Value(size_of_set, success_message = "SUCCESS: Computed the size of the sample", 
                        failure_message="ERROR: Did not capture the size of the set to determine if it is odd or even")
            
            middle = size_of_set // 2
            is_set_size_even = (size_of_set % 2) == 0

            if is_set_size_even:
                return (sorted_S[middle-1] + sorted_S[middle]) / 2
            else:
                return sorted_S[middle]
    """)))
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        import numpy as np
        np.random.seed(42)
        for _ in range(10):
            vals = [np.random.randint(-1000, 1000) for _ in range(np.random.randint(1, 1000))]
            val = median(vals)
            pybryt.Value(val, success_message="SUCCESS: computed the correct median", 
                failure_message="ERROR: failed to compute the median")
    """)))
    return nb


def test_reference_implementation():
    """
    """
    nb = generate_reference_notebook()

    ref = ReferenceImplementation.compile(nb)

    ref_filename = pkg_resources.resource_filename(__name__, os.path.join("files", "expected_ref.pkl"))
    with open(ref_filename, "rb") as f:
        expected_ref = f.read()

    with tempfile.NamedTemporaryFile() as ntf:
        ref.dump(ntf.name)
        contents = ntf.read()
        assert contents == expected_ref

    # test construction from .py file w/ ReferenceImplementation objects
    ref2_filename = pkg_resources.resource_filename(__name__, os.path.join("files", "expected_ref2.pkl"))
    expected_ref2 = ReferenceImplementation.load(ref2_filename)

    with tempfile.NamedTemporaryFile("w+", suffix=".py") as ntf:
        ntf.write(dedent("""\
            import pybryt
            import numpy as np
            np.random.seed(42)

            def square_evens(arr):
                subarr = arr[arr % 2 == 0]
                v1 = pybryt.Value(subarr)
                subarr = subarr ** 2
                v2 = pybryt.Value(subarr)
                arr = arr.copy()
                arr[arr % 2 == 0] = subarr
                return v1, v2, arr

            annots = []
            for _ in range(10):
                vals = np.array([np.random.randint(-1000, 1000) for _ in range(np.random.randint(1, 1000))])
                v1, v2, val = square_evens(vals)
                annots.append(v1)
                annots.append(v2)
                annots.append(pybryt.Value(val))
            
            ref = pybryt.ReferenceImplementation(annots)
            ref2 = pybryt.ReferenceImplementation([])
        """))

        ntf.seek(0)

        more_refs = ReferenceImplementation.compile(ntf.name)
        assert len(more_refs) == 2
        assert len(more_refs[1].annotations) == 0
        
        ref2 = more_refs[0]
        assert ref2 == expected_ref2


def test_construction_errors():
    """
    """
    with pytest.raises(TypeError, match="annotations should be a list of Annotations"):
        ReferenceImplementation(set())

    with pytest.raises(TypeError, match="Found non-annotation in annotations"):
        ReferenceImplementation([Value(1), Value(2), 3, Value(4)])

    # check that you can't load something that isn't a ReferenceImplementation
    with tempfile.NamedTemporaryFile() as ntf:
        dill.dump([], ntf)

        ntf.seek(0)

        with pytest.raises(TypeError, match="Unpickled reference implementation has type <class 'list'>"):
            ReferenceImplementation.load(ntf.name)

    # check that loading an empty reference implementation gives an error
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
        nbformat.write(nbformat.v4.new_notebook(), ntf)

        ntf.seek(0)

        with pytest.warns(UserWarning, match=f"Could not find any reference implementations in {ntf.name}"):
            ReferenceImplementation.compile(ntf.name)
