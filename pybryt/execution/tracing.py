"""Tracing function and controls"""

import inspect
import linecache
import re

from copy import copy
from types import FrameType, FunctionType, ModuleType
from typing import Any, Dict, List, Optional, Tuple, Callable

from .complexity import is_complexity_tracing_enabled
from .memory_footprint import Event, MemoryFootprint
from .utils import is_ipython_frame

from ..utils import make_secret, pickle_and_hash, UnpickleableError


ACTIVE_FOOTPRINT = None
TRACING_FUNC = None
TRACING_VARNAME = "__PYBRYT_TRACING__"


def create_collector(
    skip_types: List[type] = [type, type(len), FunctionType],
    addl_filenames: List[str] = [],
) -> Tuple[MemoryFootprint, Callable[[FrameType, str, Any], Callable]]:
    """
    Creates a memory footprint to collect observed values and a trace function.

    Any types in ``skip_types`` won't be tracked by the trace function. The trace function by 
    default only traces inside IPython but can be set to trace inside specific files using the
    ``addl_filenames`` argument, which should be a list absolute paths to files that should also be
    traced inside of.

    Args:
        skip_types (``list[type]``, optional): object types not to track
        addl_filenames (``list[str]``, optional): filenames to trace inside of in addition to 
            IPython
        
    Returns:
        ``tuple[MemoryFootprint, callable[[frame, str, object], callable]]``: the memory footprint
        and the trace function
    """
    global ACTIVE_FOOTPRINT
    vars_not_found: Dict[str, List[Tuple[str, str, int]]] = {}
    footprint = MemoryFootprint()

    def track_value(val: Any, event_name: str, seen_at: Optional[int] = None):
        """
        Tracks a value in ``footprint``. Checks that the value has not already been tracked by 
        pickling it and hashing the pickled object and comparing it to ``hashes``. If pickling is
        unsuccessful, the value is not tracked.

        Args:
            val (``object``): the object to be tracked
            event_name (``str``): the event name provided by ``sys.settrace``
            seen_at (``int``, optional): an overriding step counter value
        """
        try:
            if hasattr(val, "__module__"):
                footprint.add_imports(val.__module__.split(".")[0])

            if type(val) in skip_types:
                return

            if isinstance(val, ModuleType):
                footprint.add_imports(val.__name__.split(".")[0])
                return

            event = Event.from_event_name(event_name)
            footprint.add_value(copy(val), seen_at, event)

        # if something fails, don't track
        except:
            return

    def track_call(frame):
        """
        Tracks a call in ``calls`` as a tuple of ``(filename, function name)``.

        Args:
            frame (``types.FrameType``): the frame of the call
        """
        footprint.add_call(frame.f_code.co_filename, frame.f_code.co_name)

    # TODO: a way to track the cell of execution
    def collect_intermidiate_results(frame: FrameType, event: str, arg: Any):
        """
        Trace function for PyBryt.
        """
        if is_ipython_frame(frame) or frame.f_code.co_filename in addl_filenames:
            footprint.increment_counter()  # increment student code step counter

        if event == "call":
            track_call(frame)
            return collect_intermidiate_results

        # return if tracking is disabled by a compelxity check
        if is_complexity_tracing_enabled():
            return collect_intermidiate_results

        name = frame.f_code.co_filename + frame.f_code.co_name

        if is_ipython_frame(frame) or frame.f_code.co_filename in addl_filenames:
            if event == "line" or event == "return":

                line = linecache.getline(frame.f_code.co_filename, frame.f_lineno)
                tokens = set("".join(char if char.isalnum() or char == '_' else "\n" for char in line).split("\n"))
                for t in "".join(char if char.isalnum() or char == '_' or char == '.' else "\n" for char in line).split("\n"):
                    tokens.add(t)
                tokens = sorted(tokens)  # sort for stable ordering
                
                for t in tokens:
                    if "." in t:
                        try:
                            float(t)  # prevent adding floats prematurely
                            continue
                        except ValueError:
                            pass

                        try:
                            val = eval(t, frame.f_globals, frame.f_locals)
                            track_value(val, event)
                        except:
                            pass

                    else:
                        if t in frame.f_locals:
                            val = frame.f_locals[t]
                            track_value(val, event)
                                
                        elif t in frame.f_globals:
                            val = frame.f_globals[t]
                            track_value(val, event)
                
                # for tracking the results of an assignment statement
                m = re.match(r"^\s*(\w+)(\[[^\]]\]|(\.\w+)+)*\s=.*", line)
                if m:
                    if name not in vars_not_found:
                        vars_not_found[name] = []
                    vars_not_found[name].append((m.group(1), event, footprint.counter.get_value()))

            if event == "return":
                track_value(arg, event)

        elif (is_ipython_frame(frame) or frame.f_back.f_code.co_filename in addl_filenames) and \
                event == "return":
            track_value(arg, event)

        if event == "return" and name in vars_not_found:
            varnames = vars_not_found.pop(name)
            for t, event_name, step in varnames:
                if t in frame.f_locals:
                    val = frame.f_locals[t]
                    track_value(val, event_name, step)

                elif t in frame.f_globals:
                    val = frame.f_globals[t]
                    track_value(val, event_name, step)

        return collect_intermidiate_results

    ACTIVE_FOOTPRINT = footprint
    return footprint, collect_intermidiate_results


def get_tracing_frame():
    """
    Returns the frame that is being traced by looking for the ``__PYBRYT_TRACING__`` global variable.

    Returns:
        the frame being traced or ``None`` of no tracing is occurring
    """
    frame = inspect.currentframe()
    while frame is not None:
        if TRACING_VARNAME in frame.f_globals and frame.f_globals[TRACING_VARNAME]:
            return frame
        frame = frame.f_back
    return None


def tracing_off(frame=None, save_func=True):
    """
    Turns off PyBryt's tracing if tracing is occurring in this call stack. If PyBryt is not tracing,
    takes no action.

    This method can be used in students' notebooks to include code that shouldn't be traced as part
    of the submission, e.g. demo code or ungraded code. In the example below, the call that creates
    ``x2`` is traced but the one to create ``x3`` is not.

    .. code-block:: python

        def pow(x, a):
            return x ** a

        x2 = pow(x, 2)

        pybryt.tracing_off()
        x3 = pow(x, 3)
    """
    global TRACING_FUNC
    frame = get_tracing_frame() if frame is None else frame
    if frame is None:
        return
    if save_func:
        TRACING_FUNC = frame.f_trace
    vn = f"sys_{make_secret()}"
    exec(f"import sys as {vn}\n{vn}.settrace(None)", frame.f_globals, frame.f_locals)


def tracing_on(frame=None, tracing_func=None):
    """
    Turns tracing on if PyBryt was tracing the call stack. If PyBryt is not tracing or
    :py:meth:`tracing_off<pybryt.tracing_off>` has not been called, no action is taken.

    This method can be used in students' notebooks to turn tracing back on after deactivating tracing
    for ungraded code In the example below, ``x4`` is traced because ``tracing_on`` is used after
    ``tracing_off`` and the creation of ``x3``.

    .. code-block:: python

        def pow(x, a):
            return x ** a

        x2 = pow(x, 2)

        pybryt.tracing_off()
        x3 = pow(x, 3)
        pybryt.tracing_on()

        x4 = pow(x, 4)
    """
    global TRACING_FUNC
    frame = get_tracing_frame() if frame is None else frame
    if frame is None or (TRACING_FUNC is None and tracing_func is None):
        return
    if TRACING_FUNC is not None and tracing_func is None:
        tracing_func = TRACING_FUNC
    vn = f"cir_{make_secret()}"
    vn2 = f"sys_{make_secret()}"
    frame.f_globals[vn] = tracing_func
    exec(f"import sys as {vn2}\n{vn2}.settrace({vn})", frame.f_globals, frame.f_locals)
    frame.f_trace = tracing_func


class no_tracing:
    """
    A context manager for turning tracing off for a block of code in a submission.

    If PyBryt is tracing code, any code inside this context will not be traced for values in memory.
    If PyBryt is not tracing, no action is taken.

    .. code-block:: python

        with pybryt.no_tracing():
            # this code is not traced
            foo(1)
        
        # this code is traced
        foo(2)
    """

    def __enter__(self):
        tracing_off()

    def __exit__(self, exc_type, exc_value, traceback):
        tracing_on()
        return False


class FrameTracer:
    """
    A class for managing the tracing of a call stack.

    Args:
        frame (``FrameType``): the frame to initialize tracing in
    """

    footprint: Optional[MemoryFootprint]
    """the memory footprint being populated"""

    frame: FrameType
    """the frame being traced"""

    _tracing_already_enabled: bool
    """whether tracing was already enabled when ``start_trace`` was called"""

    def __init__(self, frame: FrameType) -> None:
        self.frame = frame
        self.footprint = None
        self._tracing_already_enabled = False

    def start_trace(self, **kwargs) -> None:
        """
        Create a collector and memory footprint and start tracing execution in the frame. Returns
        a boolean indicating whether tracing was enabled.

        Args:
            **kwargs: additional keyword arguments passed to ``create_collector``

        Returns:
            ``bool``: whether this call initiated tracing (``False`` if tracing was already enabled)
        """
        self._tracing_already_enabled = get_tracing_frame() is not None
        if self._tracing_already_enabled:
            self.footprint = get_active_footprint()
            return False

        self.footprint, cir = create_collector(**kwargs)
        self.frame.f_globals[TRACING_VARNAME] = True
        tracing_on(tracing_func=cir)
        return True

    def end_trace(self) -> None:
        """
        End execution tracing in the frame.
        """
        if not self._tracing_already_enabled:
            tracing_off(save_func=False)
            self.frame.f_globals[TRACING_VARNAME] = False

    def get_footprint(self) -> MemoryFootprint:
        """
        Return the memory footprint that was populated by the trace function.

        Returns:
            :py:class:`pybryt.execution.memory_footprint.MemoryFootprint`: the memory footprint
        """
        return self.footprint


def get_active_footprint() -> Optional[MemoryFootprint]:
    """
    Get the active memory footprint if present, else ``None``.

    Returns:
        :py:class:`pybryt.execution.memory_footprint.MemoryFootprint`: the memory footprint
    """
    return ACTIVE_FOOTPRINT
