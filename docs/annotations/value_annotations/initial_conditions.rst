Initial Conditions
==================

For some problems, it is necessary for students to choose some configurations or initial conditions
that can vary from student to student; handling all possible values of these initial conditions
would require writing quite a few references. Instead, PyBryt offers the
:py:class:`InitialCondition<pybryt.annotations.initial_condition.InitialCondition>` class to
represent a value that will be set when the student's submission is executed for use in writing
annotations.


Writing a Reference with Initial Conditions
-------------------------------------------

Using initial conditions in your references is pretty simple. Each
:py:class:`InitialCondition<pybryt.annotations.initial_condition.InitialCondition>` has a name,
the first argument to its constructor. This name is how the value in the student submission will be
identified (but more on that later).

Once you've instantiated an
:py:class:`InitialCondition<pybryt.annotations.initial_condition.InitialCondition>`, you can use it
as normal in value and other types of annotations (except attribute annotations).

.. code-block:: python

    ic = pybryt.InitialCondition("foo")
    pybryt.Value(ic)

Sometimes, however, you may want to look for a value derived from an initial condition. For this
reason, :py:class:`InitialCondition<pybryt.annotations.initial_condition.InitialCondition>`
supports all of Python's arithmetic operators, and you can also apply transformations by writing
functions:

.. code-block:: python

    pybryt.Value(ic + 2)
    pybryt.Value(2 * ic - 3)

    pybryt.Value(ic.apply(np.transpose).apply(np.linalg.norm))
    pybryt.Value(ic.apply(lambda v: pow(v, 10, 73)))

Each statement inside the :py:class:`Value<pybryt.annotations.value.Value>` constructors above
returns an :py:class:`InitialCondition<pybryt.annotations.initial_condition.InitialCondition>`.
Initial conditions maintain a list of transformations that need to be applied to reach the final
value for the annotation, and when a value is supplied from the submission, the transformations
are applied in sequence to determine the value that the value annotations should look for.


Collecting Initial Conditions in Submissions
--------------------------------------------

In order to link the initial conditions in the reference implementation to the values in the
submission, you must call
:py:func:`pybryt.set_initial_conditions<pybryt.execution.set_initial_conditions>` in the
submission. This function accepts a dictionary as its only argument mapping strings corresponding
to the names of initial conditions to the values of those initial conditions. When PyBryt is not
actively tracing, it has no effect; but, when called while PyBryt executes the submission, it tells
PyBryt to store the initial conditions passed to it in the memory footprint for later use by the
annotations.

For example, continuing the example from above, you would need to call

.. code-block:: python

    pybryt.set_initial_conditions({
        "foo": 2,
    })

to set the initial condition.

This function can be called multiple times, but the memory footprint only retains a single store of
initial conditions, so calling it multiple times with the same key will overwrite any old values
of that key. (For example, calling it with ``{"foo": 1, "bar": 3}`` and then ``{"foo": 2}``
will result in initial conditions ``{"foo": 2, "bar": 3}``).
