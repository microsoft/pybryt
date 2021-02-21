"""
"""

import numpy as np

from abc import ABC, abstractmethod
from collections import Iterable
from typing import Any, List, Optional, Union
# from enum import Enum, auto

# TODO: add iterable_type invariant


class _invariant(ABC):
    """
    """

    @staticmethod
    def __new__(cls, *args, **kwargs):
        return cls.run(*args, **kwargs)

    @staticmethod
    @abstractmethod
    def run(values: List[Any], **kwargs) -> List[Any]:
        ...


# TODO: if hashing, for all strings collect actual string and lowercased version (marked as such), 
#       and compare against that if this invariant is used. 
class string_capitalization(_invariant):

    @staticmethod
    def run(values: List[Any]) -> List[Any]:
        ret = []
        for v in values:
            if not isinstance(v, str):
                ret.append(v)
            else:
                ret.append(v.lower())
        return ret
