""""""

from collections.abc import Sized
from contextlib import contextmanager
from typing import Union


_TRACKING_DISABLED = False


class TimeComplexityResult:
    """
    A simple class for tracking the results of time complexity checks. Has fields for the name of
    the check, the input length, and the start and stop step counts.

    Args:
        name (``str``): the name of the check
        n (``int``): the length of the input
        start (``int``): the value of the step counter at the start of the check
        stop (``int``): the value of the step counter at the end of the check
    """

    name: str
    """the name of the check"""

    n: int
    """the length of the input"""

    start: int
    """the value of the step counter at the start of the check"""

    stop: int
    """the value of the step counter at the end of the check"""

    def __init__(self, name, n, start, stop):
        self.name = name
        self.n = n
        self.start = start
        self.stop = stop


@contextmanager
def check_time_complexity(name: str, n: Union[int, float, Sized]):
    """
    Context manager for checking the time complexity of a student's code.

    This context manager is only active when PyBryt is actively tracing, and acts like the null
    context when that is not the case. Note that any code inside this context will **not** be traced
    for objects in memory, so any value annotations or similar must be checked for outside of a
    complexity block.

    Checks the execution step counter in ``pybryt.execution._COLLECTOR_RET`` before and after the
    block is executed to determine the time taken by the implementation. Creates a
    :py:class:`TimeComplexityResult` object and appends it to the list of observed values after the
    block is exited.

    Args:
        name (``str``): the name of the complexity check; should match the name of the 
            :py:class:`TimeComplexity<pybryt.TimeComplexity>` annotation this is checking
        n (``int``, ``float``, or ``collections.abc.Sized``): the length of the input being checked
            or the input itself (if it implements the ``__len__`` method) for simplicity
    """
    global _TRACKING_DISABLED
    if isinstance(n, float):
        n = int(n)
    if isinstance(n, Sized):
        n = len(n)
    if not isinstance(n, int):
        try:
            n = int(n)
        except:
            raise TypeError(f"n has invalid type {type(n)}")

    from . import _COLLECTOR_RET
    curr_steps = None
    if _COLLECTOR_RET is not None:
        observed, counter, _ = _COLLECTOR_RET
        curr_steps = counter[0]

    _TRACKING_DISABLED = True

    yield

    if curr_steps is not None:
        end_steps = counter[0]
        observed.append((TimeComplexityResult(name, n, curr_steps, end_steps), end_steps))
