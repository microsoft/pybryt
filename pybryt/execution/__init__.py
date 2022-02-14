"""Submission execution internals for PyBryt"""

__all__ = ["check_time_complexity", "MemoryFootprint", "no_tracing", "TimeComplexityResult"]

import os
import dill
import nbformat

from nbconvert.preprocessors import ExecutePreprocessor
from copy import deepcopy
from tempfile import mkstemp
from typing import List, Optional
from textwrap import dedent

from .complexity import check_time_complexity, is_complexity_tracing_enabled, TimeComplexityResult
from .memory_footprint import Event, MemoryFootprint, MemoryFootprintValue
from .tracing import (
    create_collector,
    FrameTracer,
    get_tracing_frame,
    no_tracing,
    tracing_off, 
    tracing_on,
)

from ..preprocessors import NotebookPreprocessor
from ..utils import make_secret


NBFORMAT_VERSION = 4


def execute_notebook(
    nb: nbformat.NotebookNode, 
    nb_path: str, 
    addl_filenames: List[str] = [], 
    timeout: Optional[int] = 1200
) -> MemoryFootprint:
    """
    Executes a submission using ``nbconvert`` and returns the memory footprint.

    Takes in a notebook object and preprocesses it before running it through the 
    ``nbconvert.ExecutePreprocessor`` to execute it. The notebook writes the memory footprint, a 
    list of observed values and their timestamps, to a file, which is loaded using ``dill`` by this
    function. Errors during execution are ignored, and the executed notebook can be written to a 
    file using the ``output`` argument.

    Args:
        nb (``nbformat.NotebookNode``): the notebook to be executed
        nb_path (``str``): path to the notebook ``nb``
        addl_filenames (``list[str]``, optional): a list of additional files to trace inside
        output (``str``, optional): a file path at which to write the executed notebook
        timeout (``int``, optional): number of seconds to allow for notebook execution; set to 
            ``None`` for no time limit

    Returns:
        :py:class:`pybryt.execution.memory_footprint.MemoryFootprint`: the memory footprint
    """
    nb = deepcopy(nb)
    preprocessor = NotebookPreprocessor()
    nb = preprocessor.preprocess(nb)

    _, footprint_fp = mkstemp()
    nb_dir = os.path.abspath(os.path.split(nb_path)[0])

    secret = make_secret()
    frame_tracer_varname = f"frame_tracer_{secret}"

    first_cell = nbformat.v4.new_code_cell(dedent(f"""\
        import inspect
        import sys
        from pybryt.execution import FrameTracer
        {frame_tracer_varname} = FrameTracer(inspect.currentframe())
        {frame_tracer_varname}.start_trace(addl_filenames={addl_filenames})
        %cd {nb_dir}
    """))

    last_cell = nbformat.v4.new_code_cell(dedent(f"""\
        {frame_tracer_varname}.end_trace()
        footprint = {frame_tracer_varname}.get_footprint()
        footprint.filter_out_unpickleable_values()
        import dill
        with open("{footprint_fp}", "wb+") as f:
            dill.dump(footprint, f)
    """))

    nb['cells'].insert(0, first_cell)
    nb['cells'].append(last_cell)

    ep = ExecutePreprocessor(timeout=timeout, allow_errors=True)
    ep.preprocess(nb)

    with open(footprint_fp, "rb") as f:
        footprint: MemoryFootprint = dill.load(f)

    os.remove(footprint_fp)

    footprint.add_imports(*preprocessor.get_imports())
    footprint.set_executed_notebook(nb)

    return footprint
