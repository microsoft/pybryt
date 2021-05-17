.. _annotations:

Annotations
===========

.. toctree::
   :maxdepth: 3
   :hidden:

   relational_annotations
   complexity_annotations
   invariants

Annotations are the building blocks out of which reference implementations are constructed. They 
annotations represent a single condition that a student's implementation should meet, and define a 
set of behaviors for responding to the passing or failing of those conditions. Annotations provide
conditions not only for expecting a specific value but also for combining those expectations to form
conditions on the structure of students' code, including the temporal relationship of values and
complex boolean logic surrounding the presence, or lack thereof, of those values.

All annotations are created by instaniating subclasses of the abstract 
:py:class:`Annotation<pybryt.Annotation>` class. There are two main types of annotations: value 
annotations, described below, and :ref:`relational annotations<relational>`.


Values
------

Consider the most basic kind of annotation: expecting a specific value to appear while executing the 
student's code. To create a value annotation, create an instance of :py:class:`Value<pybryt.Value>`. 
The constructor takes in the value that you are expecting to see in the student's code:

.. code-block:: python

   np.random.seed(42)
   arr = np.random.normal(3, 2, size=100)
   pybryt.Value(arr)

Note that when an instance of :py:class:`Value<pybryt.Value>` is created, :py:meth:`copy.copy` is 
called on the argument passed to it, so values don't need to worry about being affected by 
mutability.


Numerical Tolerance
+++++++++++++++++++

For numerical values, or iterables of numerical values that support vectorized math, it is also 
possible to set an absolute tolerance for the acceptance of student values using the ``tol`` 
argument, which defaults to zero.

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
