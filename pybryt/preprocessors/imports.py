"""Preprocessor for collecting the set of imported modules"""

import ast
import nbformat

from typing import Set

from .abstract_preprocessor import AbstractPreprocessor


class ImportFinder(ast.NodeVisitor):
    """
    An AST walker for collecting imported modules.
    """

    def __init__(self) -> None:
        self.imports = set()

    def visit_Import(self, node: ast.AST) -> None:
        """
        Visit an import statement and collect the names of the imported modules
        """
        for alias in node.names:
            self.imports.add(alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.AST) -> None:
        """
        Visit an import from statement and collect the names of the imported modules
        """
        self.imports.add(node.module)


class ImportFindingPreprocessor(AbstractPreprocessor):
    """
    A notebook preprocessor that collects the set of modules import in the notebook.
    """

    imports: Set[str]

    def __init__(self) -> None:
        self.imports = set()
        super().__init__()

    def preprocess(self, nb: nbformat.NotebookNode) -> nbformat.NotebookNode:
        """
        Populate ``self.imports`` by walking the AST of each code cell.

        Args:
            nb (``nbformat.NotebookNode``): the notebook to be preprocessed

        Returns:
            ``nbformat.NotebookNode``: the notebook, unchanged
        """
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                code = cell['source']
                code = self.transformer_manager.transform_cell(code)
                tree = ast.parse(code)
                import_finder = ImportFinder()
                import_finder.visit(tree)
                self.imports.update(import_finder.imports)

        return nb
