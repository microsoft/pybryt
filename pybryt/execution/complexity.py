""""""

from collections.abc import Sized
from contextlib import contextmanager
from typing import Union


class TimeComplexityResult:

    def __init__(self, n, start, stop):
        self.n = n
        self.start = start
        self.stop = stop


@contextmanager
def check_time_complexity(n: Union[int, float, Sized]):
    """
    """
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
    
    yield

    if curr_steps is not None:
        end_steps = counter[0]
        observed.append((TimeComplexityResult(n, curr_steps, end_steps), end_steps))
