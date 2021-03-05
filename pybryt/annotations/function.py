"""
"""

from typing import Any, Callable, List, Tuple

from .annotation import Annotation, AnnotationResult
from ..execution import ObservedValue


class Function(Annotation):
    """
    """

    def __init__(self, n_captured: int, **kwargs):
        self._values = []
        self._n = n_captured
        super().__init__(**kwargs)

    def __call__(self, func: Callable) -> Callable:
        return self._capture_function(func)

    @property
    def children(self):
        return self._values

    def _capture_function(self, func: Callable) -> Callable:
        def call_and_capture(*args, **kwargs) -> Any:
            ret = func(*args, **kwargs)
            self._values.extend(ret[:self._n])
            vals = ret[self._n:]
            if len(vals) == 1:
                return vals[0]
            return vals
        return call_and_capture
    
    def check(self, other_values: List[ObservedValue]) -> AnnotationResult:
        results = [v.check(other_values) for v in self._values]
        return AnnotationResult(None, self, children=results)
