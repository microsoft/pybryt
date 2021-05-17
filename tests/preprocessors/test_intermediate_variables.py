""""""

import random
import nbformat

from textwrap import dedent

from pybryt.preprocessors import IntermediateVariablePreprocessor


def test_preprocessor():
    """
    """
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(dedent("""\
        a = True
        b = False
        f = lambda x: not x

        g = f(a) + f(b)

        if f(a) and f(b):
            print("hi")

        if f(a) or f(b):
            print("hi")
        
        if a or b:
            print("bye")

        l = [f(i) for i in [a, b]]

        f = lambda x: [not i for i in l]
        l = [a, b]
        if all(f(l)):
            print("ok")
        else:
            l = any(f(l))
    """)))

    ivp = IntermediateVariablePreprocessor()

    random.seed(42)
    nb = ivp.preprocess(nb)
    print(nb.cells[0].source)
    assert len(nb.cells) == 1
    assert nb.cells[0].source.strip() == dedent("""\
        a = True
        b = False
        f = (lambda x: (not x))
        var_HBRPOI = f(a)
        var_G8F1CB = f(b)
        g = (var_HBRPOI + var_G8F1CB)
        var_FNO6B9 = f(a)
        if (var_FNO6B9):
            var_M80O2R = f(b)
        if (var_FNO6B9 and var_M80O2R):
            var_AK1VRJ = print('hi')
            var_AK1VRJ
        var_NVGFYG = f(a)
        if (not (var_NVGFYG)):
            var_WWQC38 = f(b)
        if (var_NVGFYG or var_WWQC38):
            var_HYF9SX = print('hi')
            var_HYF9SX
        if (a or b):
            var_MECOSF = print('bye')
            var_MECOSF
        l = [f(i) for i in [a, b]]
        f = (lambda x: [(not i) for i in l])
        l = [a, b]
        var_KXWNRE = f(l)
        var_K8PK3Y = all(var_KXWNRE)
        if var_K8PK3Y:
            var_R9OUDO = print('ok')
            var_R9OUDO
        else:
            var_CUZREN = f(l)
            l = any(var_CUZREN)
    """).strip()
