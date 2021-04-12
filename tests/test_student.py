""""""

import tempfile
import nbformat
import pytest

from functools import lru_cache
from textwrap import dedent
from unittest import mock

from pybryt import ReferenceImplementation, ReferenceResult, StudentImplementation

from .test_reference import generate_reference_notebook


def generate_student_notebook():
    """
    """
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        import pybryt
    """)))
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        def median(S):
            sorted_S = sorted(S)
            size_of_set = len(S)
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
    """)))
    return nb


@lru_cache(1)
def generate_impl():
    nb = generate_student_notebook()
    return nb, StudentImplementation(nb)


def test_constructor():
    """
    """
    nb, stu = generate_impl()
    assert stu.nb is nb
    assert stu.steps == max(t[1] for t in stu.values)
    assert len(stu.values) == 993

    with mock.patch("pybryt.student.execute_notebook") as mocked_exec:
        mocked_exec.return_value = (0, [])

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
            nbformat.write(nb, ntf.name)

            stu = StudentImplementation(ntf.name)
            assert stu.steps == 0
            assert stu.values == []
            assert stu.nb == nb

    with pytest.raises(TypeError, match="path_or_nb is of unsupported type <class 'int'>"):
        StudentImplementation(1)


def test_load_and_dump():
    """
    """
    _, stu = generate_impl()
    with tempfile.NamedTemporaryFile() as ntf:
        stu.dump(ntf.name)
        stu2 = StudentImplementation.load(ntf.name)

        assert len(stu.values) == len(stu2.values)
        assert stu.steps == stu2.steps

    enc_stu = stu.dumps()
    stu2 = StudentImplementation.loads(enc_stu)
    assert len(stu.values) == len(stu2.values)
    assert stu.steps == stu2.steps


def test_check():
    """
    """
    ref = ReferenceImplementation.compile(generate_reference_notebook())
    nb, stu = generate_impl()

    res = stu.check(ref)
    assert isinstance(res, ReferenceResult)

    res = stu.check([ref])
    assert isinstance(res, list) and len(res) == 1 and isinstance(res[0], ReferenceResult)

    with pytest.raises(TypeError, match="check cannot take values of type <class 'int'>"):
        stu.check(1)
