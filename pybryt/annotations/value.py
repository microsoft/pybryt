"""
"""

import dill
import numpy as np

from collections import Iterable
from copy import copy
from typing import Any, List, Tuple, Union

from .annotation import Annotation, AnnotationResult
from .invariants import invariant
from ..execution import ObservedValue


class Value(Annotation):
    """
    """

    intial_value: Any
    _values: List[Any]
    tol: Union[float, int]
    invariants: List[invariant]

    def __init__(self, value: Any, tol: Union[float, int] = 0, invariants: List[invariant] = [], **kwargs):
        try:
            dill.dumps(value)
        except Exception as e:
            raise ValueError(f"Values must be serializable but the following error was thrown during serialization:\n{e}")

        self.initial_value = copy(value)
        self._values = [self.initial_value]
        self.tol = tol
        self.invariants = invariants

        for inv in self.invariants:
            self._values = inv(self._values)

        super().__init__(**kwargs)

    @property
    def children(self):
        return []

    def check(self, other_values: List[ObservedValue]) -> AnnotationResult:
        satisfied = [self._check_observed_value(v) for v in other_values]
        if not any(satisfied):
            return AnnotationResult(False, self)

        first_satisfier = satisfied.index(True)
        return AnnotationResult(True, self, other_values[first_satisfier][0], other_values[first_satisfier][1])

    def _check_observed_value(self, observed_value: ObservedValue) -> bool:
        """
        """
        other_values = [observed_value[0]]
        for inv in self.invariants:
            other_values = inv(other_values)
        
        for value in self._values:
            for other_value in other_values:
                # if type(value) != type(other_value):
                #     continue

                # else:
                if hasattr(value, 'shape'):
                    try:
                        if value.shape != other_value.shape:
                            continue
                    except AttributeError:
                        continue

                try:
                    ub, lb = value + self.tol, value - self.tol
                    numeric = True
                
                except:
                    numeric = False

                if numeric:
                    try:
                        res = np.logical_and(ub >= other_value, other_value >= lb)
                    except (ValueError, TypeError) as e:
                        continue
                else:
                    try:
                        res = value == other_value
                    except (ValueError, TypeError) as e:
                        continue

                if isinstance(res, Iterable):
                    try:
                        res = all(res)
                    except ValueError as e:
                        if isinstance(res, np.ndarray):
                            res = res.all()
                        else:
                            raise e

                if res:
                    return True

        return False
