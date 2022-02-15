""""""

import os
import nbformat
import pkg_resources
import pytest
import tempfile

from copy import deepcopy
from functools import lru_cache
from textwrap import dedent
from unittest import mock

from pybryt import (
    check, generate_student_impls, ReferenceImplementation, ReferenceResult, StudentImplementation)
from pybryt.execution.memory_footprint import MemoryFootprint

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
def _generate_impl_cached():
    nb = generate_student_notebook()
    return nb, StudentImplementation(nb)

def generate_impl():
    return deepcopy(_generate_impl_cached())


def test_constructor():
    """
    """
    nb, stu = generate_impl()
    assert stu.nb is nb
    assert isinstance(stu.footprint, MemoryFootprint)
    assert len(stu.footprint) == 993

    with mock.patch("pybryt.student.execute_notebook") as mocked_exec:
        mocked_exec.return_value = MemoryFootprint()
        mocked_exec.return_value.set_executed_notebook(nb)

        with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as ntf:
            nbformat.write(nb, ntf.name)

            stu = StudentImplementation(ntf.name)
            assert stu.footprint.num_steps == -1
            assert list(stu.footprint) == []
            assert stu.footprint.calls == []
            assert stu.nb == nb

            with tempfile.NamedTemporaryFile(mode="w+", suffix=".ipynb") as output_ntf:
                stu = StudentImplementation(ntf.name, output=output_ntf.name)
                assert nbformat.read(output_ntf.name, as_version=nbformat.NO_CONVERT) == nb

    with pytest.raises(TypeError, match="path_or_nb is of unsupported type <class 'int'>"):
        StudentImplementation(1)


def test_load_and_dump():
    """
    """
    _, stu = generate_impl()
    with tempfile.NamedTemporaryFile() as ntf:
        stu.dump(ntf.name)
        stu2 = StudentImplementation.load(ntf.name)

        assert len(stu.footprint) == len(stu2.footprint)
        assert stu.footprint.num_steps == stu2.footprint.num_steps

    enc_stu = stu.dumps()
    stu2 = StudentImplementation.loads(enc_stu)
    assert len(stu.footprint) == len(stu2.footprint)
    assert stu.footprint.num_steps == stu2.footprint.num_steps


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

    with mock.patch.object(check, "_cache_check") as mocked_cache:
        with mock.patch("pybryt.student.FrameTracer") as mocked_frame_tracer:
            mocked_frame_tracer.return_value.get_footprint.return_value = stu.footprint
            check_cm = check(ref, cache=False)
            with check_cm:
                pass

            mocked_cache.assert_not_called()
            mocked_frame_tracer.return_value.start_trace.assert_called()
            mocked_frame_tracer.return_value.end_trace.assert_called()

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

        with mock.patch("pybryt.student.FrameTracer") as mocked_frame_tracer:
            mocked_frame_tracer.return_value.get_footprint.return_value = stu.footprint
            ref_filename = pkg_resources.resource_filename(__name__, os.path.join("files", "expected_ref.pkl"))
            check_cm = check(ref_filename)
            with check_cm:
                pass

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

        # test errors
        with pytest.raises(ValueError, match="Cannot check against an empty list of references"):
            check([])

        with pytest.raises(TypeError, match="Invalid values in the reference list"):
            check([ref, "path", 1])

        # check by annotation group
        with mock.patch.object(StudentImplementation, "from_footprint") as mocked_ff, \
                mock.patch("pybryt.student.FrameTracer"), \
                mock.patch("pybryt.student.generate_report"):
            ref = ReferenceImplementation("groups", [])
            for run_group in ["1", "2", None]:
                with check(ref, group=run_group):
                    pass

                mocked_ff.return_value.check.assert_called_with([ref], group=run_group)

    # check caching
    with mock.patch("pybryt.student.FrameTracer") as mocked_frame_tracer:
        with mock.patch("pybryt.student.StudentImplementation") as mocked_stu, \
                mock.patch("pybryt.student.generate_report") as mocked_generate, \
                mock.patch("pybryt.student.os.makedirs") as mocked_makedirs:
            mocked_stu.from_footprint.return_value.check.return_value = [mock.MagicMock()]
            mocked_stu.from_footprint.return_value.check.return_value[0].name = "foo"

            check_cm = check(ref)
            with check_cm:
                check_cm._footprint = stu.footprint
            
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
    stu2.footprint.add_value([1, 2, 3, 4], stu2.footprint.num_steps + 1)

    comb = StudentImplementation.combine([stu, stu2])
    assert len(comb.footprint) == len(stu.footprint) + 1
    assert comb.footprint.num_steps == stu.footprint.num_steps + stu2.footprint.num_steps
    assert comb.footprint.get_value(-1).timestamp == stu.footprint.num_steps + stu2.footprint.num_steps


def test_generate_student_impls():
    """
    """
    num_notebooks = 6
    nb, stu = generate_impl()
    nbs = [nb] * num_notebooks

    with mock.patch("pybryt.student.execute_notebook") as mocked_execute:
        mocked_execute.return_value = deepcopy(stu.footprint)
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
