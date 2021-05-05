""""""

import numpy as np

from abc import ABC, abstractmethod
from typing import Dict


class complexity(ABC):
    """
    Architecture stolen from https://github.com/pberkes/big_O
    """

    @staticmethod
    def __new__(cls, complexity_data: Dict[int, int]) -> float:
        return cls.run(complexity_data)

    @staticmethod
    @abstractmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        """
        """
        ...

    @staticmethod
    def transform_t(t: np.ndarray) -> np.ndarray:
        """
        """
        return t

    @classmethod
    @abstractmethod
    def run(cls, complexity_data: Dict[int, int]) -> float:
        ns, ts = [], []
        for n, t in complexity_data.items():
            ns.append(n)
            ts.append(t)
        
        n = np.array(ns, dtype=int)
        t = np.array(ts, dtype=int)

        n = cls.transform_n(n)
        t = cls.transform_t(t)

        _, resid, _, _ = np.linalg.lstsq(n, t, rcond=-1)
        if len(resid) == 0:
            return np.inf
        return resid[0]


class constant(complexity):

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.ones((len(n), 1))


class linear(complexity):

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n)).T


class quadratic(complexity):

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * n)).T


class cubic(complexity):

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * n * n)).T


class logarithmic(complexity):

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), np.log2(n))).T


class linearithmic(complexity):

    @staticmethod
    def transform_n(n: np.ndarray) -> np.ndarray:
        return np.vstack((np.ones(len(n)), n * np.log2(n))).T


# class exponential(complexity):

#     @staticmethod
#     def transform_n(n: np.ndarray) -> np.ndarray:
#         return np.vstack((np.ones(len(n)), n)).T

#     @staticmethod
#     def transform_t(t: np.ndarray) -> np.ndarray:
#         return np.log2(t)


complexity_classes = [constant, linear, quadratic, cubic, logarithmic, linearithmic]#, exponential]
