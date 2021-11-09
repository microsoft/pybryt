"""Execution utilities"""

import os

from types import FrameType


def is_ipython_frame(frame: FrameType) -> bool:
    """
    Determine whether a frame is being executed by IPython.

    Args:
        frame (``types.FrameType``): the frame to examine

    Returns:
        ``bool``: whether the frame is an IPython frame
    """
    filename = frame.f_code.co_filename
    parent_dir = os.path.split(os.path.split(filename)[0])[1]
    return filename.startswith("<ipython") or parent_dir.startswith("ipykernel_")
