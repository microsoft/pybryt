"""Annotations for checking type presence, or lack thereof, within memory footprints"""

__all__ = ["ForbidType"]

import dill

from typing import Any, Dict, List, Tuple

from .annotation import Annotation, AnnotationResult

from ..execution import MemoryFootprint


class ForbidType(Annotation):
    """
    Annotation class for asserting there are no objects of a specific type in the memory footprint.

    Indicates that the student's memory footprint should not have any values of a certain type. Uses
    the ``isinstance`` function to determine if any values match the specified type. The type itself
    must be pickleable by ``dill``.

    Args:
        type\\_ (``type``): the type to forbid
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.annotations.annotation.Annotation>` constructor
    """

    type_: type
    """the type to forbid"""

    def __init__(self, type_, **kwargs):
        if not isinstance(type_, type):
            raise TypeError(f"{type_} is not a type")

        try:
            dill.dumps(type_)
        except Exception as e:
            raise ValueError(f"Types must be serializable but the following error was thrown during serialization:\n{e}")

        self.type_ = type_

        super().__init__(**kwargs)

    @property
    def children(self) -> List[Annotation]:
        return []

    def check(self, footprint: MemoryFootprint) -> AnnotationResult:
        """
        Checks that there are no values of type ``self.type_`` in the memory footprint.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        for mfp_val in footprint:
            if isinstance(mfp_val.value, self.type_):
                return AnnotationResult(False, self)
        return AnnotationResult(True, self)

    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        To be equal to a ``ForbidType``, the other object must also be a ``Forbidtype`` object, have
        the same instance variables, and the same forbidden type.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.type_ == other.type_

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation's details to a JSON-friendly dictionary format.

        Output dictionary contains the annotation's name, group, limit number, success message, and
        failure message, as well as the type as a string.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        d = super().to_dict()
        d.update({
            "type_": str(self.type_),
        })
        return d
