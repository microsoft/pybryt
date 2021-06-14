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


Annotation Arguments
--------------------

All annotations contain some core configurations that can be set using keyword arguments in the
constructor or by accessing the instance variables of that object. The table below lists these 
arguments.

.. list-table::
    :widths: 10 10 10 70

    * - Field Name
      - Keyword Argument
      - Type
      - Description
    * - ``name``
      - ``name``
      - ``str``
      - The name of the annotation; used to process ``limit``; automatically set if unspecified
    * - ``limit``
      - ``limit``
      - ``str``
      - The maximum number of annotations with a given ``name`` to track
    * - ``group``
      - ``group``
      - ``str``
      - The name of a group to which this annotation belongs; for running specific groups of annotations
        from a reference implementation
    * - ``success_message``
      - ``success_message``
      - ``str``
      - A message to be displayed to the student if the annotation is satisfied
    * - ``failure_message``
      - ``failure_message``
      - ``str``
      - A message to be displayed to the student if the annotation is *not* satisfied


Value Annotations
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

More information about invariants can be found :ref:`here<invariants>`.


Attribute Annotations
---------------------

PyBryt supports checking for the presence of an object with a specific attribute value using the
:py:class:`Attribute<pybryt.Attribute>` annotation. This annotation takes in an object and one or more
strings representing an instance variable, and asserts that the student's memory footprint should 
contain an object with that attribute such that the value of the attribute equals the value of the 
attribute in the annotation.

For example, this can be useful in checking that students have correctly fitted in ``sklearn``
regression model by checking that the coefficients are correct:

.. code-block:: python

    import sklearn.linear_model as lm

    model = lm.LinearRegression()
    model.fit(X, y)

    pybryt.Attribute(model, "coef_",
        failure_message="Your model doesn't have the correct coefficients.")

Note that, by default, PyBryt doesn't check that the object satisfying the attribute annotation has
the same type as the object the annotation was created for. If a student knew the coefficient values
in the above example, the following student code would satisfy that annotation:

.. code-block:: python

    class Foo:

        coef_ = ...  # the array of coefficients
    
    f = Foo()  # f will satisfy the annotation

To ensure that the annotation is only satisfied when the object is of the same type, set 
``enforce_type=True`` in the constructor:

.. code-block:: python

    pybryt.Attribute(model, "coef_", enforce_type=True,
        failure_message="Your model doesn't have the correct coefficients.")
