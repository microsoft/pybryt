"""Tests for debug mode"""

from pybryt import debug_mode, disable_debug_mode, enable_debug_mode
from pybryt.debug import _debug_mode_enabled


def test_debug_mode():
    """
    Test that the debug mode controllers correctly enable and disable debug mode.
    """
    enable_debug_mode()
    assert _debug_mode_enabled()
    disable_debug_mode()
    assert not _debug_mode_enabled()

    with debug_mode():
        assert _debug_mode_enabled()
    assert not _debug_mode_enabled()

    enable_debug_mode()
    with debug_mode():
        assert _debug_mode_enabled()
    assert not _debug_mode_enabled()
