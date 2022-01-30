""""""

import numpy as np
import sys

from unittest import mock

from pybryt import MemoryFootprint, no_tracing
from pybryt.execution import create_collector, FrameTracer, tracing_off, tracing_on
from pybryt.execution.memory_footprint import Event

from .utils import generate_mocked_frame


__PYBRYT_TRACING__ = False


def test_trace_function():
    """
    """
    np.random.seed(42)
    
    tracked_filepath = "/path/to/tracked/file.py"

    frame = generate_mocked_frame("<ipython-abc123>", "foo", 3)
    footprint, cir = create_collector(addl_filenames=[tracked_filepath])

    arr = np.random.uniform(-100, 100, size=(100, 100))
    cir(frame, "return", arr)
    assert len(footprint) == 1
    assert np.allclose(footprint.get_value(0).value, arr)
    assert footprint.get_value(0).timestamp == 1
    assert footprint.get_value(0).event == Event.RETURN

    # test value in skip_types
    cir(frame, "return", type(1))
    assert len(footprint) == 1

    # test pickling error
    with mock.patch("dill.dumps") as mocked_dumps:
        mocked_dumps.side_effect = Exception()
        cir(frame, "return", 1)
    
    assert len(footprint) == 1

    # test call event
    assert len(footprint.calls) == 0
    cir(frame, "call", None)
    assert len(footprint.calls) == 1
    assert footprint.calls[0] == ("<ipython-abc123>", "foo")

    frame = generate_mocked_frame(
        "<ipython-abc123>", "foo", 3, {"data": arr}
    )

    # check line processing working
    with mock.patch("linecache.getline") as mocked_linecache:

        # check eval call for attributes
        mocked_linecache.return_value = "data.T"
        cir(frame, "line", None)
        assert len(footprint) == 2
        assert np.allclose(footprint.get_value(1).value, arr.T)
        assert footprint.get_value(1).timestamp == 5
        assert footprint.get_value(1).event == Event.LINE

        # check failed eval call for attributes
        mocked_linecache.return_value = "data.doesnt_exist"
        cir(frame, "line", None)
        assert len(footprint) == 2

        # check looking in frame locals + globals
        frame.f_globals["more_data"] = np.random.uniform(-100, 100, size=(100, 100))
        frame.f_locals["more_data"] = np.random.uniform(-100, 100, size=(100, 100))
        mocked_linecache.return_value = "more_data"
        cir(frame, "line", None)
        assert len(footprint) == 3
        assert np.allclose(footprint.get_value(2).value, frame.f_locals["more_data"])
        assert footprint.get_value(2).timestamp == 7

        # check that we track assignment statements on function return
        mocked_linecache.return_value = "even_more_data = more_data ** 2"
        cir(frame, "line", None)
        assert len(footprint) == 3

        mocked_linecache.return_value = "even_more_data_2 = more_data ** 3"
        cir(frame, "line", None)
        assert len(footprint) == 3

        # check that floats aren't added with the eval call
        mocked_linecache.return_value = "event_more_data_3 = [2.1, 1000, 100.3]"
        cir(frame, "line", None)
        assert len(footprint) == 3

        frame.f_locals["even_more_data"] = frame.f_locals["more_data"] ** 2
        frame.f_globals["even_more_data_2"] = frame.f_locals["more_data"] ** 3
        mocked_linecache.return_value = ""
        cir(frame, "return", None)
        assert len(footprint) == 6
        assert footprint.get_value(3).value is None
        assert footprint.get_value(3).timestamp == 11
        assert np.allclose(footprint.get_value(4).value, frame.f_locals["more_data"] ** 2)
        assert footprint.get_value(4).timestamp == 8
        assert np.allclose(footprint.get_value(5).value, frame.f_locals["more_data"] ** 3)
        assert footprint.get_value(5).timestamp == 9

        # check that skip_types respected
        frame.f_locals["none_type"] = type(None)
        mocked_linecache.return_vaue = "none_type"
        cir(frame, "line", None)
        assert len(footprint) == 6

        # check that addl_filenames respected
        frame = generate_mocked_frame(tracked_filepath, "bar", 100, f_back=frame)
        frame.f_locals["data"] = arr
        mocked_linecache.return_value = "arr = -1 * data"
        cir(frame, "line", None)
        frame.f_locals["arr"] = -1 * arr
        cir(frame, "return", None) # run a return since arr shows up in vars_not_found
        assert len(footprint) == 7
        assert np.allclose(footprint.get_value(6).value, -1 * arr)
        assert footprint.get_value(6).timestamp == 14
    
    # check that IPython child frame return values are tracked
    frame = generate_mocked_frame("/path/to/file.py", "bar", 100, f_back=frame)
    cir(frame, "line", None)
    assert len(footprint) == 7

    cir(frame, "return", np.exp(arr))
    assert len(footprint) == 8
    assert np.allclose(footprint.get_value(7).value, np.exp(arr))
    assert footprint.get_value(7).timestamp == 14

    assert len(footprint.calls) == 1
    frame = generate_mocked_frame("/path/to/foo.py", "bar", 100)
    cir(frame, "call", None)
    assert len(footprint.calls) == 2
    assert footprint.calls[0] == ("<ipython-abc123>", "foo")
    assert footprint.calls[1] == ("/path/to/foo.py", "bar")

    # test ipykernel v6 frame filename
    frame = generate_mocked_frame("/var/8k/ipykernel_495995/29304985.py", "foo", 3)
    footprint, cir = create_collector(addl_filenames=[tracked_filepath])

    arr = np.random.uniform(-100, 100, size=(100, 100))
    cir(frame, "return", arr)
    assert len(footprint) == 1
    assert np.allclose(footprint.get_value(0).value, arr)
    assert footprint.get_value(0).timestamp == 1

    # check that imported modules are correctly tracked
    with mock.patch.object(footprint, "add_imports") as mocked_add_imports:
        class Foo:
            pass

        cir(frame, "return", Foo)
        mocked_add_imports.assert_called_with(Foo.__module__.split(".")[0])

        cir(frame, "return", np)
        mocked_add_imports.assert_called_with(np.__name__)


def test_tracing_control():
    """
    """
    global __PYBRYT_TRACING__
    trace = lambda frame, event, arg: trace

    __PYBRYT_TRACING__ = True
    with mock.patch("sys.settrace") as mocked_settrace:
        tracing_off()
        mocked_settrace.assert_called()

    with mock.patch("sys.settrace") as mocked_settrace:
        tracing_on()
        if sys.gettrace() is not None:
            mocked_settrace.assert_called()

    __PYBRYT_TRACING__ = False
    with mock.patch("sys.settrace") as mocked_settrace:
        tracing_off()
        mocked_settrace.assert_not_called()

    with mock.patch("sys.settrace") as mocked_settrace:
        tracing_on()
        mocked_settrace.assert_not_called()


def test_tracing_context_manager():
    """
    """
    with mock.patch("pybryt.execution.tracing.tracing_off") as mocked_off, \
            mock.patch("pybryt.execution.tracing.tracing_on") as mocked_on:
        with no_tracing():
            mocked_off.assert_called()
            mocked_on.assert_not_called()
        mocked_on.assert_called()


def test_frame_tracer():
    """
    Tests for ``pybryt.execution.tracing.FrameTracer``.
    """
    frame = generate_mocked_frame("<ipython-abc123>", "foo", 3)
    tracer = FrameTracer(frame)

    with mock.patch("pybryt.execution.tracing.tracing_on") as mocked_on, \
            mock.patch("pybryt.execution.tracing.tracing_off") as mocked_off, \
            mock.patch("pybryt.execution.tracing.create_collector") as mocked_create, \
            mock.patch("pybryt.execution.tracing.get_tracing_frame") as mocked_get:
        kwargs = {"foo": "bar"}
        mocked_create.return_value = (MemoryFootprint(), lambda a, b, c: None)

        # check that when tracing is enabled no action is taken
        mocked_get.return_value = frame
        assert not tracer.start_trace()
        mocked_on.assert_not_called()

        tracer.end_trace()
        mocked_off.assert_not_called()

        mocked_get.return_value = None

        assert tracer.start_trace(**kwargs)
        mocked_create.assert_called_once_with(**kwargs)
        mocked_on.assert_called_once_with(tracing_func=mocked_create.return_value[1])
        assert frame.f_globals["__PYBRYT_TRACING__"]
        assert isinstance(tracer.footprint, MemoryFootprint)

        tracer.end_trace()
        mocked_off.assert_called_once_with(save_func=False)
        assert not frame.f_globals["__PYBRYT_TRACING__"]

        assert isinstance(tracer.get_footprint(), MemoryFootprint)
