.. _value:

Value Annotations
=================

.. toctree::
    :maxdepth: 3
    :hidden:

    initial_conditions
    structural_patterns
    invariants

Value annotations are the most basic type of annotation. They expect a specific
value to appear while executing the student's code. To create a value
annotation, create an instance of :py:class:`Value<pybryt.annotations.value.Value>` and pass to
its constructor the value expected in the student's code:

.. code-block:: python

    arr = np.linspace(0, 10, 11)
    pybryt.Value(arr)

Note that when an instance of :py:class:`Value<pybryt.annotations.value.Value>` is created,
:py:meth:`copy.copy` is called on the argument passed to it, so values cannot be
affected by mutability.


Attribute Annotations
---------------------

PyBryt supports checking for the presence of an object with a specific attribute value using the
:py:class:`Attribute<pybryt.annotations.value.Attribute>` annotation. This annotation takes in an 
object and one or more strings representing an instance variable, and asserts that the student's 
memory footprint should contain an object with that attribute such that the value of the attribute 
equals the value of the  attribute in the annotation.

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


Return Value Annotations
------------------------

In addition to checking for the presence of a value, PyBryt also has an annotation that asserts that
a value was returned by a student's function. The annotation does not specify anything about the
function that returns it except that the function is part of the submission code (i.e. not part of
an imported library); it merely checks that the value was seen at least once in a return event
passed to the trace function.

You can create a return value annotation with the
:py:class:`ReturnValue<pybryt.annotations.value.ReturnValue>` constructor; it accepts all the same
arguments as the :py:class:`Value<pybryt.annotations.value.Value>` constructor:

.. code-block:: python

    pybryt.ReturnValue(df, success_message="...", failure_message="...")


Numerical Tolerances
---------------------

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
---------------------

Similar to numerical tolerances, which allow the student's solution to deviate
from the reference value, PyBryt allows specifying conditions when other data
types should be considered equal. PyBryt supports defining these conditions
using :ref:`invariants<invariants>`. To use invariants on a value, we need to
pass the invariant objects as a list to the ``invariants`` argument of the
:py:class:`Value<pybryt.Value>` constructor. For instance, let's say we want to
allow the student's solution (a string) to be case-insensitive.

.. code-block:: python

    correct_answer = "a CasE-inSensiTiVe stRING"
    pybryt.Value(correct_answer, invariants=[pybryt.invariants.string_capitalization])

More information about invariants can be found :ref:`here<invariants>`.


Custom Equivalence Functions
----------------------------

In some cases, the algorithm that value annotations use for checking if two objects are
equivalent may not be suitable to the problem at hand. For cases like this, you can provide a 
custom equivalence function that the value annotation will use instead to determine if two
objects are equal. The equivalence function should return ``True`` if the objects are equal and
``False`` otherwise. If the equivalence function raises an error, this will be interpeted as 
``False`` (unless :ref:`debug mode<debugging>` is enabled).

For example, we could implement the ``string_capitalization`` invariant using a custom
equivalence function:

.. code-block:: python

    def string_lower_eq(s1, s2):
        return s1.lower() == s2.lower()

    pybryt.Value(correct_answer, equivalence_fn=string_lower_eq)
