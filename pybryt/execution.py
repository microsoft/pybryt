"""
"""

import os
import re
import time
import tempfile
import linecache
import dill
import nbformat

from nbconvert.preprocessors import ExecutePreprocessor
from copy import copy
from types import FrameType, FunctionType, ModuleType
from typing import Any, List, Tuple, Callable, Optional
from textwrap import dedent

from .preprocessors import IntermediateVariablePreprocessor
from .utils import make_secret, pickle_and_hash


NBFORMAT_VERSION = 4


# class ObservedValue:
#     """
#     """

#     timestamp: float
#     value: Any
#     fn_name: str
#     filename: str

#     def __init__(self, value: Any, fn_name: str = None, filename: str = None, timestamp: float = None):
#         self.value = value
#         self.fn_name = fn_name
#         self.filename = filename
#         self.timestamp = timestamp


def create_collector(skip_types: List[type] = [type, type(len), ModuleType, FunctionType], addl_filenames: List[str] = []) -> \
        Tuple[List[Tuple[Any, float]], Callable[[FrameType, str, Any], Callable]]:
    """
    """
    observed = []
    vars_not_found = {}
    hashes = set()
    # prune_pickup_idx = [0]
    # next_prune = [PRUNE_FREQUENCY]

    # def prune_observations():
    #     to_delete = []
    #     for i in range(prune_pickup_idx[0], len(observed)):
    #         try:
    #             h = pickle_and_hash(observed[i])
    #             if h in hashes[0]:
    #                 to_delete.append(i)
    #             else:
    #                 hashes[0] |= set([h])
    #         except:
    #             to_delete.append(i)
        
    #     to_delete.reverse()
    #     for i in to_delete:
    #         observed.pop(i)
        
    #     prune_pickup_idx[0] = len(observed)

    def track_value(val, seen_at):
        if type(val) in skip_types:
            return

        try:
            h = pickle_and_hash(val)
        except:
            return
        
        if h not in hashes:
            observed.append((copy(val), seen_at))
            hashes.add(h)

    # TODO: a way to track the cell of execution
    def collect_intermidiate_results(frame: FrameType, event: str, arg: Any):
        seen_at = time.time()

        name = frame.f_code.co_filename + frame.f_code.co_name
        
        if frame.f_code.co_filename.startswith("<ipython") or frame.f_code.co_filename in addl_filenames:
            if event == "line" or event == "return":

                line = linecache.getline(frame.f_code.co_filename, frame.f_lineno)
                tokens = set("".join(char if char.isalnum() or char == '_' else "\n" for char in line).split("\n"))
                for t in "".join(char if char.isalnum() or char == '_' or char == '.' else "\n" for char in line).split("\n"):
                    tokens.add(t)

                # for tracking the results of an assignment statement
                m = re.match(r"\s*(\w+)\s=.*", line)
                if m:
                    if name not in vars_not_found:
                        vars_not_found[name] = []
                    vars_not_found[name].append((m.group(1), seen_at))
                
                for t in tokens:
                    if "." in t:
                        try:
                            val = eval(t, frame.f_globals, frame.f_locals)
                            track_value(val, seen_at)
                        except:
                            pass

                    else:
                        if t in frame.f_locals:
                            val = frame.f_locals[t]
                            track_value(val, seen_at)
                                
                        elif t in frame.f_globals:
                            val = frame.f_globals[t]
                            track_value(val, seen_at)

            if event == "return" and type(arg) not in skip_types:
                track_value(arg, seen_at)

        elif (frame.f_back.f_code.co_filename.startswith("<ipython") or \
                frame.f_back.f_code.co_filename in addl_filenames) and event == "return":
            track_value(arg, seen_at)

        if event == "return" and name in vars_not_found:
            varnames = vars_not_found.pop(name)
            for t, timestamp in varnames:
                if t in frame.f_locals:
                    val = frame.f_locals[t]
                    track_value(val, timestamp)

                elif t in frame.f_globals:
                    val = frame.f_globals[t]
                    track_value(val, timestamp)
        
        # if len(observed) >= next_prune[0]:
        #     prune_observations()
        #     next_prune[0] = len(observed) + PRUNE_FREQUENCY

        return collect_intermidiate_results

    return observed, collect_intermidiate_results


def execute_notebook(nb: nbformat.NotebookNode, addl_filenames: List[str] = [], output: Optional[str] = None) -> \
        Tuple[float, float, List[Tuple[Any, float]]]:
    """
    """
    preprocessor = IntermediateVariablePreprocessor()
    nb = preprocessor.preprocess(nb)

    secret = make_secret()
    _, observed_fp = tempfile.mkstemp()

    first_cell = nbformat.v4.new_code_cell(dedent(f"""\
        import sys
        from pybryt.execution import create_collector
        observed_{secret}, cir = create_collector(addl_filenames={addl_filenames})
        sys.settrace(cir)
    """))

    last_cell = nbformat.v4.new_code_cell(dedent(f"""\
        sys.settrace(None)
        import dill
        from pybryt.utils import filter_pickleable_list
        filter_pickleable_list(observed_{secret})
        with open("{observed_fp}", "wb+") as f:
            dill.dump(observed_{secret}, f)
    """))

    nb['cells'].insert(0, first_cell)
    nb['cells'].append(last_cell)

    ep = ExecutePreprocessor(timeout=1200, allow_errors=True)

    execution_start = time.time()
    ep.preprocess(nb)
    execution_end = time.time()

    if output:
        with open(output, "w+") as f:
            nbformat.write(nb, f)

    with open(observed_fp, "rb") as f:
        observed = dill.load(f)

    os.remove(observed_fp)

    return execution_start, execution_end, observed
