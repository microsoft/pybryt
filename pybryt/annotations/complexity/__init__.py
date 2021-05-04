""""""

__all__ = ["complexities", "ComplexityAnnotation", "TimeComplexity"]

from . import complexities
from ..annotation import Annotation, AnnotationResult
from ...execution import TimeComplexityResult


class ComplexityAnnotation(Annotation):
    """
    """

    def __init__(self, complexity: complexities.complexity, **kwargs):
        if "name" not in kwargs:
            raise ValueError("Complexity annotations require a 'name' kwarg")
        if complexity not in complexities.complexity_classes:
            raise ValueError(f"Invalid valid for argument 'complexity': {complexity}")
        self.complexity = complexity
        super().__init__(**kwargs)

    @property
    def children(self) -> List[Annotation]:
        """
        ``list[Annotation]``: the child annotations of this annotation. If this annotation has no 
        children, an empty list.
        """
        return []


class TimeComplexity(ComplexityAnnotation):
    """
    """

    def check(self, observed_values: List[Tuple[Any, int]]) -> AnnotationResult:
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
        complexity_data = {}
        for v, ts in observed_values.items():
            if not isinstance(v, TimeComplexityResult) or v.name != self.name:
                continue

            complexity_data[v.n] = v.stop - v.start

        best_cls, best_res = None, None
        for cplx in complexities.complexity_classes:
            res = cplx(complexity_data)

            if best_res is None or res < best_res:
                best_cls, best_res = cplx, res

        return AnnotationResult(best_cls is self.complexity, self)
