""""""

from ..utils import AttrDict


def generate_mocked_frame(
    co_filename, co_name, f_lineno, f_globals={}, f_locals={}, f_trace=None, f_back=None
):
    """
    Factory for generating objects with the instance variables of an ``inspect`` frame that are 
    needed by PyBryt's trace function.
    """
    code = AttrDict({
        "co_filename": co_filename,
        "co_name": co_name,
    })
    return AttrDict({
        "f_lineno": f_lineno,
        "f_globals": f_globals,
        "f_locals": f_locals,
        "f_trace": f_trace,
        "f_back": f_back,
        "f_code": code,
    })