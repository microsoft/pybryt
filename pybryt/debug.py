"""Debug mode"""

__all__ = ["debug_mode", "disable_debug_mode", "enable_debug_mode"]

from contextlib import contextmanager
from typing import NoReturn


_DEBUG_MODE_ENABLED = False


def _debug_mode_enabled() -> bool:
    """
    Return whether debug mode is currently enabled.

    Returns:
        ``bool``: whether debug mode is enabled
    """
    return _DEBUG_MODE_ENABLED


def enable_debug_mode() -> None:
    """
    Enable PyBryt's debug mode.
    """
    global _DEBUG_MODE_ENABLED
    _DEBUG_MODE_ENABLED = True


def disable_debug_mode() -> None:
    """
    Disable PyBryt's debug mode.
    """
    global _DEBUG_MODE_ENABLED
    _DEBUG_MODE_ENABLED = False


@contextmanager
def debug_mode() -> None:
    """
    A context in which debug mode is enabled.

    When the context exits, debug mode is disabled globally. This means debug mode will be disabled
    even if it was enabled before the context was entered.
    """
    enable_debug_mode()
    yield
    disable_debug_mode()
