.. _complexity:

Complexity Annotations
======================

Complexity annotations define an expectation of the complexity of a block of student code. Currently,
PyBryt supports one kind of complexity annotation: time complexity. All complexity annotations are
subclasses of the abstract 
:py:class:`ComplexityAnnotation<pybryt.annotations.complexty.ComplexityAnnotation>` class, which
defines some helpful defaults for working with these annotations.


Creating Complexity Annotations
-------------------------------

Complexity annotations can be created just like value annotations: by calling their constructor. The
constructor takes one positional argument which corresponds to a class asserting the expected 
complexity of the code. These complexity classes can be found in the 
:py:mod:`pybryt.complexities<pybryt.annotations.complexity.complexities>` module. All complexity
classes are subclasses of the abstract base class 
:py:class:`pybryt.complexities.complexity<pybryt.annotations.complexity.complexities.complexity>`.

The constructor also takes one required keyword argument, ``name``. This should be set to a string
that corresponds to named time complexity context in the student's code (more on this below). The name
should be unique across all annotations.

For example, to check the time complexity of a block named ``"sort"`` with :math:`\mathcal{O}(n \log n)`:

.. code-block:: python

    import pybryt
    import pybryt.complexities as cplx

    pybryt.TimeComplexity(cplx.linearithmic, name="sort")

A full list of the available complexity classes can be found :ref:`here<complexities>`.


Custom Complexity Classes
+++++++++++++++++++++++++

If a complexity not provided in PyBryt's defaults is needed, this can be created by subclassing
:py:class:`pybryt.complexities.complexity<pybryt.annotations.complexity.complexities.complexity>`.
This abstract base class requires the ``transform_n`` static method to be implemented, which should 
transform the array of input lengths, passed as an ``numpy.ndarray`` so that the least-squares solver
can be used to determine if the data matches this complexity. Optionally, you can also override the
``transform_t`` static method, which transforms the array of timings. The default implementation of this
function is the identity function.

.. code-block:: python

    import numpy as np
    import pybryt.complexities as cplx

    class loglog(cplx.complexity):

        @staticmethod
        def transform_n(n: np.ndarray) -> np.ndarray:
            return np.vstack((np.ones(len(n)), np.log2(np.log2(n)))).T

To use these custom complexity classes, they can either be passed as the first argument to the
``TimeComplexity`` constructor, if they are the desired complexity, or passed in a list to the
``addl_complexities`` argument if they should be considered but are not correct.

.. code-block:: python

    # my_cplx is a package with custom complexities
    pybryt.TimeComplexity(my_cplx.quartic, name="foo", addl_complexities=[my_cplx.factorial])


Tracking Code Complexity
------------------------

To track the time complexity of students' code, PyBryt provides the 
:py:obj:`check_time_complexity<pybryt.execution.check_time_complexity>` context manager. This
context manager takes two arguments, the name of the block (which should match the ``name`` of a
time complexity annotation in the reference implementation) and length of the input (or, for simplicity,
the input itself if it has a ``__len__`` method).

The context manager uses PyBryt's tracing function to determine the runtime of the student's code by
counting the number of steps taken while the code executes (the number of times the trace function is
called). It then adds an object that tracks this information to the student's memory footprint when
the block exits.

An important note: any code placed inside this context manager will **not** have its objects in-memory
traced. PyBryt's trace function will only be used to track the number of steps taken during execution,
but no values will be added to the student's memory footprint. This means that any code needed to
satisfy value annotations, relational annotations, etc. must be placed outside this context manager.
This is also the case during reference construction: any annotations created by code inside this
context manager will not be automatically tracked and added to a reference implementation. If this
behavior is desired, it must be accomplished manually.

For example, to satisfy the time complexity annotation above, the code block below checks the time
complexity of a student-implemented ``sort`` function on a series of inputs of increasing sizes.

.. code-block:: python

    import numpy as np
    for exp in np.arange(8):
        n = np.random.uniform(size=10**exp)
        with pybryt.check_time_complexity("sort", n):
            sort(n)


Evaluating Code Complexity
--------------------------

When evaluating whether a time complexity annotation has been satisfied, PyBryt uses the method of
the |big_O|_ Python package. The annotation is evaluated by
collecting all of the time complexity result objects found in the student's memory footprint that
match the ``name`` of the annotation. 

The data from these results is collected and sent through
each complexity class, which uses ``np.linalg.lstsq`` to fit the input length data to
the time data (incorporating the transformations needed for each complexity) and returns the 
residuals of this fit. The complexity with the smallest residuals (incorporating a slight preference 
for simpler complexities) is determined to be the best match, and is used to determine whether or not 
the annotation was satisfied.

.. |big_O| replace:: ``big_O``
.. _big_O: https://github.com/pberkes/big_O
