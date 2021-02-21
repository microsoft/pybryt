"""
"""

__all__ = [
    "RelationalAnnotation", "BeforeAnnotation", "AndAnnotation", "OrAnnotation", "XorAnnotation", 
    "NotAnnotation"
]

from abc import abstractmethod
from typing import List, Union

from .annotation import Annotation, AnnotationResult
from ..execution import ObservedValue


class RelationalAnnotation(Annotation):
    """
    """

    _annotations: List[Union['Annotation', 'RelationalAnnotation']]

    def __init__(self, *annotations, **kwargs):
        self._annotations = annotations
        for ann in self._annotations:
            if not isinstance(ann, Annotation):
                raise ValueError("One of the arguments is not an annotation")

        super().__init__(**kwargs)

    @property
    def children(self):
        return self._annotations

    @abstractmethod
    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        ...


class BeforeAnnotation(RelationalAnnotation):
    """
    """

    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(other_values))

        if all(res.satisfied for res in results):
            before = []
            for i in range(len(self._annotations) - 1):
                before.append(results[i].satisfied_at < results[i + 1].satisfied_at)
            
            return AnnotationResult(all(before), self, children = results)
        
        else:
            return AnnotationResult(False, self, children = results)


class AndAnnotation(RelationalAnnotation):
    """
    """

    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(other_values))

        return AnnotationResult(all(res.satisfied for res in results), self, children = results)


class OrAnnotation(RelationalAnnotation):
    """
    """

    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(other_values))

        return AnnotationResult(any(res.satisfied for res in results), self, children = results)


class XorAnnotation(RelationalAnnotation):
    """
    """

    def __init__(self, *annotations):
        super().__init__(*annotations)
        assert len(self._annotations) == 2, "Cannot use xor with more than two annotations"

    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(other_values))

        sats = [res.satisfied for res in results]
        return AnnotationResult(sats[0] ^ sats[1], self, children = results)


class NotAnnotation(RelationalAnnotation):
    """
    """

    def check(self, other_values: List[ObservedValue]) -> "AnnotationResult":
        """
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(other_values))

        return AnnotationResult(all(not res.satisfied for res in results), self, children = results)
