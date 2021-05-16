""""""

from collections.abc import Sized
from contextlib import contextmanager
from typing import Union


_TRACKING_DISABLED = False


class TimeComplexityResult:

    def __init__(self, name, n, start, stop):
        self.name = name
        self.n = n
        self.start = start
        self.stop = stop


@contextmanager
def check_time_complexity(name: str, n: Union[int, float, Sized]):
    """
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

    _TRACKING_DISABLED = False

    if curr_steps is not None:
        end_steps = counter[0]
        observed.append((TimeComplexityResult(name, n, curr_steps, end_steps), end_steps))
