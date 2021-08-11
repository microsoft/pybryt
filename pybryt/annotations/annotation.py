"""Abstract base class for annotations and annotation results class"""

__all__ = ["Annotation", "AnnotationResult"]

from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple


_TRACKED_ANNOTATIONS = []
_GROUP_INDICES = {}
_ANNOTATION_COUNTER = 0


class Annotation(ABC):
    """
    Abstract base class for annotating a reference implementation.

    Defines an API and global configurations for all annotations used for marking-up reference
    implementations. All instances of this class, or any of its subclasses, are added to a singleton
    list that PyBryt maintains to track all annotations for simple reference creation. Supports
    bitwise logical operators and contains methods for creating relational annotations (see
    :py:class:`RelationalAnnotation<pybryt.RelationalAnnotation>`).

    Args:
        name (``str``, optional): the name of the annotation
        limit (``int``, optional): the maximum number of annotations with name ``name`` to track
            in ``_TRACKED_ANNOTATIONS``
        group (``str``, optional): the name of the group that this annotation belongs to
        success_message (``str``, optional): a message to relay to the student if satisfied
        failure_message (``str``, optional): a message to relay to the student if not satisfied
    """

    name: str
    """the name of the annotation"""
    
    limit: Optional[int]
    """the maximum number of annotations with this name to track in :obj:`_TRACKED_ANNOTATIONS`"""
    
    group: Optional[str]
    """the name of the group that this annotation belongs to"""
    
    success_message: Optional[str]
    """a message to relay to the student if satisfied"""
    
    failure_message: Optional[str]
    """a message to relay to the student if not satisfied"""

    def __init__(
        self, name: Optional[str] = None, limit: Optional[int] = None, group: Optional[str] = None, 
        success_message: Optional[str] = None, failure_message: Optional[str] = None,
    ):
        global _ANNOTATION_COUNTER
        _ANNOTATION_COUNTER += 1
        if name is not None:
            self.name = name
        else:
            self.name = f"Annotation {_ANNOTATION_COUNTER}"
        self.limit = limit
        self.group = group
        self.success_message = success_message
        self.failure_message = failure_message
        
        self._track()

    def __repr__(self):
        ret = f"pybryt.{self.__class__.__name__}"
        return ret
    
    def _track(self) -> None:
        """
        Tracks this annotation in ``_TRACKED_ANNOTATIONS`` and updates ``_GROUP_INDICES`` with the
        index of the annotation if ``self.group`` is present. If the annotation has children
        (returned by ``self.children``), the children are removed from ``_TRACKED_ANNOTATIONS``.
        """
        from ..execution.complexity import _TRACKING_DISABLED
        if _TRACKING_DISABLED:
            return

        global _GROUP_INDICES, _TRACKED_ANNOTATIONS

        idx = len(_TRACKED_ANNOTATIONS)
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
        Returns the list of tracked annotations.

        Returns:
            ``list[Annotation]``: the list of tracked annotations
        """
        return _TRACKED_ANNOTATIONS

    @staticmethod
    def reset_tracked_annotations() -> None:
        """
        Resets the list of tracked annotations and the mapping of group names to indices in that
        list.
        """
        global _ANNOTATION_COUNTER, _GROUP_INDICES, _TRACKED_ANNOTATIONS
        _TRACKED_ANNOTATIONS.clear()
        _GROUP_INDICES.clear()
        _ANNOTATION_COUNTER = 0

    @property
    @abstractmethod
    def children(self) -> List["Annotation"]:
        """
        ``list[Annotation]``: the child annotations of this annotation. If this annotation has no 
        children, an empty list.
        """
        ... # pragma: no cover

    @abstractmethod
    def check(self, observed_values: List[Tuple[Any, int]]) -> "AnnotationResult":
        """
        Runs the check on the condition asserted by this annotation and returns a results object.

        Checks that the condition required by this annotation is met using the list of tuples of
        observed values and timestamps ``observed_values``. Creates and returns an 
        :py:class:`AnnotationResult<pybryt.AnnotationResult>` object with the results of this check.

        Args:
            observed_values (``list[tuple[object, int]]``): a list of tuples of values observed
                during execution and the timestamps of those values
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation based on 
            ``observed_values``
        """
        ... # pragma: no cover

    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return isinstance(other, type(self)) and  self.name == other.name and \
            self.success_message == other.success_message and \
            self.failure_message == other.failure_message and self.group == other.group and \
            self.limit == other.limit

    def before(self, other_annotation: "Annotation", **kwargs) -> "BeforeAnnotation":
        """
        Creates an annotation asserting that this annotation is satisfied before another (i.e. that
        the satisfying timestamp of this annotation is less than or equal to that of 
        ``other_annotation``).

        Args:
            other_annotation (``Annotation``): the annotation that should be satisfied after this 
                one
            kwargs: other keyword arguments passed to the ``BeforeAnnotation`` constructor
        
        Returns:
            ``BeforeAnnotation``: the annotation asserting the before condition
        """
        return BeforeAnnotation(self, other_annotation, **kwargs)

    def after(self, other_annotation: "Annotation", **kwargs) -> "BeforeAnnotation":
        """
        Creates an annotation asserting that this annotation is satisfied after another (i.e. that
        the satisfying timestamp of this annotation is greater than or equal to that of 
        ``other_annotation``).

        Args:
            other_annotation (``Annotation``): the annotation that should be satisfied before this 
                one
            kwargs: other keyword arguments passed to the ``BeforeAnnotation`` constructor
        
        Returns:
            ``BeforeAnnotation``: the annotation asserting the before condition
        """
        return BeforeAnnotation(other_annotation, self, **kwargs)

    def __and__(self, other_annotation: "Annotation") -> "AndAnnotation":
        """
        Overrides the ``&`` operator for annotations to return an 
        :py:class`AndAnnotation<pybryt.AndAnnotation>`, asserting that both annotations should be 
        satisfied.

        Args:
            other_annotation (``Annotation``): the other annotation

        Returns:
            ``AndAnnotation``: the annotation asserting the and condition
        """
        return AndAnnotation(self, other_annotation)

    def __or__(self, other_annotation: "Annotation") -> "OrAnnotation":
        """
        Overrides the ``|`` operator for annotations to return an 
        :py:class`OrAnnotation<pybryt.OrAnnotation>`, asserting that either annotation should be 
        satisfied.

        Args:
            other_annotation (``Annotation``): the other annotation

        Returns:
            ``OrAnnotation``: the annotation asserting the and condition
        """
        return OrAnnotation(self, other_annotation)

    def __xor__(self, other_annotation: "Annotation") -> "XorAnnotation":
        """
        Overrides the ``^`` operator for annotations to return an 
        :py:class`XorAnnotation<pybryt.XorAnnotation>`, asserting that either annotation but not 
        both should be satisfied.

        Args:
            other_annotation (``Annotation``): the other annotation

        Returns:
            ``XorAnnotation``: the annotation asserting the xor condition
        """
        return XorAnnotation(self, other_annotation)

    def __invert__(self) -> "NotAnnotation":
        """
        Overrides the ``~`` operator for annotations to return an 
        :py:class`NotAnnotation<pybryt.NotAnnotation>`, asserting that this annotation should *not*
        be satisfied.

        Args:
            other_annotation (``Annotation``): the other annotation

        Returns:
            ``NotAnnotation``: the annotation asserting the and condition
        """
        return NotAnnotation(self)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation's details to a JSON-friendly dictionary format.

        Output dictionary contains the annotation's name, group, limit number, success message, and
        failure message.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        type_name = type(self).__name__
        if type_name.endswith("Annotation"):
            type_name = type_name[:-len("Annotation")]
        type_name = type_name.lower()
        if type_name.startswith("_"):
            type_name = None
        return {
            "name": self.name,
            "group": self.group,
            "limit": self.limit,
            "success_message": self.success_message,
            "failure_message": self.failure_message,
            "children": [c.to_dict() for c in self.children],
            "type": type_name,
        }


class AnnotationResult:
    """
    Class that manages and defines an API for interacting with the results of an annotation.

    Created when an annotation calls its :py:meth:`check<pybryt.Annotation.check` method and 
    wrangles the results of that annotation. Contains fields for tracking child annotation results,
    values satisfying annotations, and messages returned by this annotation and its children.

    Args:
        satisfied (``bool`` or ``None``): whether the condition of the annotation was satisfied; if
            child annotation results should be used to determine this value, set to ``None``
        annotation (:py:class:`Annotation`): the annotation that this result is for
        value (``object``, optional): the value that satisfied the condition of this annotation
        timestamp (``int``, optional): the step counter value at which this annotation was satisfied
        children (``list[AnnotationResult]``, optional): child annotation results of this annotation
            result
    """

    _satisfied: Optional[bool]
    """
    whether the condition of the annotation was satisfied; if child annotation results should be 
    used to determine this value, set to ``None``
    """

    annotation: Annotation
    """the annotation that this result is for"""

    _value: Any
    """the value that satisfied the condition of this annotation"""

    timestamp: int
    """the step counter value at which this annotation was satisfied"""

    children: List["AnnotationResult"]
    """child annotation results of this annotation result"""


    def __init__(
        self, satisfied: Optional[bool], annotation: Annotation, value: Any = None, timestamp: int = -1, 
        children: List["AnnotationResult"] = [],
    ):
        self._satisfied = satisfied
        self.annotation = annotation
        self._value = value
        self.timestamp = timestamp
        self.children = children

    def __repr__(self):
        return f"AnnotationResult(satisfied={self.satisfied}, annotation={self.annotation})"

    @property
    def satisfied(self) -> bool:
        """
        ``bool``: whether this annotation was satisfied
        """
        if self._satisfied is not None:
            return self._satisfied
        elif self.children:
            return all(c.satisfied for c in self.children)
        else: # pragma: no cover
            return False

    @property
    def satisfied_at(self) -> int:
        """
        ``int``: the step counter value at which this annotation was satisfied; if child results are 
        present, this is the maximum satisfying timestamp of all child results; if this annotation
        was not satisfied, returns -1
        """
        if not self.satisfied:
            return -1
        if self.children:
            return max(c.satisfied_at for c in self.children)
        return self.timestamp

    @property
    def name(self) -> Optional[str]:
        """
        ``str`` or ``None``: the name of the annotation that these results track
        """
        return self.annotation.name
    
    @property
    def group(self) -> Optional[str]:
        """
        ``str`` or ``None``: the group name of the annotation that these results track
        """
        return self.annotation.group

    @property
    def value(self) -> Any:
        """
        ``object``: the value that satisfied the condition of this annotation
        """
        if self._value is None and self.children and len(self.children) == 1:
            return self.children[0].value
        return self._value

    @property
    def messages(self) -> List[Tuple[str, Optional[str], bool]]: # (message, name, satisfied)
        """
        ``list[tuple[str, Optional[str], bool]]``: The messages returned by this annotation and its 
        children based on whether or not the annotations were satisfied. A list of tuples where the 
        first element is the message, the second is the name of the annotation (or ``None`` if no 
        name is  present), and the third is whether the annotation was satisfied.
        """
        messages = []
        for c in self.children:
            messages.extend(c.messages)
        
        if self.satisfied and self.annotation.success_message:
            messages.append((self.annotation.success_message, self.annotation.name, True))
        elif not self.satisfied and self.annotation.failure_message:
            messages.append((self.annotation.failure_message, self.annotation.name, False))

        return messages

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this annotation result's details to a JSON-friendly dictionary format.

        Output dictionary contains the annotation, whether it was satisfied, when it was satisfied,
        and any child results.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        return {
            "satisfied": self.satisfied,
            "satisfied_at": self.satisfied_at,
            "annotation": self.annotation.to_dict(),
            "children": [c.to_dict() for c in self.children],
        }


from .relation import *
