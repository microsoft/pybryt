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


class check_time_complexity:
    """
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

        from . import _COLLECTOR_RET
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
