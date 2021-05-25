.. _annotations:

Annotations
===========

.. toctree::
   :maxdepth: 3
   :hidden:

   relational_annotations
   complexity_annotations
   invariants

Annotations are the basic building blocks, out of which reference
implementations are constructed. The annotations represent a single condition
that a student's implementation should meet, and they define a set of behaviors
for responding to the passing or failing of those conditions. Annotations
provide conditions not only for expecting a specific value but also for
combining those expectations to form conditions on the structure of the
student's code, including the temporal relationship of values and complex
boolean logic surrounding the presence or absence of those values.

All annotations are created by instantiating subclasses of the abstract
:py:class:`Annotation<pybryt.Annotation>` class. There are two main types of
annotations: 
 
* value annotations, described below, and
* :ref:`relational annotations<relational>`.

Value annotations
-----------------

Value annotation is the most basic type of annotation. It expects a specific
value to appear while executing the student's code. To create a value
annotation, we create an instance of :py:class:`Value<pybryt.Value>` and pass to
its constructor the value we expect to see in the student's code:

.. code-block:: python

   arr = np.linspace(0, 10, 11)
   pybryt.Value(arr)

Note that when an instance of :py:class:`Value<pybryt.Value>` is created,
:py:meth:`copy.copy` is called on the argument passed to it, so values cannot be
affected by mutability.

Numerical Tolerances
++++++++++++++++++++

For numerical values, or iterables of numerical values that support vectorized
math, it is also possible to define an absolute tolerance (``atol``) and/or a
relative tolerance (``rtol``) to allow the student's solution to deviate from
the reference. Numerical tolerances are computed as with ``numpy.allcose``,
where the value is "equal enough" if it is within :math:`v \pm (\texttt{atol}
+ \texttt{rtol} \cdot |v|)`, where :math:`v` is the value of the annotation.
Both ``atol`` and ``rtol`` default to zero and have to be specified when value
annotation is defined:

.. code-block:: python

   pybryt.Value(arr, atol=1e-3, rtol=1e-5)

Invariants
++++++++++

Similar to numerical tolerances, which allow the student's solution to deviate
from the reference value, PyBryt allows specifying conditions when other data
types should be considered equal. PyBryt supports defining these conditions
using :ref:`invariants<invariants>`. To use invariants on a value, we need to
pass the invariant objects as a list to the ``invariants`` argument of the
:py:class:`Value<pybryt.Value>` constructor. For instance, let us say we want to
allow the student's solution (string) to be case-insensitive.

.. code-block:: python

   correct_answer = "a CasE-inSensiTiVe stRING"
   pybryt.Value(correct_answer, invariants=[pybryt.invariants.string_capitalization])
