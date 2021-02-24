Annotations
===========

Annotations are the building blocks out of which reference implementations are constructed. They 
annotations represent a single condition that a student's implementation should meet, and define a 
set of behaviors for responding to the passing or failing of those conditions. Annotations provide
conditions not only for expecting a specific value but also for combining those expectations to form
conditions on the structure of students' code, including the temporal relationship of values and
complex boolean logic surrounding the presence, or lack thereof, of those values.


Values
------

All annotations are created by instaniating subclasses of the abstract :py:class:`pybryt.Annotation`
class. Consider the most basic kind of annotation: expecting a specific value to appear while
executing the student's code. To create a value annotation, create an instance of 
:py:class:`pybryt.Value`. The constructor takes in the value that you are expecting to see in the 
student's code:

.. code-block:: python

   np.random.seed(42)
   arr = np.random.normal(3, 2, size=100)
   pybryt.Value(arr)

Note that when an instance of :py:class:`pybryt.Value` is created, :py:meth:`copy.copy` is called on
the argument passed to it, so values don't need to worry about being affected by mutability.


Numerical Tolerance
+++++++++++++++++++

For numerical values, or iterables of numerical values that support vectorized math, it is also 
possible to set an absolute tolerance for the acceptance of student values using the ``tol`` argument,
which defaults to zero.

.. code-block:: python

   pybryt.Value(arr, tol=1e-4)


Invariants
++++++++++

PyBryt supports :ref:`invariants<invariants>`, which are conditions that allow for objects with 
different structures to be considered "equal" from PyBryt's perspective. To use invariants on a 
value, pass the invariant objects in a list to the ``invariants`` argument of the constructor:

.. code-block:: python

   correct_answer = "a CasE-inSensiTiVe stRING"
   pybryt.Value(correct_answer, invariants=[pybryt.invariants.string_capitalization])


Relational Annotations
----------------------

Relational annotations define some kind of relationship between two or more annotations. Currently,
PyBryt supports two kinds of relational annotations: temporal annotations and boolean annotations. 
All relational annotations are subclasses of the abstract 
:py:class:`pybryt.BeforeAnnotation<pybryt.annotations.relation.BeforeAnnotation>` class, which 
defines some helpful defaults for working with annotations that have child annotations.

Temporal Annotations
++++++++++++++++++++

Temporal annotations describe *when* variables should appear in students' code relative to one 
another. For example, consider the problem of a dynamic programming algorithm to compute the 
Fibonacci sequence: the array containing :math:`n-1` first Fibonacci numbers should appear in memory 
before the array containing the :math:`n` first Fibonacci numbers. 

To enforce such a constraint, the :py:class:`pybryt.Annotation` class defines a ``before`` method 
that asserts that one annotation occurs before another:

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
   curr_val.before(v)
   curr_val = v
   if n == 2:
       return fibs
   
   for i in range(2, n-1):
       fibs[i] = fibs[i-1] + fibs[i-2]
       
       v = pybryt.Value(fibs) # array of first n Fibonacci numbrs
       curr_val.before(v)     # check that first n-1 Fib numbers come before first n
       curr_val = v           # update curr_val for next iteration
   
   return fibs

In the example above, updating a pointer ``curr_val`` in the loop allows us to create a ``before`` 
condition such that we ensure the student followed the correct dynamic programming algorithm by 
checking each update to the ``fibs`` array.

Temporal annotations are satisfied when the student's code satisfies all of the child 
:py:class:`pybryt.Value` annotations and when the first annotation (the one calling 
:py:meth:`pybryt.Annotation.before`) has a timestamp greater than or equal to the timestamp of the 
second annotation.

Note that :py:meth:`pybryt.Annotation.before` returns an instance of the 
:py:class:`pybryt.BeforeAnnotation<pybryt.annotations.relation.BeforeAnnotation>` class, which is 
itself a subclass of :py:class:`pybryt.Annotation` and supports all of the same operations. 
:py:class:`pybryt.Annotation` also provides :py:meth:`pybryt.Annotation.after`, which also returns 
and instance of the 
:py:class:`pybryt.BeforeAnnotation<pybryt.annotations.relation.BeforeAnnotation>` class, but with 
the operands switched.


Boolean Annotations
+++++++++++++++++++

Boolean annotations define conditions on the presence of different values. For example, in defining
a solutions, students may be able to take two different paths, and this logic can be enforced 
using a :py:class:`pybryt.XorAnnotation<pybryt.annotations.relation.XorAnnotation>` to ensure that
only one of the two possible values is present.

Relational annotations can be created either by instantiating the classes directly using the 
constructor or, as is more recommended, by using Python's bitwise logical operators, ``&``, ``|``, 
``^``, and ``~``, on annotations. The dunder methods for these operators have been overrided with 
for the :py:class:`pybryt.Annotation` class, and return the 
:py:class:`pybryt.RelationalAnnotation<pybryt.annotations.relation.RelationalAnnotation>` subclass
instance corresponding to the logical operator used.

To create the xor example above from two values ``v1`` and ``v2``, simply write

.. code-block:: python

   v1 ^ v2

To assert that a student should *not* have a specific value ``v`` in their code, use

.. code-block:: python

   ~v
