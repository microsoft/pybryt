"""
"""

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, List, NoReturn, Optional, Tuple

# from .relation import Before
from ..execution import ObservedValue


_TRACKED_ANNOTATIONS = []
_GROUP_INDICES = {}


class Annotation(ABC):
    """
    """

    success_message: Optional[str] = None
    failure_message: Optional[str] = None
    name: Optional[str] = None

    def __init__(self, **kwargs):
        """
        """

        if "success_message" in kwargs:
            self.success_message = kwargs["success_message"]
        if "failure_message" in kwargs:
            self.failure_message = kwargs["failure_message"]
        if "name" in kwargs:
            self.name = kwargs["name"]
        
        if "name" in kwargs:
            self.name = kwargs["name"]
        else:
            self.name = None
        
        if "limit" in kwargs:
            self.limit = kwargs["limit"]
        else:
            self.limit = None

        if "group" in kwargs:
            self.group = kwargs["group"]
        else:
            self.group = None
        
        self._track()


    def __repr__(self):
        ret = f"pybryt.{self.__class__.__name__}"
        # if hasattr(self, "value"):
        #     ret += f"({type(self.value)})"
        return ret
    
    def _track(self) -> NoReturn:
        global _GROUP_INDICES, _TRACKED_ANNOTATIONS

        idx = len(_TRACKED_ANNOTATIONS)
        if self.name is None:
            if self.limit is not None:
                raise TypeError("'limit' passed without 'name'") 
        else:
            if self.name not in _GROUP_INDICES:
                _GROUP_INDICES[self.name] = []
            if self.limit is not None and len(_GROUP_INDICES[self.name]) >= self.limit:
                return
            else:
                _GROUP_INDICES[self.name].append(idx)
        
        for child in self.children:
            try:
                _TRACKED_ANNOTATIONS.remove(child)
            except ValueError:
                pass
        
        _TRACKED_ANNOTATIONS.append(self)
    
    @staticmethod
    def get_tracked_annotations() -> List["Annotation"]:
        """
        """
        return _TRACKED_ANNOTATIONS

    @staticmethod
    def reset_tracked_annotations():
        global _GROUP_INDICES, _TRACKED_ANNOTATIONS
        _TRACKED_ANNOTATIONS.clear()
        _GROUP_INDICES.clear()

    @property
    @abstractmethod
    def children(self) -> List["Annotation"]:
        """
        """
        ...

    @abstractmethod
    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        ...

    def before(self, other_annotation: "Annotation", **kwargs) -> "BeforeAnnotation":
        """
        """
        return BeforeAnnotation(self, other_annotation, **kwargs)

    def after(self, other_annotation: "Annotation", **kwargs) -> "BeforeAnnotation":
        """
        """
        return BeforeAnnotation(other_annotation, self, **kwargs)

    def __and__(self, other_annotation: "Annotation") -> "AndAnnotation":
        """
        """
        return AndAnnotation(self, other_annotation)

    def __or__(self, other_annotation: "Annotation") -> "OrAnnotation":
        """
        """
        return OrAnnotation(self, other_annotation)

    def __xor__(self, other_annotation: "Annotation") -> "XorAnnotation":
        """
        """
        return XorAnnotation(self, other_annotation)

    def __invert__(self) -> "NotAnnotation":
        """
        """
        return NotAnnotation(self)


class AnnotationResult:

    _satisfied: Optional[bool]
    annotation: Annotation
    value: Any
    timestamp: float
    children: Optional[List["AnnotationResult"]]

    def __init__(
        self, satisfied: Optional[bool], annotation: Annotation, value: Any = None, timestamp: float = -1, 
        children: Optional[List["AnnotationResult"]] = None
    ):
        self._satisfied = satisfied
        self.annotation = annotation
        self.value = value
        self.timestamp = timestamp
        self.children = children

    def __repr__(self):
        return f"AnnotationResult(satisfied={self.satisfied}, annotation={self.annotation})"

    @property
    def satisfied(self) -> bool:
        if self._satisfied is not None:
            return self._satisfied
        elif self.children is not None:
            return all(c.satisfied for c in self.children)
        else:
            return bool(self._satisfied)

    @property
    def satisfied_at(self) -> float:
        if self.children is not None:
            return max(c.satisfied_at for c in self.children)
        return self.timestamp

    @property
    def name(self):
        return self.annotation.name
    
    @property
    def group(self):
        return self.annotation.group

    @property
    def messages(self) -> List[Tuple[str, Optional[str], bool]]: # (message, name, satisfied)
        messages = []
        if self.children:
            for c in self.children:
                messages.extend(c.messages)
        
        if self.satisfied and self.annotation.success_message:
            messages.append((self.annotation.success_message, self.annotation.name, True))
        elif not self.satisfied and self.annotation.failure_message:
            messages.append((self.annotation.failure_message, self.annotation.name, False))

        return messages


from .relation import *
