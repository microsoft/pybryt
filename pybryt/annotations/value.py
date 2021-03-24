"""
"""

__all__ = ["Value", "Attribute"]

import dill
import numpy as np

from collections.abc import Iterable
from copy import copy
from typing import Any, Dict, List, Tuple, Union

from .annotation import Annotation, AnnotationResult
from .invariants import invariant


class Value(Annotation):
    """
    Annotation class for asserting that a value should be observed.

    Indicates that a value passed to the constructor should be observed while tracing through the
    students' code. Values can be of any type that is picklable by ``dill``. Values can specify a
    list of :ref:`invariants<invariants>` that will allow objects to be considered "equal." For 
    values that support arithemtic operators, absolute tolerances can be specified as well.

    Args:
        value (``object``): the value that should be observed
        tol (``float`` or ``int``, optional): absolute tolerance for numeric values
        invariants (``list[invariant]``): invariants for 
            this value
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    intial_value: Any
    """a copy of the value passed to the constructor"""

    _values: List[Any]
    """
    a list of values that resulted from passing the intial value through the series of invariants 
    specified in the constructor
    """

    tol: Union[float, int]
    """absolute tolerance for numeric values"""

    invariants: List[invariant]
    """the invariants for this value"""

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

    def check(self, observed_values: List[Tuple[Any, int]]) -> AnnotationResult:
        """
        Checks that the value tracked by this annotation occurs in the list of observed values.

        Checks that the value under the conditions of its invariants occurs in the list of tuples of
        observed values and timestamps ``observed_values``. Creates and returns an 
        :py:class:`AnnotationResult<pybryt.AnnotationResult>` object with the results of this check.

        Args:
            observed_values (``list[tuple[object, int]]``): a list of tuples of values observed
                during execution and the timestamps of those values
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation based on 
            ``observed_values``
        """
        satisfied = [self._check_observed_value(v) for v in observed_values]
        if not any(satisfied):
            return AnnotationResult(False, self)

        first_satisfier = satisfied.index(True)
        return AnnotationResult(True, self, observed_values[first_satisfier][0], observed_values[first_satisfier][1])

    def _check_observed_value(self, observed_value: Tuple[Any, int]) -> bool:
        """
        Checks whether a single observed value tuple satisfies this value.

        Applies all invariants to the first element of the tuple and then checks whether any of the
        resulting values match and of the values in ``self._values``.

        Args:
            observed_value (``tuple[object, int]``): the observed value tuple

        Returns:
            ``bool``: whether the value matched
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
                        if (hasattr(value, "shape") and hasattr(other_value, "shape") and value.shape != other_value.shape) \
                                or (hasattr(value, "shape") ^ hasattr(other_value, "shape")):
                            continue
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


class _AttrValue(Value):
    """
    Wrapper around ``Value`` for checking whether an object has an *attribute* matching a specific
    value.

    Args:
        obj (``object``): the object being checked
        attr (``str``): the attribute of the object being checked
        **kwargs: additional keyword arguments passed to the :py:class:`Value<pybryt.Value>` 
            constructor
    """

    _object: Any
    _attr: str

    def __init__(self, obj: Any, attr: str, **kwargs):
        self._object = obj
        self._attr = attr
        val = getattr(obj, attr)
        super().__init__(val, **kwargs)
    
    def check(self, observed_values: List[Tuple[Any, int]]) -> AnnotationResult:
        """
        Checks whether any of the values in ``observed_values`` has an attribute matching the value
        in this annotation.

        Args:
            observed_values (``list[tuple[object, int]]``): a list of tuples of values observed
                during execution and the timestamps of those values
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation based on 
            ``observed_values``
        """
        vals = [t for t in observed_values if hasattr(t[0], self._attr)]
        attrs = [(getattr(obj, self._attr), t) for obj, t in vals]
        res = super().check(attrs)
        satisfier = vals[attrs.index((res.value, res.timestamp))][0]
        return AnnotationResult(None, self, value=satisfier, children=[res])


class Attribute(Annotation):
    """
    Annotation for asserting that an object has an attribute value matching that of another object.

    Uses a :py:class:`Value<pybryt.Value>` annotation to check there exists an object in the 
    students' code which as a specific attribute, or a series of attributes, with values matching
    those in the object passed to the constructor. The constructor taks in the object in question
    and the name of the attribute(s) being studied.

    Args:
        obj (``object``): the object being checked
        attrs (``str`` or ``list[str]``): the attribute or attributes that should be checked
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    _annotations: List[_AttrValue]

    def __init__(self, obj: Any, attrs: Union[str, List[str]], **kwargs):
        if isinstance(attrs, str):
            attrs = [attrs]
        if not isinstance(attrs, list) or not all(isinstance(a, str) for a in attrs):
            raise TypeError(f"Invalid type for argument 'attrs': {type(attrs)}")
                
        self._annotations = []
        for attr in attrs:
            if not hasattr(obj, attr):
                raise AttributeError(f"{obj} has not attribute '{attr}'")
            self._annotations.append(_AttrValue(obj, attr, **kwargs))

    @property
    def children(self):
        return self._annotations

    def check(self, observed_values: List[Tuple[Any, int]]) -> AnnotationResult:
        """
        Checks whether any of the values in ``observed_values`` has all of the required attributes,
        each matching the values expected.

        Args:
            observed_values (``list[tuple[object, int]]``): a list of tuples of values observed
                during execution and the timestamps of those values
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation based on 
            ``observed_values``
        """
        results = [v.check(observed_values) for v in self._annotations]        
        return AnnotationResult(None, self, children=results)
