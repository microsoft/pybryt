"""Invariants for value annotations"""

import numpy as np

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any, List, Optional, Union


class invariant(ABC):
    """
    Abstract base class for invariants. 
    
    All subclasses should implement the :py:meth:`run<invariant.run>` static method for generating 
    values that this invariant accepts as "correct". Invariants have a custom ``__new__`` method 
    that returns the value of calling the :py:meth:`run<invariant.run>` method, making them 
    function as callables.
    """

    @staticmethod
    def __new__(cls, *args, **kwargs):
        return cls.run(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def run(values: List[Any], **kwargs) -> List[Any]:
        """
        Returns a list of values that this invariant accepts as correct.

        Takes in a list of acceptable values from a :py:class:`Value<pybryt.Value>` annotation and
        returns a list of values that would evaluate as "the same" under the conditions of this 
        invariant.

        For example, if ``values`` as a list with a single element, a numpy matrix, and the 
        invariant was matrix transposition, this method would return a length-2 list containing the
        original matrix and its transpose.

        Args:
            values (``list[object]``): acceptable values, either from the initial constructor call
                of the annotation or from the results of other invariants
            kwargs: additional keyword arguments
        
        Returns:
            ``list[object]``: the values that would evaluate as "the same" under the conditions 
            of this invariant
        """
        ... # pragma: no cover


class string_capitalization(invariant):
    """
    An invariant that compares strings ignoring the capitalization of letters.
    """

    @staticmethod
    def run(values: List[Any]) -> List[Any]:
        """
        Returns a list of values in which all strings have been lowercased.

        Args:
            values (``list[object]``): acceptable values, either from the initial constructor call
                of the annotation or from the results of other invariants
        
        Returns:
            ``list[object]``: the transformed values
        """
        ret = []
        for v in values:
            if not isinstance(v, str):
                ret.append(v)
            else:
                ret.append(v.lower())
        return ret


class matrix_transpose(invariant):
    """
    An invariant that compares 2-dimensional arrays ignoring transposition.
    """

    @staticmethod
    def run(values: List[Any]) -> List[Any]:
        """
        Returns a list of values in which all 2D iterables have been converted to NumPy arrays and
        have had their transpose added

        Args:
            values (``list[object]``): acceptable values, either from the initial constructor call
                of the annotation or from the results of other invariants
        
        Returns:
            ``list[object]``: the transformed values
        """
        ret = []
        for v in values:
            if isinstance(v, np.ndarray):
                ret.append(v)
                ret.append(v.T)
            elif isinstance(v, Iterable) and not isinstance(v, str):
                try:
                    arr = np.array(v)
                    ret.append(arr)
                    ret.append(arr.T)
                except:
                    ret.append(v)
            else:
                ret.append(v)
        return ret


class list_permutation(invariant):
    """
    An invariant that compares iterables (except strings) ignoring ordering, using ``sorted``.
    """

    @staticmethod
    def run(values: List[Any]) -> List[Any]:
        """
        Returns a list of values in which all iterables have been sorted.

        Args:
            values (``list[object]``): acceptable values, either from the initial constructor call
                of the annotation or from the results of other invariants
        
        Returns:
            ``list[object]``: the transformed values
        """
        ret = []
        for v in values:
            if isinstance(v, np.ndarray):
                ret.append(np.sort(v))
            elif isinstance(v, Iterable) and not isinstance(v, str):
                ret.append(sorted(v))
            else:
                ret.append(v)
        return ret
