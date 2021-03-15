"""
"""

import os
import dill
import json
import warnings
import numpy as np

from copy import deepcopy
from typing import Any, List, NoReturn, Optional, Tuple, Union

from .annotations import Annotation, AnnotationResult
from .utils import notebook_to_string


class ReferenceImplementation:
    """
    A reference implementation class for managing collections of annotations. Defines methods for
    creating, running, and storing reference implementations.

    Args:
        annotations (``list[Annotation]``): the annotations comprising this reference implementation
    """
    
    annotations: List[Annotation]
    """the annotations comprising this reference implementation"""

    def __init__(self, annotations: List[Annotation]):
        if not isinstance(annotations, list):
            raise TypeError("annotations should be a list of Annotations")
        if not all(isinstance(ann, Annotation) for ann in annotations):
            raise TypeError("Found non-annotation in annotations")
        
        self.annotations = annotations

    @staticmethod
    def load(file: str) -> 'ReferenceImplementation':
        """
        Unpickles a reference implementation from a file.

        Args:
            file (``str``): the path to the file
        
        Returns:
            :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>`: the unpickled
            reference implementation
        """
        with open(file, "rb") as f:
            instance = dill.load(f)
        if not isinstance(instance, ReferenceImplementation):
            raise TypeError(f"Unpickled reference implementation has type {type(instance)}")
        return instance
    
    def dump(self, dest: str = "reference.pkl") -> NoReturn:
        """
        Pickles this reference implementation to a file.

        Args:
            dest (``str``, optional): the path to the file
        """
        with open(dest, "wb+") as f:
            dill.dump(self, f)

    def run(self, observed_values: List[Tuple[Any, float]], group: Optional[str] = None) -> 'ReferenceResult':        
        """
        Runs the annotations tracked by this reference implementation against a memory footprint.

        Can run only specific annotations by specifying the ``group`` argument. Returns a 
        :py:class:`ReferenceResult<pybryt.ReferenceResult>` object.

        Args:
            observed_values (``list[tuple[object, float]]``): the memory footprint
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
            results.append(exp.check(observed_values))
        
        return ReferenceResult(self, results, group=group)

    @classmethod
    def compile(cls, file: str) -> Union['ReferenceImplementation', List['ReferenceImplementation']]:
        """
        Compiles a notebook or Python script into a single or list of reference implementations.

        
        """
        Annotation.reset_tracked_annotations()

        ext = os.path.splitext(file)[1]
        if ext == ".ipynb":
            source = notebook_to_string(file)

        else:
            with open(file) as f:
                source = f.read()

        env = {}
        exec(source, env)

        refs = []
        annots = []
        for _, v in env.items():
            if isinstance(v, cls):
                refs.append(v)
            # if isinstance(v, Annotation):
            #     annots.append(v)

        if not refs:
            if not Annotation.get_tracked_annotations():
                warnings.warn(f"Could not find any reference implementations in {file}")
            else:
                refs = [cls(deepcopy(Annotation.get_tracked_annotations()))]

        Annotation.reset_tracked_annotations()
        
        if len(refs) == 1:
            return refs[0]
        return refs


class ReferenceResult:
    """
    """

    reference: ReferenceImplementation
    results: List[AnnotationResult]
    group: Optional[str]

    def __init__(self, reference, annotation_results: List[AnnotationResult], group=None):
        self.reference = reference
        self.results = annotation_results
        self.group = group
    
    def __repr__(self):
        results = ',\n  '.join(repr(r) for r in self.results)
        return f"ReferenceResult([\n  {results}\n])"

    @property
    def correct(self):
        return all(r.satisfied for r in self.results)

    @property
    def messages(self):
        messages = []
        message_names = {}
        for r in self.results:
            m = r.messages
            for msg in m:
                if msg[1] is None:
                    messages.append(msg[0])
                else:
                    if msg[1] in message_names and not msg[2]:
                        idx = message_names[msg[1]]
                        messages[idx] = msg[0]
                    elif msg[1] not in message_names:
                        message_names[msg[1]] = len(messages)
                        messages.append(msg[0])
        return messages

    def to_array(self):
        """
        """
        return np.array([r.satisfied for r in self.results], dtype=int)
