"""Annotations for asserting the presence of a value"""

__all__ = ["Value", "Attribute"]

import dill
import numbers
import pandas as pd
import numpy as np

from collections.abc import Iterable
from copy import copy
from typing import Any, Dict, List, Optional, Tuple, Union

from .annotation import Annotation, AnnotationResult
from .invariants import invariant


class Value(Annotation):
    """
    Annotation class for asserting that a value should be observed.

    Indicates that a value passed to the constructor should be observed while tracing through the
    students' code. Values can be of any type that is picklable by ``dill``. Values can specify a
    list of :ref:`invariants<invariants>` that will allow objects to be considered "equal." For 
    values that support arithemtic operators, absolute tolerances can be specified as well.

    Numeric tolerances are computed as with ``numpy.allcose``, where the value is considered "equal 
    enough" if it is within :math:`v \\pm (\\texttt{atol} + \\texttt{rtol} \\cdot |v|)`, where 
    :math:`v` is the value of the annotation.

    Args:
        value (``object``): the value that should be observed
        atol (``float`` or ``int``, optional): absolute tolerance for numeric values
        rtol (``float`` or ``int``, optional): relative tolerance for numeric values
        invariants (``list[invariant]``): invariants for 
            this value
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.annotations.annotation.Annotation>` constructor
    """

    intial_value: Any
    """a copy of the value passed to the constructor"""

    _values: List[Any]
    """
    a list of values that resulted from passing the intial value through the series of invariants 
    specified in the constructor
    """

    atol: Optional[Union[float, int]]
    """absolute tolerance for numeric values"""

    rtol: Optional[Union[float, int]]
    """relative tolerance for numeric values"""

    invariants: List[invariant]
    """the invariants for this value"""

    def __init__(
        self, value: Any, atol: Optional[Union[float, int]] = None, rtol: Optional[Union[float, int]] = None, 
        invariants: List[invariant] = [], **kwargs
    ):
        try:
            dill.dumps(value)
        except Exception as e:
            raise ValueError(f"Values must be serializable but the following error was thrown during serialization:\n{e}")

        self.initial_value = copy(value)
        self._values = [self.initial_value]
        self.atol = atol
        self.rtol = rtol
        self.invariants = invariants

        for inv in self.invariants:
            self._values = inv(self._values)

        super().__init__(**kwargs)

    @property
    def children(self) -> List[Annotation]:
        return []

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation's details to a JSON-friendly dictionary format.

        Output dictionary contains the annotation's name, group, limit number, success message, and
        failure message, as well as an ``invariants`` key with a list of the names of all invariants
        used in this value annotation and a ``atol`` key with this annotation's tolerance. This 
        dictionary does *not* contain the value being tracked.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        d = super().to_dict()
        d.update({
            "invariants": [inv.__name__ for inv in self.invariants],
            "atol": self.atol,
            "rtol": self.rtol,
        })
        return d

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
            :py:class:`AnnotationResult`: the results of this annotation based on ``observed_values``
        """
        satisfied = [self._check_observed_value(v) for v in observed_values]
        if not any(satisfied):
            return AnnotationResult(False, self)

        first_satisfier = satisfied.index(True)
        return AnnotationResult(True, self, observed_values[first_satisfier][0], observed_values[first_satisfier][1])
    
    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        To be equal to a ``Value``, the other object must also be a ``Value`` object, have the same
        set of invariants, the same tolerance, and the same initial value.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.invariants == other.invariants and \
            self.check_values_equal(self.initial_value, other.initial_value) and \
            self.atol == other.atol and self.rtol == other.rtol

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
                if self.check_values_equal(value, other_value, self.atol, self.rtol):
                    return True

        return False

    @staticmethod
    def check_values_equal(value, other_value, atol = None, rtol = None) -> bool:
        """
        Checks whether two objects are equal. 
        
        If the values are both numeric (numerics, arrays, etc.) and ``atol`` and/or ``rtol`` are 
        specified, the values are considered equal if ``other_value`` is within the tolerance
        bounds of ``value``.

        Args:
            value (``object``): the first object to compare
            other_value (``object``): the second object to compare
            atol (``float``, optional): the absolute tolerance for numeric values
            rtol (``float``, optional): the relative tolerance for numeric values
        """
        if isinstance(value, Iterable) ^ isinstance(other_value, Iterable):
            return False

        if value is None:
            return other_value is None

        if atol is None:
            atol = 0
        if rtol is None:
            rtol = 0

        if hasattr(value, 'shape'):
            try:
                if value.shape != other_value.shape:
                    return False
            except AttributeError:
                return False

        try:
            ub, lb = value + atol, value - atol
            ub += rtol * np.abs(value)
            lb -= rtol * np.abs(value)
            numeric = True

        except:
            numeric = False

        if numeric:
            try:
                res = np.logical_and(ub >= other_value, other_value >= lb)
            except (ValueError, TypeError) as e:
                return False
        else:
            try:
                if (hasattr(value, "shape") and hasattr(other_value, "shape") and value.shape != other_value.shape) \
                        or (hasattr(value, "shape") ^ hasattr(other_value, "shape")):
                    return False
                if len(value) > 0 and isinstance(value, Iterable) and all(isinstance(i, numbers.Real) for i in value):
                    # Tolerances make sense only for iterables with numerical data.
                    res = np.allclose(value, other_value, atol=atol, rtol=rtol)
                else:
                    res = value == other_value
            except (ValueError, TypeError) as e:
                return False

        if isinstance(res, Iterable):
            # handle NaN values in pandas objects
            if isinstance(res, (pd.DataFrame, pd.Series)) and hasattr(value, "isna") and \
                    hasattr(other_value, "isna"):
                res = res | (value.isna() & other_value.isna())
            if isinstance(res, (np.ndarray, pd.DataFrame, pd.Series)):
                res = res.all(axis=None)
            else:
                res = all(res)

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
        enforce_type (``bool``, optional): whether to ensure that the satisfying value has the same 
            type as the initial value
        **kwargs: additional keyword arguments passed to the :py:class:`Value<pybryt.Value>` 
            constructor
    """

    _object: Any
    _attr: str

    enforce_type: bool
    """whether to ensure that the satisfying value has the same type as the initial value"""

    def __init__(self, obj: Any, attr: str, enforce_type: bool = False, **kwargs):
        self._object = obj
        self._attr = attr
        self.enforce_type = enforce_type
        val = getattr(obj, attr)
        super().__init__(val, **kwargs)
    
    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        To be equal to a ``_AttrValue``, the other object must also be a ``_AttrValue`` object, have
        equal underlying ``Value`` annotations, have equal source objects, and have the same 
        ``_attr``.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.check_values_equal(self._object, other._object) and \
            self._attr == other._attr and self.enforce_type == other.enforce_type
    
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
        if self.enforce_type:  # filter out values of wrong type if enforce_type is True
            observed_values = [t for t in observed_values if isinstance(t[0], type(self._object))]
        vals = [t for t in observed_values if hasattr(t[0], self._attr)]
        attrs = [(getattr(obj, self._attr), t) for obj, t in vals]
        res = super().check(attrs)
        try:
            satisfier = vals[attrs.index((res.value, res.timestamp))][0]
        except ValueError:
            satisfier = None
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
        enforce_type (``bool``, optional): whether to ensure that the satisfying value has the same 
            type as the initial value
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    _annotations: List[_AttrValue]
    _invariants: List[invariant]
    _atol: Optional[Union[float, int]]
    _rtol: Optional[Union[float, int]]

    enforce_type: bool
    """whether to ensure that the satisfying value has the same type as the initial value"""

    def __init__(self, obj: Any, attrs: Union[str, List[str]], enforce_type: bool = False, **kwargs):
        if isinstance(attrs, str):
            attrs = [attrs]
        if not isinstance(attrs, list) or not all(isinstance(a, str) for a in attrs):
            raise TypeError(f"Invalid type for argument 'attrs': {type(attrs)}")

        name = kwargs.pop("name", None)
        success_message = kwargs.pop("success_message", None)
        failure_message = kwargs.pop("failure_message", None)
        self._annotations = []
        for attr in attrs:
            if not hasattr(obj, attr):
                raise AttributeError(f"{obj} has not attribute '{attr}'")
            self._annotations.append(_AttrValue(obj, attr, enforce_type=enforce_type, **kwargs))
        
        self._invariants = kwargs.pop("invariants", [])
        self._atol = kwargs.pop("atol", None)
        self._rtol = kwargs.pop("rtol", None)

        self.enforce_type = enforce_type
    
        super().__init__(name=name, success_message=success_message, failure_message=failure_message,
            **kwargs)

    @property
    def children(self) -> List[Annotation]:
        return self._annotations
    
    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        To be equal to an ``Attribute``, the other object must also be an ``Attribute`` object and
        have equal child annotations.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.children == other.children

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation's details to a JSON-friendly dictionary format.

        Output dictionary contains the annotation's name, group, limit number, success message, and
        failure message, as well as an ``invariants`` key with a list of the names of all invariants
        used in this value annotation, a ``atol`` key with this annotation's tolerance, and a key for 
        the attributes being checked. This dictionary does *not* contain the value being tracked.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        d = super().to_dict()
        d.update({
            "invariants": [inv.__name__ for inv in self._invariants],
            "atol": self._atol,
            "rtol": self._rtol,
            "attributes": [av._attr for av in self._annotations],
            "enforce_type": self.enforce_type,
        })
        return d

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
