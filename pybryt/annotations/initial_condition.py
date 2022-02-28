"""Placeholders for student-set initial conditions"""

__all__ = ["InitialCondition"]

import operator

from typing import Any, Callable, Dict, List, Optional

from ..execution import MemoryFootprint


class InitialCondition:
    """
    A placeholder for initial conditions set in the submission.

    Args:
        name (``str``): the name of the initial condition
        transforms (``list[callable[[object], object]]``, optional): a list of transformations 
            (single-argument functions) to apply to the value in sequence
    """

    name: str
    """the name of the initial condition"""

    transforms: List[Callable[[Any], Any]]
    """transformations that should be applied to the value, in order"""

    def __init__(self, name: str, transforms: Optional[List[Callable[[Any], Any]]] = None):
        if not isinstance(name, str):
            raise TypeError("The name of an initial condition must be a string")

        self.name = name
        self.transforms = [] if transforms is None else transforms

    def apply(self, transform: Callable[[Any], Any]) -> "InitialCondition":
        """
        Apply an additional transformation to this initial condition, returning a new one.

        This instance is not modified; instead, a new initial condition instances is created with
        all transforms copied from this one but with the addition of the new transformation.

        Args:
            transform (``callable[[object], object]``): the transformation to add

        Returns:
            :py:class:`InitialCondition`: the new initial condition instance
        """
        transforms = self.transforms.copy()
        transforms.append(transform)
        return type(self)(self.name, transforms=transforms)

    def supply_footprint(self, footprint: MemoryFootprint) -> Any:
        """
        Calculate the value of this initial condition with all transformations applied based on the
        value stored in the provided memory footprint. 

        Args:
            initial_conditions (``dict[str, object]``): the initial conditions

        Returns:
            ``object``: the value after applying all transformations to it in sequence
        """
        return self.supply_values(footprint.get_initial_conditions())

    def supply_values(self, vals: Dict[str, Any]) -> Any:
        """
        Calculate the value of this initial condition with all transformations applied using the
        provided initial condition values.

        Applies all transformations in this initial condition to the supplied value and returns the
        result. If the result is itself an :py:class:`InitialCondition`, the values dictionary is
        supplied to that initial condition.

        Args:
            vals (``dict[str, object]``): the values to use as the initial conditions by name

        Returns:
            ``object``: the value after applying all transformations to it in sequence
        """
        if self.name not in vals:
            raise ValueError(f"The provided values do not have key '{self.name}'")

        ret = self.supply_value(vals[self.name])
        if isinstance(ret, type(self)):
            ret = ret.supply_values(vals)

        return ret

    def supply_value(self, val: Any) -> Any:
        """
        Calculate the value of this initial condition with all transformations applied.

        Applies all transformations in this initial condition to the supplied value and returns the
        result.

        Args:
            val (``object``): the value to use as the initial condition

        Returns:
            ``object``: the value after applying all transformations to it in sequence
        """
        for fn in self.transforms:
            val = fn(val)
        return val

    def _apply_binary_operator(
        self,
        op: Callable[[Any, Any], Any],
        other: Any,
        right: bool = False,
    ) -> "InitialCondition":
        """
        Create a new initial condition by applying a binary operator to this one.

        If ``right`` is true, then the value represented by this initial condition is passed as the
        second argument to the operator function; otherwise, it is passed as the first.

        Args:
            op (``callable[[object, object], object]``): a binary operator function
            other (``object``): the other object the operator should be applied to
            right (``bool``): whether this initial condition should be on the "right-side" of the
                operator

        Returns:
            :py:class:`InitialCondition`: the new initial condition instance
        """
        fn = lambda v: op(v, other)
        if right:
            fn = lambda v: op(other, v)

        return self.apply(fn)

    def __eq__(self, other) -> bool:
        """
        Determine whether the other object is also an initial condition with the same name and
        transforms.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return isinstance(other, type(self)) and self.name == other.name and \
            self.transforms == other.transforms

    def __add__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.add, other)

    def __radd__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.add, other, right=True)

    def __sub__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.sub, other)

    def __rsub__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.sub, other, right=True)

    def __mul__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.mul, other)

    def __rmul__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.mul, other, right=True)

    def __matmul__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.matmul, other)

    def __rmatmul__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.matmul, other, right=True)

    def __truediv__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.truediv, other)

    def __rtruediv__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.truediv, other, right=True)

    def __floordiv__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.floordiv, other)

    def __rfloordiv__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.floordiv, other, right=True)

    def __mod__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.mod, other)

    def __rmod__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.mod, other, right=True)

    def __divmod__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(divmod, other)

    def __rdivmod__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(divmod, other, right=True)

    def __pow__(self, other: Any, modulo: Any = None) -> "InitialCondition":
        if modulo is not None:  # support ternary pow
            return self.apply(lambda v: pow(v, other, modulo))
        return self._apply_binary_operator(operator.pow, other)

    def __rpow__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.pow, other, right=True)

    def __lshift__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.lshift, other)

    def __rlshift__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.lshift, other, right=True)

    def __rshift__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.rshift, other)

    def __rrshift__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.rshift, other, right=True)

    def __and__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.and_, other)

    def __rand__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.and_, other, right=True)

    def __xor__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.xor, other)

    def __rxor__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.xor, other, right=True)

    def __or__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.or_, other)

    def __ror__(self, other: Any) -> "InitialCondition":
        return self._apply_binary_operator(operator.or_, other, right=True)

    def __neg__(self) -> "InitialCondition":
        return self.apply(operator.neg)

    def __pos__(self) -> "InitialCondition":
        return self.apply(operator.pos)

    def __abs__(self) -> "InitialCondition":
        return self.apply(operator.abs)

    def __invert__(self) -> "InitialCondition":
        return self.apply(operator.invert)
