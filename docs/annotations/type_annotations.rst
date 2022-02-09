.. _type:

Type Annotations
================

Type annotations are somewhat similar to value annotations, although they operate on types
insted of individual values or objects. They can be used to check the presence, or lack thereof, of
objects of a specific type in a memory footprint, or conditions on that presence.


Forbid Type
-----------

The :py:class:`ForbidType<pybryt.annotations.type_.ForbidType>` annotation asserts that a student's
memory footprint has no values of a specific type in it. For example, if students should be implementing
an algorithm without vectorization, it is possible to create an annotation forbidding the use of
arrays:

.. code-block:: python

    import numpy as np

    pybryt.ForbidType(np.ndarray, failure_message="Arrays are not allowed!")

Checking for values is performed using Python's built-in ``isinstance`` function. Types passed to 
the constructor must be pickleable with the ``dill`` library.
