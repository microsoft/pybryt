"""Reference implementations for PyBryt"""

__all__ = ["ReferenceImplementation", "ReferenceResult", "generate_report"]

import nbformat
import numpy as np
import os
import warnings

from copy import deepcopy
from textwrap import indent
from typing import Any, Dict, List, Optional, Tuple, Union

from .annotations import Annotation, AnnotationResult
from .execution import MemoryFootprint
from .utils import get_stem, notebook_to_string, Serializable


class ReferenceImplementation(Serializable):
    """
    A reference implementation class for managing collections of annotations. Defines methods for
    creating, running, and storing reference implementations.

    Args:
        name (``str``): the name of the reference implementation
        annotations (``list[Annotation]``): the annotations comprising this reference implementation
    """
    
    annotations: List[Annotation]
    """the annotations comprising this reference implementation"""

    name: str
    """the name of the reference implementation"""

    def __init__(self, name: str, annotations: List[Annotation]):
        if not isinstance(annotations, list):
            raise TypeError("annotations should be a list of Annotations")
        if not all(isinstance(ann, Annotation) for ann in annotations):
            raise TypeError("Found non-annotation in annotations")
        
        self.annotations, name_counts = [], {}
        for ann in annotations:
            track = True
            if ann.name is not None:
                count = name_counts.get(ann.name, 0)
                if ann.limit is None or ann.limit > count:
                    name_counts[ann.name] = count + 1
                else:
                    track = False

            if track:
                self.annotations.append(ann)

        self.name = name

    def __eq__(self, other: Any) -> bool:
        """
        Checks whether this reference implementation is equal to another object.

        For an object to equal a reference implementation, it must also be a reference 
        implementation and have the same annotations as this reference implementation.

        Args:
            other (``object``): the object to compare to

        Returns:
            ``bool``: whether the objects are equal
        """
        return isinstance(other, type(self)) and self.annotations == other.annotations and \
            self.name == other.name

    @property
    def _default_dump_dest(self) -> str:
        return f"{self.name}.pkl"

    def get(self, name: str) -> Union[Annotation, List[Annotation]]:
        """
        Retrieves and returns annotation(s) using their ``name`` attribute.

        Returns a single annotation if there is only one annotation with that name, otherwise returns
        a list of annotations with that name.

        Args:
            name (``str``): the name of look up

        Returns:
            ``Annotation`` or ``list[Annotation]``: the annotation(s) with that name

        Raises:
            ``ValueError``: if there are no annotations with that name
        """
        annots = []
        for ann in self.annotations:
            if ann.name == name:
                annots.append(ann)
        if len(annots) == 0:
            raise ValueError(f"Found no annotations with name '{name}'")
        elif len(annots) == 1:
            return annots[0]
        else:
            return annots

    def run(self, footprint: MemoryFootprint, group: Optional[str] = None) -> 'ReferenceResult':        
        """
        Runs the annotations tracked by this reference implementation against a memory footprint.

        Can run only specific annotations by specifying the ``group`` argument. Returns a 
        :py:class:`ReferenceResult<pybryt.ReferenceResult>` object.

        Args:
            footprint (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the
                memory footprint to check against
            group (``str``, optional): if specified, only annotations in this group will be run

        Returns:
            :py:class:`ReferenceResult<pybryt.ReferenceResult>`: the results of this check

        Raises:
            ``ValueError``: if ``group`` is specified but there are no annotations with that group
        """
        if group is not None:
            annots = []
            for ann in self.annotations:
                if ann.group == group:
                    annots.append(ann)
            if len(annots) == 0:
                raise ValueError(f"Group '{group}' not found")
        
        else:
            annots = self.annotations
        
        results = []
        for exp in annots:
            results.append(exp.check(footprint))
        
        return ReferenceResult(self, results, group=group)

    @classmethod
    def compile(cls, path_or_nb: Union[str, nbformat.NotebookNode], name: Optional[str] = None) -> \
            Union['ReferenceImplementation', List['ReferenceImplementation']]:
        """
        Compiles a notebook or Python script into a single or list of reference implementations.

        Creates a reference implementation by executing a Jupyter Notebook or Python script and 
        collecting all :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` objects
        created, if any, or all :py:class:`Annotation<pybryt.Annotation>` objects otherwise.

        Args:
            path_or_nb (``str`` or ``nbformat.NotebookNode``): the file to be executed
        
        Returns:
            ``ReferenceImplementation`` or ``list[ReferenceImplementation]``: the reference(s) 
            created by executing the file
        """
        Annotation.reset_tracked_annotations()

        if isinstance(path_or_nb, str) and os.path.splitext(path_or_nb)[1] != ".ipynb":
            with open(path_or_nb) as f:
                source = f.read()
        else:
            source = notebook_to_string(path_or_nb)

        if isinstance(path_or_nb, str) and name is None:
            name = get_stem(path_or_nb)

        env = {}
        exec(source, env)

        refs = []
        for _, v in env.items():
            if isinstance(v, cls):
                refs.append(v)

        if not refs:
            if not Annotation.get_tracked_annotations():
                warnings.warn(f"Could not find any reference implementations in " \
                    f"{path_or_nb if isinstance(path_or_nb, str) else 'the provided notebook'}")
            else:
                if name is None:
                    raise ValueError("No name specified for the reference being compiled")
                refs = [cls(name, deepcopy(Annotation.get_tracked_annotations()))]

        Annotation.reset_tracked_annotations()
        
        if len(refs) == 1:
            return refs[0]
        return refs


class ReferenceResult(Serializable):
    """
    Class for wrangling and managing the results of a reference implementation. Collects a series of
    :py:class:`AnnotationResult<pybryt.AnnotationResult>` objects and provides an API for managing
    those results collectively.

    Args:
        reference (``ReferenceImplementation``): the reference implementation
        annotation_results (``list[AnnotationResult]``): the annotation results from running the
            reference implementation
        group (``str``, optional): the name of the group of annotations executed, if applicable
    """

    reference: ReferenceImplementation
    """the reference implementation executed"""

    results: List[AnnotationResult]
    """the annotation results from running the reference implementation"""

    group: Optional[str]
    """the name of the group of annotations executed, if applicable"""

    def __init__(
        self, reference: ReferenceImplementation, annotation_results: List[AnnotationResult], 
        group: Optional[str] = None
    ):
        self.reference = reference
        self.results = annotation_results
        self.group = group

    def __repr__(self):
        results = ',\n  '.join(repr(r) for r in self.results)
        return f"ReferenceResult([\n  {results}\n])"

    @property
    def _default_dump_dest(self) -> str:
        return f"{self.name}_results.pkl"

    @property
    def correct(self) -> bool:
        """
        ``bool``: whether the reference implementation was satisfied
        """
        return all(r.satisfied for r in self.results)

    @property
    def name(self) -> str:
        """
        ``str``: the name of the underlying reference implementation
        """
        return self.reference.name

    @property
    def messages(self) -> List[str]:
        """
        ``list[str]``: the list of messages returned by all annotations in the reference 
        implementation; if ``self.group`` is not ``None``, only messages from annotations in that
        group are returned
        """
        finalized_messages, message_indices_by_name = [], {}
        for r in self.results:
            for msg in r.messages:
                if msg.name in message_indices_by_name and not msg.satisfied:
                    idx = message_indices_by_name[msg.name]
                    finalized_messages[idx] = msg.message

                elif msg.name not in message_indices_by_name:
                    message_indices_by_name[msg.name] = len(finalized_messages)
                    finalized_messages.append(msg.message)

        return [m for m in finalized_messages if m is not None]

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts this reference result's details to a JSON-friendly dictionary format.

        Output dictionary contains the group name run, if present, and the dictionary representations
        of all child annotation results.

        Returns:
            ``dict[str, object]``: the dictionary representation of this annotation
        """
        return {
            "group": self.group,
            "results": [ar.to_dict() for ar in self.results],
        }

    def to_array(self) -> np.ndarray:
        """
        Converts this result into a numpy array of integers, where ``1`` indicates a satisfied 
        annotation and ``0`` is unsatisfied.

        Returns:
            ``numpy.ndarray``: indicator array for the passage of annotations
        """
        return np.array([r.satisfied for r in self.results], dtype=int)


def generate_report(
    results: Union[ReferenceResult, List[ReferenceResult]], show_only: Optional[str] = None,
    fill_empty: bool = True
) -> str:
    """
    Collects a series of reference result objects and returns a summary of these results with any
    messages from the annotations.

    ``show_only`` should be in the set ``{'satisfied', 'unsatisfied', None}``. If ``"satisfied"``,
    the summary will contain only the results of satisfied reference implementations. If 
    ``"unsatisfied"``, the summary will contain only the results of unsatisfied reference 
    implementations. If ``None``, all reference implementations will be included.

    If ``show_only`` is set to a value that would result in an empty report (e.g. it is set to
    ``"satisfied"`` but no reference was satisfied) and ``fill_empty`` is ``True``, the report will
    be filled with any references that would normally be excluded by ``show_only``.

    Args:
        results (``Union[ReferenceResult, list[ReferenceResult]]``): the result(s) being collected
        show_only (``{'satisfied', 'unsatisfied', None}``): which results to report
        fill_empty (``bool``): if the resulting report would be empty, include results of the type
            not specified by ``show_only``

    Returns:
        ``str``: the summary report
    """
    if isinstance(results, ReferenceResult):
        results = [results]
    if not isinstance(results, list) or not all(isinstance(r, ReferenceResult) for r in results):
        raise TypeError("Cannot generate a report from arguments that are not reference result objects")
    if show_only not in {"satisfied", "unsatisfied", None}:
        raise ValueError("show_only must be in {'satisfied', 'unsatisfied', None}")
    
    filtered = []
    for res in results:
        if res.correct and show_only != "unsatisfied":
            filtered.append(res)
        elif not res.correct and show_only != "satisfied":
            filtered.append(res)

    if len(filtered) == 0 and fill_empty:
        filtered = results

    report = ""
    for i, res in enumerate(filtered):
        report += f"REFERENCE: {res.name}\n"
        report += f"SATISFIED: {res.correct}"

        if res.messages:
            report += f"\nMESSAGES:\n"
            report += indent("\n".join(res.messages), "  - ")

        if i != len(filtered) - 1:
            report += "\n\n"

    return report
