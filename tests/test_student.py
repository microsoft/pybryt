""""""

import os
import tempfile
import nbformat
import pytest
import pkg_resources

from copy import deepcopy
from functools import lru_cache
from textwrap import dedent
from types import MethodType
from unittest import mock

from pybryt import (
    check, generate_student_impls, ReferenceImplementation, ReferenceResult, StudentImplementation
)

from .test_reference import generate_reference_notebook


__PYBRYT_TRACING__ = False


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
    assert isinstance(stu.calls, list)
    assert all(isinstance(c, tuple) for c in stu.calls)
    assert all(len(c) == 2 for c in stu.calls)
    assert all(isinstance(c[0], str) for c in stu.calls)
    assert all(isinstance(c[1], str) for c in stu.calls)

    with mock.patch("pybryt.student.execute_notebook") as mocked_exec:
        mocked_exec.return_value = (0, [], [], None)

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
            nbformat.write(nb, ntf.name)

            stu = StudentImplementation(ntf.name)
            assert stu.steps == 0
            assert stu.values == []
            assert stu.calls == []
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
    ref = ReferenceImplementation.compile(generate_reference_notebook(), name="foo")
    nb, stu = generate_impl()

    res = stu.check(ref)
    assert isinstance(res, ReferenceResult)

    res = stu.check([ref])
    assert isinstance(res, list) and len(res) == 1 and isinstance(res[0], ReferenceResult)

    with pytest.raises(TypeError, match="check cannot take values of type <class 'int'>"):
        stu.check(1)


def test_errors():
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("raise Exception()"))

    with pytest.warns(UserWarning, match="Executing student notebook produced errors in the notebook"):
        stu = StudentImplementation(nb)

    assert len(stu.errors) == 1
    assert stu.errors[0]["ename"] == "Exception"
    assert stu.errors[0]["evalue"] == ""
    assert stu.errors[0]["output_type"] == "error"
    assert isinstance(stu.errors[0]["traceback"], list)
    assert len(stu.errors[0]) == 4
    

def test_check_cm(capsys):
    """
    """
    ref = ReferenceImplementation.compile(generate_reference_notebook(), name="foo")
    _, stu = generate_impl()
    mfp = stu.values

    with mock.patch.object(check, "_cache_check") as mocked_cache:
        with mock.patch("pybryt.student.tracing_on") as mocked_tracing, mock.patch("pybryt.student.tracing_off"):
            check_cm = check(ref, cache=False)
            with check_cm:
                check_cm._observed = mfp

            mocked_cache.assert_not_called()

        captured = capsys.readouterr()
        expected = dedent("""\
            REFERENCE: foo
            SATISFIED: True
            MESSAGES:
              - SUCCESS: Sorted the sample correctly
              - SUCCESS: Computed the size of the sample
              - SUCCESS: computed the correct median
        """)
        assert captured.out == expected

        with mock.patch("pybryt.student.tracing_on") as mocked_tracing, mock.patch("pybryt.student.tracing_off"):
            ref_filename = pkg_resources.resource_filename(__name__, os.path.join("files", "expected_ref.pkl"))
            check_cm = check(ref_filename)
            with check_cm:
                check_cm._observed = mfp

            mocked_cache.assert_called()

            check_cm2 = check([ref_filename])
            assert check_cm._ref == check_cm2._ref

        captured = capsys.readouterr()
        expected = dedent("""\
            REFERENCE: foo
            SATISFIED: True
            MESSAGES:
              - SUCCESS: Sorted the sample correctly
              - SUCCESS: Computed the size of the sample
              - SUCCESS: computed the correct median
        """)
        assert captured.out == expected

        # check no action when tracing
        global __PYBRYT_TRACING__
        __PYBRYT_TRACING__ = True

        try:
            with mock.patch("pybryt.student.tracing_on") as mocked_tracing, mock.patch("pybryt.student.tracing_off"):
                check_cm = check(ref)
                with check_cm:
                    pass

                mocked_tracing.assert_not_called()

        except:
            __PYBRYT_TRACING__ = False
            raise

        else:
            __PYBRYT_TRACING__ = False

        # test errors
        with pytest.raises(ValueError, match="Cannot check against an empty list of references"):
            check([])

        with pytest.raises(TypeError, match="Invalid values in the reference list"):
            check([ref, "path", 1])

    # check caching
    with mock.patch("pybryt.student.tracing_on") as mocked_tracing, mock.patch("pybryt.student.tracing_off"):
        with mock.patch("pybryt.student.StudentImplementation") as mocked_stu, \
                mock.patch("pybryt.student.generate_report") as mocked_generate, \
                mock.patch("pybryt.student.os.makedirs") as mocked_makedirs:
            mocked_stu.from_footprint.return_value.check.return_value = [mock.MagicMock()]
            mocked_stu.from_footprint.return_value.check.return_value[0].name = "foo"
            # breakpoint()
            check_cm = check(ref)
            with check_cm:
                check_cm._observed = mfp
            
            mocked_makedirs.assert_called_with(".pybryt_cache", exist_ok=True)
            mocked_stu.from_footprint.return_value.dump.assert_called()
            mocked_stu.from_footprint.return_value.check.return_value[0].dump.assert_called_with(".pybryt_cache/foo_results.pkl")


def test_from_cache():
    """
    """
    with mock.patch("pybryt.student.glob") as mocked_glob, \
            mock.patch.object(StudentImplementation, "load") as mocked_load, \
            mock.patch.object(StudentImplementation, "combine") as mocked_combine:
        mocked_glob.return_value = [".pybryt_cache/student_impl_foo.pkl", ".pybryt_cache/student_impl_bar.pkl"]
        StudentImplementation.from_cache(combine=False)

        mocked_load.assert_has_calls([mock.call(fp) for fp in mocked_glob.return_value])
        mocked_combine.assert_not_called()

        StudentImplementation.from_cache()

        mocked_combine.assert_called()


def test_combine():
    """
    """
    _, stu = generate_impl()
    stu2 = deepcopy(stu)
    stu2.steps += 1
    stu2.values.append(([1, 2, 3, 4], stu2.steps))

    comb = StudentImplementation.combine([stu, stu2])
    assert len(comb.values) == len(stu.values)  + 1
    assert comb.steps == stu.steps + stu2.steps
    assert comb.values[-1][1] == stu.steps + stu2.steps


def test_generate_student_impls():
    """
    """
    num_notebooks = 6
    nb, stu = generate_impl()
    nbs = [nb] * num_notebooks

    with mock.patch("pybryt.student.execute_notebook") as mocked_execute:
        mocked_execute.return_value = (stu.steps, stu.values, stu.calls, None)
        stus = generate_student_impls(nbs)

    assert all(s == stu for s in stus)

    with mock.patch("pybryt.student.Process") as mocked_process:

        class MockedQueue:
            def __init__(self, *args, **kwargs):
                self.calls = 0

            def empty(self, *args, **kwargs):
                if self.calls >= num_notebooks:
                    return True
                self.calls += 1
                return False

            def get(self, *args, **kwargs):
                return (nb, stu)

        with mock.patch("pybryt.student.Queue") as mocked_queue:
            mocked_queue.return_value = mock.MagicMock(wraps=MockedQueue())
            stus = generate_student_impls(nbs, parallel=True)

    assert all(s == stu for s in stus)
