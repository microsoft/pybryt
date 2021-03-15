"""Intermediate variable preprocessor for PyBryt submissions"""

import ast
import astunparse
import nbformat

from IPython.core.inputtransformer2 import TransformerManager

from ..utils import make_secret, notebook_to_string


class UnassignedVarWrapper(ast.NodeTransformer):
    """
    AST node transformer that creates intermediate variables for any calls in nested expressions

    Transforms an AST such that every ``Call`` or ``BinOp`` which does not have an ``Assign`` as its 
    parent is added to the AST in the closest parent node with a ``body`` as an intermediate v
    ariable. The node is replaced with a ``Name`` of the new variable name. Any nodes who have a 
    parent node that is an instance of any node type in ``UnassignedVarWrapper._skip_node_types`` 
    is not transformed.

    Attrs:
        insertions (``list[tuple[ast.Node, str, int, ast.Node]]``): a tuple of insertions to make in 
            a node's body; for the tuple ``(parent, attr, idx, node)``, performing the insertion is 
            done by running ``getattr(parent, attr).insert(idx, node)``
    """

    _skip_node_types = [ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp, ast.Lambda]

    def __init__(self):
        super().__init__()
        self.insertions = [] # list of (parent, attr, idx, node)

    @staticmethod
    def add_parents(root):
        """
        Adds a ``parent`` field to each node in the AST rooted at ``root`` pointed to the direct
        parent of that node.

        Args:
            root (``ast.Node``): the root of the AST
        """
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                child.parent = node

    @staticmethod
    def get_varname():
        """
        Returns a random, valid Python identifier as a string

        Returns:
            ``str``: the variable name
        """
        return f"var_{make_secret()}"
    
    def visit(self, root, *args, **kwargs):
        """
        Visits each node in the tree to transform all ``Call`` nodes and then performs the node
        insertions specified in ``self.insertions``. Arguments and return values are the same as 
        ``ast.NodeTransformer``.
        """
        self.root = root
        ret = super().visit(root, *args, **kwargs)
        for parent, attr, idx, node in self.insertions:
            getattr(parent, attr)[idx] = node
        return ret

    def transform_unassigned_node(self, node):
        """
        Transforms an unassigned node into an intermediate variable to be inserted in the closest
        ancestor node with a body. Updates ``self.insertions`` with the insertion needed to be
        performed after ``super().visit`` finishes.

        Args:
            node (``ast.Node``): the node to be transformed; should have its ``parent`` attribute
                set by ``self.add_parents``

        Returns:
            ``ast.Node``: an untransformed node if no transformation was required or the new 
            ``Name`` node to be inserted into the AST if transformation was required.
        """
        if not isinstance(node.parent, ast.Assign):
            vn = self.get_varname()
            curr = node.parent
            body_child = None
            while not isinstance(curr, ast.Module):#hasattr(curr.parent, "body"):
                if hasattr(curr.parent, "body") and not (hasattr(curr.parent, "test") and \
                        curr.parent.test == curr) and body_child is None:
                    body_child = curr
                
                # don't perform if in a comprehension
                if any(isinstance(curr, t) for t in type(self)._skip_node_types):
                    # for n in ast.iter_child_nodes(node):
                    #     self.visit(n)
                    return node
                
                curr = curr.parent
            
            curr = body_child
            is_else = False
            try:
                idx = curr.parent.body.index(curr)
            except ValueError:
                if isinstance(curr.parent, ast.If):
                    idx = curr.parent.orelse.index(curr)
                    is_else = True
                else:
                    raise
            
            curr = curr.parent
            new_assign = ast.Assign([ast.Name(vn, ctx=ast.Load())], node, ctx=ast.Load())
            new_assign.parent = curr
            if is_else:
                curr.orelse.insert(idx, new_assign)
                self.insertions.append((curr, "orelse", idx, new_assign))
            else:
                curr.body.insert(idx, new_assign)
                self.insertions.append((curr, "body", idx, new_assign))

            new_name = ast.Name(vn, ctx=ast.Load())
            new_name.parent = node.parent
            node.parent = new_assign

            self.visit(new_assign)

            return new_name
        else:
            for n in ast.iter_child_nodes(node):
                self.visit(n)
        return node
    
    def visit_Call(self, node):
        """
        Transforms all ``Call`` nodes if necessary.
        """
        return self.transform_unassigned_node(node)
    
    def visit_BinOp(self, node):
        """
        Transforms all ``BinOp`` nodes if necessary.
        """
        return self.transform_unassigned_node(node)


class IntermediateVariablePreprocessor():
    """
    Preprocessor for inserting intermediate variables in a notebook to assist in tracing.
    """

    def preprocess(self, nb):
        """
        Preprocesses a notebook by inserting intermediate variables.

        Iterates through the cells in a notebook, converting them to ASTs and using
        :py:class:`UnassignedVarWrapper<pybryt.preprocessors.intedmediate_variablea.UnassignedVarWrapper>`
        to processor the code and ``astunparse.unparse`` to turn the result back into a string. 
        Updates the notebook inplace.

        Args:
            nb (``nbformat.NotebookNode``): the notebook to be preprocessed

        Returns:
            ``nbformat.NotebookNode``: the updated notebook
        """
        # code = notebook_to_string(nb)
        transformer_mgr = TransformerManager()
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                code = cell['source']
                code = transformer_mgr.transform_cell(code)
                tree = ast.parse(code)
                transformer = UnassignedVarWrapper()
                transformer.add_parents(tree)
                tree = transformer.visit(tree)
                tree = ast.fix_missing_locations(tree)
                code = astunparse.unparse(tree)
                cell['source'] = code

        # nb = nbformat.v4.new_notebook()
        # nb['cells'].append(nbformat.v4.new_code_cell(code))
        return nb
