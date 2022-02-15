"""Annotation classes for complexity assertions"""

__all__ = ["ComplexityAnnotation", "TimeComplexity"]

from typing import Any, List, Union

from . import complexities as cplx

from ..annotation import Annotation, AnnotationResult

from ...execution import MemoryFootprint, TimeComplexityResult


EPS = 1e-6 # a value to set a slight preference for simpler methods


class ComplexityAnnotation(Annotation):
    """
    Abstract base class for annotations that assert a condition on the complexity of a student's code.

    All complexity annotations should inherit from this class, which defines a constructor that
    takes in a complexity class and any necessary keyword arguments. Note that all compelxity
    annotations require a ``name`` keyword argument so that they can be matched with their results
    from the student's memory footprint.

    Args:
        complexity (:py:class:`complexity<pybryt.complexities.complexity>` or :py:class:`ComplexityUnion<pybryt.complexities.ComplexityUnion>`):
            the complexity class being asserted
        addl_complexities(``list[complexity]``): additional custom complexity classes to consider
        **kwargs: additional keyword arguments passed to the 
            :py:class:`Annotation<pybryt.Annotation>` constructor
    """

    complexity: Union[cplx.complexity, cplx.ComplexityUnion]
    """the complexity class of this annotation"""

    addl_complexities: List[cplx.complexity]
    """additional complexity classes to consider"""

    def __init__(
        self,
        complexity: Union[cplx.complexity, cplx.ComplexityUnion],
        addl_complexities: List[cplx.complexity] = [],
        **kwargs,
    ):
        if "name" not in kwargs:
            raise ValueError("Complexity annotations require a 'name' kwarg")
        if complexity not in cplx.complexity_classes and \
                not isinstance(complexity, cplx.complexity) and \
                not isinstance(complexity, cplx.ComplexityUnion):
            raise ValueError(f"Invalid valid for argument 'complexity': {complexity}")
        self.complexity = complexity
        self.addl_complexities = addl_complexities
        super().__init__(**kwargs)

    @property
    def children(self) -> List[Annotation]:
        """
        ``list[Annotation]``: the child annotations of this annotation. If this annotation has no 
        children, an empty list.
        """
        return []
    
    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this annotation is equal to another object.

        A complexity annotation equals another object if it is also a complexity annotation of the
        same type, has the same name, and has the same complexity assertion.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return super().__eq__(other) and self.complexity == other.complexity


class TimeComplexity(ComplexityAnnotation):
    """
    Annotation for asserting the time complexity of a block of student code.

    Time complexity here is defined as the number of execution steps taken while executing the
    code block, which is determined using the number of calls to PyBryt's trace function. Use the
    :py:obj:`check_time_complexity<pybryt.check_time_complexity>` context manager to check time
    complexity in student's code. The ``name`` of this annotation should be the same as the ``name``
    passed to the context manager or this annotation will not be able to find the results of the 
    check.
    """

    def check(self, footprint: MemoryFootprint) -> AnnotationResult:
        """
        Checks the time complexity of a block of student code and returns a results object.

        Finds all instances of the :py:class:`TimeComplexityResult<pybryt.execution.TimeComplexityResult>` 
        class in the student's memory footprint and selects all those with matching names. Collects
        the timing data from each into a dictionary and runs each complexity class in
        :py:obj:`complexities.complexity_classes<pybryt.complexities.complexity_classes>` against
        this data. Returns a result indicating whether the closest-matched complexity class was the
        one asserted in this annotation's ``complexity`` field. The ``value`` of the result object
        is set to the matching complexity class.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
        
        Returns:
            :py:class:`AnnotationResult`: the results of this annotation against ``footprint``
        """
        is_union = isinstance(self.complexity, cplx.ComplexityUnion)
        if not is_union and self.complexity not in cplx.complexity_classes:
            self.addl_complexities.insert(0, self.complexity)

        complexity_data = {}
        for mfp_val in footprint:
            if not isinstance(mfp_val.value, TimeComplexityResult) or mfp_val.value.name != self.name:
                continue

            complexity_data[mfp_val.value.n] = mfp_val.value.stop - mfp_val.value.start

        best_res = None
        complexities: List[cplx.complexity] = cplx.complexity_classes + self.addl_complexities
        for complexity in complexities:
            result = complexity(complexity_data)

            if best_res is None or result.residual < best_res.residual - EPS:
                best_res = result

        satisfied = best_res.complexity_class == self.complexity
        if is_union:
            satisfied = best_res.complexity_class in self.complexity.get_complexities()
        return AnnotationResult(satisfied, self, value=best_res.complexity_class)
