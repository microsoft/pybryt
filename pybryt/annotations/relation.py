"""Relational annotations for asserting conditions on other annotations"""

__all__ = [
    "RelationalAnnotation", "BeforeAnnotation", "AndAnnotation", "OrAnnotation", "XorAnnotation", 
    "NotAnnotation"
]

from abc import abstractmethod
from typing import Any, Dict, List, Tuple

from .annotation import Annotation, AnnotationResult

from ..execution import MemoryFootprint


class RelationalAnnotation(Annotation):
    """
    Abstract base class for annotations that assert some kind of condition (temporal or boolean)
    on one or more other annotations.

    All relational annotations should inherit from this class, which defines a constructor that
    takes in a list of annotations and any necessary keyword arguments and populates the fields 
    needed for tracking child annotations.

    Args:
        *annotations (:py:class:`Annotation<pybryt.Annotation>`): the child annotations being 
            operated on
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    _annotations: List['Annotation']
    """the child annotations that this annotation operates on"""

    def __init__(self, *annotations, **kwargs):
        self._annotations = annotations
        for ann in self._annotations:
            if not isinstance(ann, Annotation):
                raise ValueError("One of the arguments is not an annotation")

        super().__init__(**kwargs)

    @property
    def children(self):
        """
        ``list[Annotation]``: the child annotations that this annotation operates on
        """
        return self._annotations

    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        For an object to equal a relational annotation, it must also be a relational annotation of
        the same type and have the same child annotations.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.children == other.children

    @abstractmethod
    def check(self, footprint: MemoryFootprint) -> "AnnotationResult":
        ... # pragma: no cover


class BeforeAnnotation(RelationalAnnotation):
    """
    pybryt.BeforeAnnotation()

    Annotation for asserting that one annotation occurs before another.

    When being :py:meth:`check<pybryt.BeforeAnnotation.check>` is called, ensures that all child 
    annotations are satisfied and then checks that for the :math:`i^\\text{th}` annotation the
    :math:`(i+1)^\\text{th}` annotation has a timestamp greater than or equal to its own. 
    Annotations must be passed to the constructor in the order in which they are expected to appear.

    Args:
        *annotations (:py:class:`Annotation<pybryt.Annotation>`): the child annotations being 
            operated on
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    def check(self, footprint: MemoryFootprint) -> "AnnotationResult":
        """
        Checks that all child annotations are satisfied by the memory footprint and
        that the timestamps of the satisfying values occur in non-decreasing order.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(footprint))

        if all(res.satisfied for res in results):
            before = []
            for i in range(len(self._annotations) - 1):
                before.append(results[i].satisfied_at <= results[i + 1].satisfied_at)
            
            return AnnotationResult(all(before), self, children = results)
        
        else:
            return AnnotationResult(False, self, children = results)


class AndAnnotation(RelationalAnnotation):
    """
    Annotation for asserting that a series of annotations are **all** satisfied.

    Args:
        *annotations (:py:class:`Annotation<pybryt.Annotation>`): the child annotations being 
            operated on
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    def check(self, footprint: MemoryFootprint) -> "AnnotationResult":
        """
        Checks that all child annotations are satisfied by the values in the memory footprint.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(footprint))

        return AnnotationResult(all(res.satisfied for res in results), self, children = results)


class OrAnnotation(RelationalAnnotation):
    """
    Annotation for asserting that, of a series of annotations, **any** are satisfied.

    Args:
        *annotations (:py:class:`Annotation<pybryt.Annotation>`): the child annotations being 
            operated on
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    def check(self, footprint: MemoryFootprint) -> "AnnotationResult":
        """
        Checks that any of the child annotations are satisfied by the memory footprint.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(footprint))

        return AnnotationResult(any(res.satisfied for res in results), self, children = results)


class XorAnnotation(RelationalAnnotation):
    """
    Annotation for asserting that, of two annotations, one is satisfied and the other is not.

    Args:
        *annotations (:py:class:`Annotation<pybryt.Annotation>`): the child annotations being 
            operated on
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    def __init__(self, *annotations):
        super().__init__(*annotations)
        assert len(self._annotations) == 2, "Cannot use xor with more than two annotations"

    def check(self, footprint: MemoryFootprint) -> "AnnotationResult":
        """
        Checks that one child annotation is satisfied and one is not by the memory footprint.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(footprint))

        sats = [res.satisfied for res in results]
        return AnnotationResult(sats[0] ^ sats[1], self, children = results)


class NotAnnotation(RelationalAnnotation):
    """
    Annotation for asserting that a single annotation should **not** be satisfied.

    Args:
        *annotations (:py:class:`Annotation<pybryt.Annotation>`): the child annotation being 
            operated on
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    def check(self, footprint: MemoryFootprint) -> "AnnotationResult":
        """
        Checks that the child annotation is not satisfied by the values in the memory footprint.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        results = []
        for ann in self._annotations:
            results.append(ann.check(footprint))

        return AnnotationResult(all(not res.satisfied for res in results), self, children = results)
