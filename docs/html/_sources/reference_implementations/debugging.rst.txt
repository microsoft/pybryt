.. _debugging:

Debugging References
====================

To assist in debugging your reference implementations, PyBryt comes with a debug mode that can be
enabled programmatically. To enable debug mode, use 
:py:func:`pybryt.enable_debug_mode<pybryt.debug.enable_debug_mode>`. To disable debug mode, use
:py:func:`pybryt.disable_debug_mode<pybryt.debug.disable_debug_mode>`. Alternatively, you can 
enable debug mode in a ``with`` block uses the context manager 
:py:obj:`pybryt.debug_mode<pybryt.debug.debug_mode>`.

.. code-block:: python

    pybryt.enable_debug_mode()
    # debug your reference
    pybryt.disable_debug_mode()

    # or...

    with pybryt.debug_mode():
        # debug your reference

In debug mode, PyBryt will raise exceptions instead of ignoring conditions that could cause
unexpected behavior. Currently, conditions that raise exceptions in debug mode are:

* when a custom equivalence function is passed to a :py:class:`Value<pybryt.annotations.value.Value>`
  annotation along with ``atol`` and/or ``rtol``
* when a custom equivalence function raises an exception
