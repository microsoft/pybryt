"""Tests for ``pybryt.complexity``"""

from unittest import mock

from pybryt import complexities as cplx
from pybryt.complexity import ANNOTATION_NAME, _check_time_complexity_wrapper, TimeComplexityChecker
from pybryt.execution import MemoryFootprintValue, TimeComplexityResult


def test_time_complexity_checker():
    """
    Tests for ``pybryt.complexity.TimeComplexityChecker``.
    """
    checker = TimeComplexityChecker()
    
    with mock.patch("pybryt.complexity._check_time_complexity_wrapper") as mocked_wrapper:
        n = 10
        checker(n)
        mocked_wrapper.assert_called_once_with(checker, n)

        res = TimeComplexityResult("foo", n, 0, 10)
        checker.add_result(res)
        assert checker.results == [res]

        with mock.patch("pybryt.complexity.TimeComplexity") as mocked_annot:
            ret = checker.determine_complexity()
            mocked_annot.assert_called_once_with(cplx.constant, name=ANNOTATION_NAME)
            mocked_annot.return_value.check.assert_called()
            assert ret == mocked_annot.return_value.check.return_value.value


def test_wrapper():
    """
    Tests for ``pybryt.complexity._check_time_complexity_wrapper``.
    """
    n = 10
    checker = TimeComplexityChecker()
    res = TimeComplexityResult(ANNOTATION_NAME, n, 0, 10)
    with mock.patch.object(checker, "add_result") as mocked_add, \
            mock.patch("pybryt.complexity.FrameTracer") as mocked_tracer, \
            mock.patch("pybryt.complexity.inspect") as mocked_inspect, \
            mock.patch("pybryt.complexity.check_time_complexity") as mocked_cm:
        mocked_tracer.return_value.get_footprint.return_value.__iter__ = \
            mock.Mock(return_value=iter([MemoryFootprintValue(res, 0, None)]))
        wrapper = _check_time_complexity_wrapper(checker, n)
        with wrapper:
            mocked_tracer.assert_called_once_with(mocked_inspect.currentframe.return_value.f_back)
            mocked_tracer.return_value.start_trace.assert_called_once()
            mocked_cm.assert_called_once_with(ANNOTATION_NAME, n)
            mocked_cm.return_value.__enter__.assert_called_once()

        mocked_cm.return_value.__exit__.assert_called_once()
        mocked_tracer.return_value.end_trace.assert_called_once()
        mocked_tracer.return_value.get_footprint.assert_called_once()
        mocked_add.assert_called_once_with(res)
