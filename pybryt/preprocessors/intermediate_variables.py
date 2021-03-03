import ast
import astunparse
import nbformat

from IPython.core.inputtransformer2 import TransformerManager

from ..utils import make_secret, notebook_to_string


def get_varname():
    return f"var_{make_secret()}"


def add_parents(root):
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node


class UnassignedVarWrapper(ast.NodeTransformer):

    _skip_node_types = [ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp, ast.Lambda]
    
    def __init__(self):
        super().__init__()
        self.insertions = [] # list of (parent, attr, idx, node)
    
    def visit(self, root, *args, **kwargs):
        self.root = root
        ret = super().visit(root, *args, **kwargs)
        for parent, attr, idx, node in self.insertions:
            getattr(parent, attr)[idx] = node
        return ret

    def transform_unassigned_node(self, node):
        if not isinstance(node.parent, ast.Assign):
            vn = get_varname()
            curr = node.parent
            body_child = None
            while not isinstance(curr, ast.Module):#hasattr(curr.parent, "body"):
                if hasattr(curr.parent, "body") and body_child is None:
                    body_child = curr
                
                # don't perform if in a comprehension
                if any(isinstance(curr, t) for t in type(self)._skip_node_types):
                    # for n in ast.iter_child_nodes(node):
                    #     self.visit(n)
                    return node
                
                curr = curr.parent
            
            curr = body_child
            try:
                idx = curr.parent.body.index(curr)
                is_else = False
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
        return self.transform_unassigned_node(node)
    
    def visit_BinOp(self, node):
        return self.transform_unassigned_node(node)


class IntermediateVariablePreprocessor():

    def preprocess(self, nb):
        # code = notebook_to_string(nb)
        transformer_mgr = TransformerManager()
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                code = cell['source']
                code = transformer_mgr.transform_cell(code)
                tree = ast.parse(code)
                add_parents(tree)
                transformer = UnassignedVarWrapper()
                tree = transformer.visit(tree)
                tree = ast.fix_missing_locations(tree)
                code = astunparse.unparse(tree)
                cell['source'] = code

        # nb = nbformat.v4.new_notebook()
        # nb['cells'].append(nbformat.v4.new_code_cell(code))
        return nb
