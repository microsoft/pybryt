"""Annotations for checking imported modules within memory footprints"""

__all__ = ["ForbidImport", "ImportAnnotation", "RequireImport"]

import importlib
import sys

from abc import abstractmethod
from typing import Any, Dict, List

from .annotation import Annotation, AnnotationResult

from ..execution import MemoryFootprint


class ImportAnnotation(Annotation):
    """
    Annotation class for asserting conditions on the set of imported modules

    The set of modules imported in the student implementation is determined using ``sys.modules``,
    meaning that subclasses count any modules imported by third-party libaries, not just directly
    by the student's code.

    Args:
        module (``str``): the module name to forbid in importable form
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.annotations.annotation.Annotation>` constructor
    """

    module: str
    """the module name to forbid"""

    def __init__(self, module, **kwargs):
        if not isinstance(module, str):
            raise TypeError(f"{module} is not a string")

        try:
            already_imported = module in sys.modules
            importlib.import_module(module)
            if not already_imported:  # clean up sys.modules if needed
                sys.modules.pop(module)
        except Exception as e:
            raise ValueError(f"{module} is not importable")

        self.module = module

        super().__init__(**kwargs)

    @property
    def children(self) -> List[Annotation]:
        return []

    @abstractmethod
    def check(self, footprint: MemoryFootprint) -> AnnotationResult:
        ... # pragma: no cover

    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        To be equal to a ``ForbidImport``, the other object must also be a ``ForbidImport`` object, 
        have the same instance variables, and the same forbidden module.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.module == other.module

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation's details to a JSON-friendly dictionary format.

        Output dictionary contains the annotation's name, group, limit number, success message, and
        failure message, as well as the module name.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        d = super().to_dict()
        d.update({
            "module": str(self.module),
        })
        return d


class RequireImport(ImportAnnotation):
    """
    Annotation class for asserting that a specific module was imported.

    Args:
        module (``str``): the module name to forbid in importable form
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.annotations.annotation.Annotation>` constructor
    """

    def check(self, footprint: MemoryFootprint) -> AnnotationResult:
        """
        Checks that the memory footprint's imports contain the specified module.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        return AnnotationResult(self.module in footprint.imports, self)


class ForbidImport(ImportAnnotation):
    """
    Annotation class for asserting that a specific module was not imported.

    Args:
        module (``str``): the module name to forbid in importable form
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.annotations.annotation.Annotation>` constructor
    """

    def check(self, footprint: MemoryFootprint) -> AnnotationResult:
        """
        Checks that the memory footprint's imports don't contain the specified module.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        return AnnotationResult(self.module not in footprint.imports, self)
