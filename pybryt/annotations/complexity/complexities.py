"""Complexity classes for complexity annotations"""

import numpy as np

from abc import ABC, abstractmethod
from typing import Dict


class complexity(ABC):
    """
    Abstract base class for a complexity. Subclassses should implement the ``transform_n`` method,
    which transforms the input lengths array so that least squares can be used. If needed, the
    ``transform_t`` method can also be overwritten to transform the step counter values.

    The architecture for these and the algorithm for determining the optimal complexity is borrowed
    from https://github.com/pberkes/big_O.
    """

    @staticmethod
    def __new__(cls, complexity_data: Dict[int, int]) -> float:
        return cls.run(complexity_data)

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

    @classmethod
    def run(cls, complexity_data: Dict[int, int]) -> float:
        """
        Returns the sum of residuals by performing least squares on the input length data and timings.

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
            n = cls.transform_n(n)
            t = cls.transform_t(t)

            _, resid, _, _ = np.linalg.lstsq(n, t, rcond=-1)
            if len(resid) == 0:
                return np.inf
            return resid[0]
        except:
            return np.inf


class constant(complexity):
    """
    Complexity class for constant time: :math:`\\mathcal{O}(1)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.ones((len(n), 1))


class logarithmic(complexity):
    """
    Complexity class for logarithmic time: :math:`\\mathcal{O}(\\log n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), np.log2(n))).T


class linear(complexity):
    """
    Complexity class for linear time: :math:`\\mathcal{O}(n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n)).T


class linearithmic(complexity):
    """
    Complexity class for linearithmic time: :math:`\\mathcal{O}(n \\log n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * np.log2(n))).T


class quadratic(complexity):
    """
    Complexity class for quadratic time: :math:`\\mathcal{O}(n^2)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * n)).T


class cubic(complexity):
    """
    Complexity class for cubic time: :math:`\\mathcal{O}(n^3)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * n * n)).T


class exponential(complexity):
    """
    Complexity class for exponential time: :math:`\\mathcal{O}(2^n)`
    """

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n)).T

    @staticmethod
    def transform_t(t: np.ndarray) -> np.ndarray:
        return np.log2(t)


complexity_classes = [constant, logarithmic, linear, linearithmic, quadratic, cubic]#, exponential]
