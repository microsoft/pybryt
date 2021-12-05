""""""

import inspect

from collections.abc import Sized
from itertools import chain
from types import FrameType
from typing import List, Optional, Union

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
    """

    results: List[TimeComplexityResult]
    """"""

    def __init__(self) -> None:
        self.results = []

    def __call__(self, n: Union[int, float, Sized]) -> "_check_time_complexity_wrapper":
        """
        """
        return _check_time_complexity_wrapper(self, n)

    def add_result(self, result: TimeComplexityResult) -> None:
        self.results.append(result)

    def determine_complexity(self) -> cplx.complexity:
        """
        """
        annot = TimeComplexity(cplx.constant, name=ANNOTATION_NAME)
        footprint = MemoryFootprint.from_values(
            *chain.from_iterable([(tcr, i) for i, tcr in enumerate(self.results)]))
        result = annot.check(footprint)
        return result.value


class _check_time_complexity_wrapper:

    checker: TimeComplexityChecker

    check_context: check_time_complexity

    frame_tracer: FrameTracer
    """"""

    n: Union[int, float, Sized]
    """"""

    def __init__(self, checker: TimeComplexityChecker, n: Union[int, float, Sized]) -> None:
        self.checker = checker
        self.n = n
        self.check_context = None
        self.frame_tracer = None

    def __enter__(self) -> None:
        if get_tracing_frame() is not None:
            return  # if already tracing, no action required

        self.frame_tracer = FrameTracer(inspect.currentframe().f_back)
        self.frame_tracer.start_trace()
        self.check_context = check_time_complexity(ANNOTATION_NAME, self.n)
        self.check_context.__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.check_context.__exit__(exc_type, exc_value, traceback)

        if self.frame_tracer is not None:
            self.frame_tracer.end_trace()

        result = None
        for val, _ in self.frame_tracer.get_footprint().values:
            if isinstance(val, TimeComplexityResult):
                result = val

        if result:
            self.checker.add_result(result)

        return False
