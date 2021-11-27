"""Class for gathering and operating on collections of annotations"""

__all__ = ["Collection"]

from typing import Any, Dict, List, Tuple

from .annotation import Annotation, AnnotationResult

from ..execution import MemoryFootprint


class Collection(Annotation):
    """
    A class for collecting and operating on multiple annotations.

    If ``enforce_order`` is true, this collection will only be satisfied if all of its children are
    satisfied *and* the satisfying timestamps are in non-decreasing order (for those that have them).

    Args:
        *annotations (:py:class:`Annotation<pybryt.annotations.annotation.Annotation>`): the child 
            annotations being operated on
        enforce_order (``bool``, optional): whether to enforce the ordering of annotations as added 
            to this collection
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.annotations.annotation.Annotation>` constructor
    """

    _annotations: List[Annotation]
    """the child annotations that this annotation operates on"""

    enforce_order: bool
    """whether to enforce the ordering of annotations as added to this collection"""

    def __init__(self, *annotations: Annotation, enforce_order: bool = False, **kwargs):
        self._annotations = list(annotations)
        for ann in self._annotations:
            if not isinstance(ann, Annotation):
                raise ValueError("One of the arguments is not an annotation")

        self.enforce_order = enforce_order

        super().__init__(**kwargs)

    @property
    def children(self) -> List[Annotation]:
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
        return super().__eq__(other) and self.children == other.children and \
            self.enforce_order == other.enforce_order

    def check(self, footprint: MemoryFootprint) -> AnnotationResult:
        """
        Checks that all child annotations are satisfied by the values in the memory footprint, and
        that the timestamps of the satisfying values occur in non-decreasing order if 
        ``self.enforce_order`` is true.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        results = []
        for ann in self.children:
            results.append(ann.check(footprint))
        
        if self.enforce_order and all(res.satisfied for res in results):
                before = []
                with_timestamp = [res for res in results if res.satisfied_at != -1]
                for i in range(len(with_timestamp) - 1):
                    before.append(with_timestamp[i].satisfied_at < with_timestamp[i + 1].satisfied_at)

                return AnnotationResult(all(before), self, children = results)

        else:
            return AnnotationResult(None, self, children = results)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation's details to a JSON-friendly dictionary format.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        d = super().to_dict()
        d.update({
            "enforce_order": self.enforce_order,
        })
        return d

    def add(self, annotation: Annotation) -> None:
        """
        Adds an annotation to this collection.

        Args:
            annotation (:py:class:`Annotation<pybryt.annotations.annotation.Annotation>`): the
                annotation to add
        """
        if not isinstance(annotation, Annotation):
            raise TypeError(f"{annotation} is not an annotation")

        self._annotations.append(annotation)
        try:
            self.get_tracked_annotations().remove(annotation)
        except ValueError:  # pragma: no cover
            pass

    def remove(self, annotation: Annotation) -> None:
        """
        Removes an annotation from this collection.

        Args:
            annotation (:py:class:`Annotation<pybryt.annotations.annotation.Annotation>`): the
                annotation to remove
        """
        if not isinstance(annotation, Annotation):
            raise TypeError(f"{annotation} is not an annotation")

        if annotation not in self._annotations:
            raise ValueError(f"The specified annotation is not part of this collection")

        self._annotations.remove(annotation)
