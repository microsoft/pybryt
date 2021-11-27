"""Submission preprocessors for PyBryt"""

import nbformat

from typing import List, Set

from .abstract_preprocessor import AbstractPreprocessor
from .imports import ImportFindingPreprocessor
from .intermediate_variables import IntermediateVariablePreprocessor


PREPROCESSORS = [
    ImportFindingPreprocessor,
    IntermediateVariablePreprocessor
]


class NotebookPreprocessor(AbstractPreprocessor):
    """
    A class for applying a series of preprocessors to a notebook.
    """

    preprocessors: List[AbstractPreprocessor]

    def __init__(self) -> None:
        self.preprocessors = []
        for preprocessor_class in PREPROCESSORS:
            self.preprocessors.append(preprocessor_class())

    def preprocess(self, nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
        for preprocessor in self.preprocessors:
            nb = preprocessor.preprocess(nb)

        return nb

    def get_imports(self) -> Set[str]:
        """
        Get the set of imports from the :py:class:`ImportFinder<pybryt.preprocessors.imports.ImportFindingPreprocessor`.

        Returns:
            ``set[str]``: the set of modules imported
        """
        import_finder_idx = [isinstance(p, ImportFindingPreprocessor) for p in self.preprocessors].index(True)
        return self.preprocessors[import_finder_idx].imports
