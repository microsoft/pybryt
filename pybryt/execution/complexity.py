"""Complexity analysis internals"""

from collections.abc import Sized
from typing import Optional, Union

from .memory_footprint import MemoryFootprint


COMPLEXITY_TRACING_ENABLED = False


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

    name: str

    n: int

    start_steps: Optional[int]

    footprint: Optional[MemoryFootprint]

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
  
        self.name = name
        self.n = n
        self.start_steps, self.footprint = None, None

    def __enter__(self):
        global COMPLEXITY_TRACING_ENABLED

        if get_active_footprint() is not None:
            self.footprint = get_active_footprint()
            self.start_steps = self.footprint.counter.get_value()

        COMPLEXITY_TRACING_ENABLED = True

    def __exit__(self, exc_type, exc_value, traceback):
        global COMPLEXITY_TRACING_ENABLED

        COMPLEXITY_TRACING_ENABLED = False

        if self.start_steps is not None:
            end_steps = self.footprint.counter.get_value()
            self.footprint.add_value(TimeComplexityResult(
                self.name, self.n, self.start_steps, end_steps), allow_duplicates=True)

        return False


def is_complexity_tracing_enabled() -> bool:
    """
    Return whether complexity tracing is currently enabled.

    Returns:
        ``bool``: whether complexity tracing is currently enabled
    """
    return COMPLEXITY_TRACING_ENABLED


from .tracing import get_active_footprint
