"""Submission execution internals for PyBryt"""

import os
import re
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


def create_collector(skip_types: List[type] = [type, type(len), ModuleType, FunctionType], addl_filenames: List[str] = []) -> \
        Tuple[List[Tuple[Any, int]], Callable[[FrameType, str, Any], Callable]]:
    """
    Creates a list to collect observed values and a trace function.

    Any types in ``skip_types`` won't be tracked by the trace function. The trace function by 
    default only traces inside IPython but can be set to trace inside specific files using the
    ``addl_filenames`` argument, which should be a list absolute paths to files that should also be
    traced inside of.

    Args:
        skip_types (``list[type]``, optional): object types not to track
        addl_filenames (``list[str]``, optional): filenames to trace inside of in addition to 
            IPython
        
    Returns:
        ``tuple[list[tuple[object, int]], callable[[frame, str, object], callable]]``: the list
        of tuples of observed objects and their timestamps, and the trace function
    """
    observed = []
    vars_not_found = {}
    hashes = set()
    counter = [0]

    def track_value(val, seen_at=None):
        """
        Tracks a value in ``observed``. Checks that the value has not already been tracked by 
        pickling it and hashing the pickled object and comparing it to ``hashes``. If pickling is
        unsuccessful, the value is not tracked.

        Args:
            val (``object``): the object to be tracked
            seen_at (``int``, optional): an overriding step counter value
        """
        if type(val) in skip_types:
            return

        try:
            h = pickle_and_hash(val)
        except:
            return
        
        if seen_at is None:
            seen_at = counter[0]
            counter[0] += 1
        
        if h not in hashes:
            observed.append((copy(val), seen_at))
            hashes.add(h)

    # TODO: a way to track the cell of execution
    def collect_intermidiate_results(frame: FrameType, event: str, arg: Any):
        """
        Trace function for PyBryt.
        """
        name = frame.f_code.co_filename + frame.f_code.co_name
        
        if frame.f_code.co_filename.startswith("<ipython") or frame.f_code.co_filename in addl_filenames:
            if event == "line" or event == "return":

                line = linecache.getline(frame.f_code.co_filename, frame.f_lineno)
                tokens = set("".join(char if char.isalnum() or char == '_' else "\n" for char in line).split("\n"))
                for t in "".join(char if char.isalnum() or char == '_' or char == '.' else "\n" for char in line).split("\n"):
                    tokens.add(t)
                
                for t in tokens:
                    if "." in t:
                        try:
                            val = eval(t, frame.f_globals, frame.f_locals)
                            track_value(val)
                        except:
                            pass

                    else:
                        if t in frame.f_locals:
                            val = frame.f_locals[t]
                            track_value(val)
                                
                        elif t in frame.f_globals:
                            val = frame.f_globals[t]
                            track_value(val)
                
                # for tracking the results of an assignment statement
                m = re.match(r"\s*(\w+)\s=.*", line)
                if m:
                    if name not in vars_not_found:
                        vars_not_found[name] = []
                    vars_not_found[name].append((m.group(1), counter[0]))
                    counter[0] += 1

            if event == "return" and type(arg) not in skip_types:
                track_value(arg)

        elif (frame.f_back.f_code.co_filename.startswith("<ipython") or \
                frame.f_back.f_code.co_filename in addl_filenames) and event == "return":
            track_value(arg)

        if event == "return" and name in vars_not_found:
            varnames = vars_not_found.pop(name)
            for t, step in varnames:
                if t in frame.f_locals:
                    val = frame.f_locals[t]
                    track_value(val, step)

                elif t in frame.f_globals:
                    val = frame.f_globals[t]
                    track_value(val, step)

        return collect_intermidiate_results

    return observed, collect_intermidiate_results


def execute_notebook(nb: nbformat.NotebookNode, addl_filenames: List[str] = [], output: Optional[str] = None) -> \
        Tuple[int, List[Tuple[Any, int]]]:
    """
    Executes a submission using ``nbconvert`` and returns the memory footprint.

    Takes in a notebook object and preprocesses it before running it through the 
    ``nbconvert.ExecutePreprocessor`` to execute it. The notebook writes the memory footprint, a 
    list of observed values and their timestamps, to a file, which is loaded using ``dill`` by this
    function. Errors during execution are ignored, and the executed notebook can be written to a 
    file using the ``output`` argument.

    Args:
        nb (``nbformat.NotebookNode``): the notebook to be executed
        addl_filenames (``list[str]``, optional): a list of additional files to trace inside
        output (``str``, optional): a file path at which to write the executed notebook

    Returns:
        ``tuple[int, list[tuple[object, int]]]``: the number of execution steps and the memory 
        footprint
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

    ep.preprocess(nb)

    if output:
        with open(output, "w+") as f:
            nbformat.write(nb, f)

    with open(observed_fp, "rb") as f:
        observed = dill.load(f)

    os.remove(observed_fp)

    n_steps = max([t[1] for t in observed])

    return n_steps, observed
