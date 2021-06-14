""""""

from collections.abc import Sized
from contextlib import contextmanager
from typing import Union


_TRACKING_DISABLED = False


class TimeComplexityResult:
    """
    A class for collecting the results of time complexity check blocks.

    Args:
        name (``str``): the name of the block
        n (``int``): the input length
        start (``int``): the step counter value at the start of the block
        stop (``int``): the step counter value at the end of the block
    """

    name: str
    """the name of the block"""

    n: int
    """the input length or the input itself"""

    start: int
    """the step counter value at the start of the block"""

    stop: int
    """the step counter value at the end of the block"""

    def __init__(self, name, n, start, stop):
        self.name = name
        self.n = n
        self.start = start
        self.stop = stop


class check_time_complexity:
    """
    A context manager for checking the time complexity of student code.

    Halts tracking of values in memory and sets the trace function to only increment the step
    counter. When the block exits, the step counter is checked an a ``TimeComplexityResult`` object
    is appended to the student's memory footprint.

    If the current call stack is not being traced by PyBryt, no action is taken.

    Args:
        name (``str``): the name of the check; should match with the name of an annotation in the
            reference implementation
        n (``Union[int, float, Sized]``): the input length or the input itself if it supports ``len``
    """

    def __init__(self, name: str, n: Union[int, float, Sized]):
        if isinstance(n, float):
            n = int(n)
        if isinstance(n, Sized):
            n = len(n)
        if not isinstance(n, int):
            try:
                n = int(n)
            except:
                raise TypeError(f"n has invalid type {type(n)}")
  
        self._name = name
        self._n = n
        self._curr_steps = None
        self._observed, self._counter = None, None

    def __enter__(self):
        global _TRACKING_DISABLED

        from .tracing import _COLLECTOR_RET
        if _COLLECTOR_RET is not None:
            self._observed, self._counter, _ = _COLLECTOR_RET
            self._curr_steps = self._counter[0]

        _TRACKING_DISABLED = True

    def __exit__(self, exc_type, exc_value, traceback):
        global _TRACKING_DISABLED

        _TRACKING_DISABLED = False

        if self._curr_steps is not None:
            end_steps = self._counter[0]
            self._observed.append((
                TimeComplexityResult(self._name, self._n, self._curr_steps, end_steps), 
                end_steps,
            ))

        return False
