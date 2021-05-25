.. _relational:

Relational Annotations
======================

Relational annotations define some kind of relationship between two or more
annotations. Currently, PyBryt supports two types of relational annotations:

* temporal annotations and
* boolean annotations. 

All relational annotations are subclasses of the abstract
:py:class:`RelationalAnnotation<pybryt.annotations.relation.RelationalAnnotation>`
class, which defines some helpful defaults for working with annotations that
have child annotations.

Temporal Annotations
--------------------

Temporal annotations describe *when* variables should appear in student's code
relative to one another. For example, let us consider the problem of a dynamic
programming algorithm to compute the Fibonacci sequence: the array containing
:math:`n-1` first Fibonacci numbers should appear in memory before the array
with :math:`n` first Fibonacci numbers. To enforce such a constraint, the
:py:class:`Annotation<pybryt.Annotation>` class defines a ``before`` method that
asserts that one annotation occurs before another:

.. code-block:: python

    def fib(n):
        """
        Compute and return an array of the first n Fibonacci numbers using dynamic programming.

        Args:
        n (``int``): the number of Fibonacci numbers to return

        Returns:
        ``np.ndarray``: the first ``n`` Fibonacci numbers

        """
        fibs = np.zeros(n, dtype=int)

        fibs[0] = 0
        curr_val = pybryt.Value(fibs)
        if n == 1:
            return fibs

        fibs[1] = 1
        v = pybryt.Value(fibs)
        curr_val.before(v)  # we expect curr_val to appear in memory before v
        curr_val = v
        if n == 2:
            return fibs

        for i in range(2, n-1):
            fibs[i] = fibs[i-1] + fibs[i-2]

            v = pybryt.Value(fibs) # array of first n Fibonacci numbers
            curr_val.before(v)     # check that first n-1 appear before first n Fibonacci numbers
            curr_val = v           # update curr_val for next iteration

        return fibs

In the example above, updating ``curr_val`` in the loop allows us to create a
``before`` condition to ensure the student followed the correct dynamic
programming algorithm by checking each update to the ``fibs`` array.

Temporal annotations are satisfied when the student's code satisfies all of the
child :py:class:`Value<pybryt.Value>` annotations and when the first annotation
(the one calling :py:meth:`Annotation.before<pybryt.Annotation.before>`) has a
timestamp greater than or equal to the timestamp of the second annotation.

Note that :py:meth:`Annotation.before<pybryt.Annotation.before>` returns an
instance of the
:py:class:`BeforeAnnotation<pybryt.annotations.relation.BeforeAnnotation>`
class, which is itself a subclass of :py:class:`Annotation<pybryt.Annotation>`
and supports all of the same operations.
:py:class:`Annotation<pybryt.Annotation>` also provides
:py:meth:`Annotation.after<pybryt.Annotation.after>`, which also returns an
instance of the
:py:class:`BeforeAnnotation<pybryt.annotations.relation.BeforeAnnotation>`
class, but with the operands switched.

Boolean Annotations
-------------------

Boolean annotations define conditions on the presence of different values. For
example, in solving an exercise, students may be able to take two different
paths, and this logic can be enforced using a
:py:class:`XorAnnotation<pybryt.annotations.relation.XorAnnotation>` to ensure
that only one of the two possible values is present.

Relational annotations can be created either by instantiating the classes
directly using the constructor or, as it is more recommended, by using Python's
bitwise logical operators, ``&``, ``|``, ``^``, and ``~``, on annotations. The
special (dunder) methods for these operators have been overridden in
:py:class:`Annotation<pybryt.Annotation>` class, and return the
:py:class:`RelationalAnnotation<pybryt.annotations.relation.RelationalAnnotation>`
subclass instance corresponding to the logical operator used.

To create the XOR example from two values ``v1`` and ``v2``, we write

.. code-block:: python

   v1 ^ v2

To assert that a student should *not* have a specific value ``v`` in their code,
we use

.. code-block:: python

   ~v
