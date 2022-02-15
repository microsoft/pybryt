"""Complexity classes for complexity annotations"""

import numpy as np

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Union


@dataclass
class ComplexityClassResult:
    """
    A container class for the results of complexity checks.
    """

    complexity_class: "complexity"
    """the complexity class associated with this result"""

    residual: float
    """the residual from the least-squares fit"""


class complexity(ABC):
    """
    Abstract base class for a complexity. Subclassses should implement the ``transform_n`` method,
    which transforms the input lengths array so that least squares can be used. If needed, the
    ``transform_t`` method can also be overwritten to transform the step counter values.

    The architecture for these and the algorithm for determining the optimal complexity is borrowed
    from https://github.com/pberkes/big_O.
    """

    def __or__(self, other: Any) -> "ComplexityUnion":
        """
        Create a complexity union through use of the ``|`` operator.

        Args:
            other (any): the other object in the union

        Returns:
            :py:class:`ComplexityUnion`: the union
        """
        return ComplexityUnion.from_or(self, other)

    def __call__(self, complexity_data: Dict[int, int]) -> ComplexityClassResult:
        """
        Return the sum of residuals by performing least squares on the input length data and timings.

        Uses ``transform_n`` and ``transform_t`` to transform the data from ``complexity_data``, which
        is a dictionary mapping input lengths to step counts. Performs least squares on the resulting
        arrays and returns the sum of residuals.

        Args:
            complexity_data (``dict[int, int]``): the complexity information

        Returns:
            ``float``: the sum of residuals from least squares
        """
        ns, ts = [], []
        for n, t in complexity_data.items():
            ns.append(n)
            ts.append(t)
        
        n = np.array(ns, dtype=int)
        t = np.array(ts, dtype=int)

        try:
            n = self.transform_n(n)
            t = self.transform_t(t)

            _, resid, _, _ = np.linalg.lstsq(n, t, rcond=-1)
            if len(resid) == 0:
                return ComplexityClassResult(self, np.inf)
            return ComplexityClassResult(self, resid[0])
        except:
            return ComplexityClassResult(self, np.inf)

    @staticmethod
    @abstractmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        """
        Transforms the array of input lengths for performing least squares.

        Args:
            n (``np.ndarray``): the array of input lengths
        
        Returns:
            ``np.ndarray``: the transformed array of input lengths
        """
        ... # pragma: no cover

    @staticmethod
    def transform_t(t: np.ndarray) -> np.ndarray:
        """
        Transforms the array of timings for performing least squares.

        Args:
            n (``np.ndarray``): the array of timings
        
        Returns:
            ``np.ndarray``: the transformed array of timings
        """
        return t


class _constant(complexity):
    """
    Complexity class for constant time: :math:`\\mathcal{O}(1)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.ones((len(n), 1))


# complexity classes are singletons
constant = _constant()


class _logarithmic(complexity):
    """
    Complexity class for logarithmic time: :math:`\\mathcal{O}(\\log n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), np.log2(n))).T


logarithmic = _logarithmic()


class _linear(complexity):
    """
    Complexity class for linear time: :math:`\\mathcal{O}(n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n)).T


linear = _linear()


class _linearithmic(complexity):
    """
    Complexity class for linearithmic time: :math:`\\mathcal{O}(n \\log n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * np.log2(n))).T


linearithmic = _linearithmic()


class _quadratic(complexity):
    """
    Complexity class for quadratic time: :math:`\\mathcal{O}(n^2)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * n)).T


quadratic = _quadratic()


class _cubic(complexity):
    """
    Complexity class for cubic time: :math:`\\mathcal{O}(n^3)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * n * n)).T


cubic = _cubic()


class _exponential(complexity):
    """
    Complexity class for exponential time: :math:`\\mathcal{O}(2^n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n)).T

    @staticmethod
    def transform_t(t: np.ndarray) -> np.ndarray:
        return np.log2(t)


exponential = _exponential()


complexity_classes = [constant, logarithmic, linear, linearithmic, quadratic, cubic]#, exponential]


class ComplexityUnion:
    """
    A complexity class that represents a union of multiple complexity classes.

    Complexity unions can be used to write annotations but cannot be used as classes to determine
    the complexity of a block of code; they are simply collections of acceptable complexity classes.

    This class does not ensure the uniqueness of the complexity classes it tracks; that is, if the
    same complexity class is added twice, it will be tracked twice.

    Args:
        *complexity_classes (:py:class:`complexity`): the complexity classes in the union
    """

    _complexity_classes = List[complexity]
    """the complexity classes contained in the union"""

    def __init__(self, *complexity_classes: complexity):
        self._complexity_classes = list(complexity_classes)

    def __or__(self, other: Any) -> "ComplexityUnion":
        """
        Create a complexity union through use of the ``|`` operator.

        Args:
            other (any): the other object in the union

        Returns:
            :py:class:`ComplexityUnion`: the union
        """
        return self.from_or(self, other)

    @classmethod
    def from_or(
        cls,
        left: Union[complexity, "ComplexityUnion"],
        right: Union[complexity, "ComplexityUnion"],
    ) -> "ComplexityUnion":
        """
        Create a complexity union from two operands.

        Args:
            left (:py:class:`complexity` or :py:class:`ComplexityUnion`): the left operand
            right (:py:class:`complexity` or :py:class:`ComplexityUnion`): the right operand

        Returns:
            :py:class:`ComplexityUnion`: the union containing both operands

        Raises:
            ``TypeError``: if either operand is not a complexity class or complexity union
        """
        if not isinstance(left, (complexity, cls)):
            raise TypeError(f"Attempted to combine a complexity class with an object of type {type(left)}")

        if not isinstance(right, (complexity, cls)):
            raise TypeError(f"Attempted to combine a complexity class with an object of type {type(right)}")

        if isinstance(left, cls):
            right_complexities = [right]
            if isinstance(right, cls):
                right_complexities = right.get_complexities()
            return cls(*left.get_complexities(), *right_complexities)

        elif isinstance(right, cls):
            return cls(left, *right.get_complexities())

        return cls(left, right)

    def add_complexity(self, complexity_class: complexity) -> None:
        """
        Add another complexity class to this union.

        Args:
            complexity_class (:py:class:`complexity`): the complexity class to add
        """
        self._complexity_classes.append(complexity_class)

    def get_complexities(self) -> List[complexity]:
        """
        Return a list of the complexity classes in this union.

        Returns:
            ``list[complexity]``: the complexity classes
        """
        return [*self._complexity_classes]

    def __eq__(self, other: Any) -> bool:
        """
        Determine whether another object is equal to this complexity union.

        An object is equal to a complexity union if it is also a complexity union and contains the
        same complexity classes.

        Returns:
            ``bool``: whether the other object is equal to this one
        """
        return isinstance(other, type(self)) and \
            set(self.get_complexities()) == set(other.get_complexities())
