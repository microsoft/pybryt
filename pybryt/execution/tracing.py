""""""

import sys
import inspect

from ..utils import make_secret


TRACING_VARNAME = "__PYBRYT_TRACING__"
TRACING_FUNC = None


def _currently_tracing():
    """
    Determines whether PyBryt is actively tracing the current call stack by looking at the parent
    frames and determining if ``__PYBRYT_TRACING__`` exists and is ``True`` in any of their globals.

    Returns:
        ``bool``: if PyBryt is currently tracing
    """
    frame = inspect.currentframe()
    while frame is not None:
        if TRACING_VARNAME in frame.f_globals and frame.f_globals[TRACING_VARNAME]:
            return True
        frame = frame.f_back
    return False


def _get_tracing_frame():
    """
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
    if not _currently_tracing():
        return
    frame = _get_tracing_frame() if frame is None else frame
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
    if not _currently_tracing() or (TRACING_FUNC is None and tracing_func is None):
        return
    if TRACING_FUNC is not None and tracing_func is None:
        tracing_func = TRACING_FUNC
    frame = _get_tracing_frame() if frame is None else frame
    vn = f"cir_{make_secret()}"
    vn2 = f"sys_{make_secret()}"
    frame.f_globals[vn] = tracing_func
    exec(f"import sys as {vn2}\n{vn2}.settrace({vn})", frame.f_globals, frame.f_locals)
