"""Abstract base class for notebook preprocessors"""

import nbformat

from abc import ABC, abstractmethod
from IPython.core.inputtransformer2 import TransformerManager


class AbstractPreprocessor(ABC):
    """
    An abstract base class for notebook execution preprocessors.
    """

    transformer_manager: TransformerManager

    def __init__(self) -> None:
        self.transformer_manager = TransformerManager()

    @abstractmethod
    def preprocess(self, nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
        """
        Preprocesses a notebook for execution.

        Args:
            nb (``nbformat.NotebookNode``): the notebook to be preprocessed

        Returns:
            ``nbformat.NotebookNode``: the updated notebook
        """
        ...  # pragma: no cover
