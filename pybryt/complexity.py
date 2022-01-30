"""Time complexity analysis utilities"""

import inspect

from collections.abc import Sized
from itertools import chain
from typing import List, Optional, Union

from pybryt.execution.memory_footprint import MemoryFootprintValue

from .annotations import complexities as cplx, TimeComplexity
from .execution import (
    check_time_complexity, 
    get_tracing_frame,
    FrameTracer,
    MemoryFootprint,
    TimeComplexityResult,
)


ANNOTATION_NAME = "__time_complexity_checker__"


class TimeComplexityChecker:
    """
    A utility class for using PyBryt's tracing functionality to check the time complexity of a block
    of code.

    Uses PyBryt's tracing internals to set a trace function that counts the number of steps taken
    to execute a block of code, and then uses the complexity annotation framework to determine the
    best-matched complexity class of the block.
    """

    name: str
    """the name to use for the annotation"""

    results: List[TimeComplexityResult]
    """the result objects holding the step data for each input length"""

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name if name is not None else ANNOTATION_NAME
        self.results = []

    def __call__(self, n: Union[int, float, Sized]) -> "_check_time_complexity_wrapper":
        """
        Create a wrapper for :py:class:`pybryt.execution.complexity.check_time_complexity` that enables
        tracing and collects the results object produced by that context manager.

        Args:
            n (``Union[int, float, Sized]``): the input length or the input itself if it supports ``len``

        Returns:
            :py:class:`_check_time_complexity_wrapper`: the initialized context manager that wraps
            ``check_time_complexity``
        """
        return _check_time_complexity_wrapper(self, n)

    def add_result(self, result: TimeComplexityResult) -> None:
        """
        Add a time complexity result to the collection of results.

        Args:
            result (``TimeComplexityResult``): the result object
        """
        self.results.append(result)

    def determine_complexity(self) -> cplx.complexity:
        """
        Determine the best-matched complexity class based on the results collected.

        Returns:
            :py:class:`pybryt.annotations.complexity.complexities.complexity`: the complexity class
            corresponding to the best-matched complexity
        """
        annot = TimeComplexity(cplx.constant, name=self.name)
        footprint = MemoryFootprint.from_values(
            *[MemoryFootprintValue(tcr, i, None) for i, tcr in enumerate(self.results)])
        result = annot.check(footprint)
        return result.value


class _check_time_complexity_wrapper:
    """
    A wrapper for :py:class:`pybryt.execution.complexity.check_time_complexity` that enables tracing
    for and collects the results from that context manager.

    Args:
        checker (:py:class:`TimeComplexityChecker`): the complexity checker that is using this wrapper
        n (``Union[int, float, Sized]``): the input length or the input itself if it supports ``len``
    """

    checker: TimeComplexityChecker
    """the complexity checker that is using this wrapper"""

    check_context: check_time_complexity
    """the time complexity context being wrapped"""

    frame_tracer: FrameTracer
    """the frame tracer being used to manage execution tracing"""

    n: Union[int, float, Sized]
    """the input length or the input itself if it supports ``len``"""

    def __init__(self, checker: TimeComplexityChecker, n: Union[int, float, Sized]) -> None:
        self.checker = checker
        self.n = n
        self.check_context = None
        self.frame_tracer = None

    def __enter__(self) -> None:
        self.frame_tracer = FrameTracer(inspect.currentframe().f_back)
        self.frame_tracer.start_trace()
        self.check_context = check_time_complexity(self.checker.name, self.n)
        self.check_context.__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.check_context.__exit__(exc_type, exc_value, traceback)
        self.frame_tracer.end_trace()

        result = None
        for mfp_val in self.frame_tracer.get_footprint():
            if isinstance(mfp_val.value, TimeComplexityResult):
                result = mfp_val.value

        if result:
            self.checker.add_result(result)

        return False
