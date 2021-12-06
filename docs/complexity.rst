Complexity Analysis
===================

PyBryt exposes its code complexity analysis tools so that they can be used to analyze blocks of code
without necessitating the use of the annotation framework. These tools can be used to give students
a way to test the complexity of their implementations, or just to analyze code complexity in a manner
that is more reliable than using a timer.

These tools use PyBryt's internal tracing mechanisms, meaning that the data used to determine the
complexity is based on a step counter rather than the system clock, making it deterministic and more
accurate for analyzing the runtime of solutions.

To make use of these analysis tools, use the 
:py:class:`TimeComplexityChecker<pybryt.complexity.TimeComplexityChecker>` class. This class, once
instantiated, can be used as a context manager to track the runtime data for a block of code given
an input length. The context manager functions similarly to :ref:`PyBryt's context manager for 
complexity annotations<complexity_annotation_cm>` in that you provide it with the input length (or
the input itself if it supports ``len``) and use it multiple times to gather observations for each
input length.

Once the data has been gathered, use the
:py:meth:`TimeComplexityChecker.determine_complexity<pybryt.complexity.TimeComplexityChecker.determine_complexity>`
method to determine the complexity class. This uses PyBryt's complexity analysis framework to find
the complexity and returns the corresponding complexity class from 
:py:mod:`pybryt.complexities<pybryt.annotations.complexity.complexities>`. For more information on
how the complexity class is determined, see :ref:`complexity`.

.. code-block:: python

    checker = pybryt.TimeComplexityChecker()
    for exp in range(8):
        n = 10 ** exp
        with checker(n):
            some_function(n)

    checker.determine_complexity()

Note that, unlike :py:class:`check_time_complexity<pybryt.execution.complexity.check_time_complexity>`,
you must use the same instance of the class for each entry into the context so that the observations
can be gathered together.


Working with Annotations
------------------------

The :py:class:`TimeComplexityChecker<pybryt.complexity.TimeComplexityChecker>` uses 
:py:class:`check_time_complexity<pybryt.execution.complexity.check_time_complexity>` under the hood,
so it is also compatible with PyBryt's annotation framework. To use a checker that will also track
results for satisfying annotations, pass the name of the annotation to the constructor, just like
with :py:class:`check_time_complexity<pybryt.execution.complexity.check_time_complexity>`:

.. code-block:: python

    checker = pybryt.TimeComplexityChecker("fib_runtime")
    for exp in range(30):
        with checker(n):
            fib(n)

This is a good alternative to :py:class:`check_time_complexity<pybryt.execution.complexity.check_time_complexity>`
when you want students to be able to check the complexity of their code easily, without
having to run PyBryt on the submission each time.
