Student Implementations
=======================

For tracking and managing student implementations, stored in PyBryt as a list of 2-tuples of the 
objects observed while tracing students' code and the timestamps of those objects, PyBryt provides
the :py:class:`StudentImplementation<pybryt.student.StudentImplementation>` class. The constructor for this
class takes in either a path to a Jupyter Notebook file or a notebook object read in with 
``nbformat``.

.. code-block:: python

    stu = pybryt.StudentImplementation("subm.ipynb")

    # or...
    nb = nbformat.read("subm.ipynb")
    stu = pybryt.StudentImplementation(nb)


Notebook Execution
------------------

The constructor reads the notebook file and stores the student's code. It then proceeds to execute
the student's notebook using ``nbformat``'s ``ExecutePreprocessor``. The memory footprint of the
student's code is constructed by executing the notebook with a trace function that tracks every 
value created and accessed **by the student's code** and the timestamps at which those values were
observed. PyBryt also tracks all of the function calls that occur during execution.

To trace into code written in specific files, use the ``addl_filenames`` argument of the constructor 
to pass a list of absolute paths of files to trace inside of. This can be useful for cases in which
a testing harness is being used to test student's code and the student's *actual* submission is 
written in a Python script (which PyBryt would by default not trace).

.. code-block:: python

    stu = pybryt.StudentImplementation("harness.ipynb", addl_filenames=["subm.py"])

To prevent notebooks from getting stuck in a loop or from taking up too many resources, PyBryt
automatically sets a timeout of 1200 seconds for each notebook to execute. This cap can be changed
using the `timeout` argument to the constructor, and can be removed by setting that value to ``None``:

.. code-block:: python

    stu = pybryt.StudentImplementation("subm.ipynb", timeout=2000)

    # no timeout
    stu = pybryt.StudentImplementation("subm.ipynb", timeout=None)

PyBryt also employs various custom notebook preprocessors for handling special cases that occur in 
the code to allow different types of values to be checked. To see the exact version of the code that 
PyBryt executes, set ``output`` to a path to a notebook that PyBryt will write with the executed 
notebook. You can also access this notebook as an ``nbformat.NotebookNode`` object using 
:py:obj:`StudentImplementation.executed_nb<pybryt.student.StudentImplementation.executed_nb>`
This can be useful e.g. for debugging reference implementations by inserting ``print`` 
statements that show the values at various stages of execution.

.. code-block:: python

    stu = pybryt.StudentImplementation("subm.ipynb", output="executed-subm.ipynb")

If there is code in a student notebook that should not be traced by PyBryt, wrap it PyBryt's
:py:class:`no_tracing<pybryt.execution.no_tracing>` context manager. Any code inside this context
will not be traced (if PyBryt is tracing the call stack). If no tracing is occurring, no action is
taken.

.. code-block:: python

    with pybryt.no_tracing():
        foo(1)


Checking Implementations
------------------------

To reconcile a student implementation with a set of reference implementations, use the
:py:meth:`StudentImplementation.check<pybryt.student.StudentImplementation.check>` method, which takes in
a single :py:class:`ReferenceImplementation<pybryt.reference.ReferenceImplementation>` object, or a list of
them, and returns a :py:class:`ReferenceResult<pybryt.reference.ReferenceResult>` object (or a list of them).
This method simply abstracts away managing the memory footprint tracked by the 
:py:class:`StudentImplementation<pybryt.student.StudentImplementation>` object and calls the 
:py:meth:`ReferenceImplementation.run<pybryt.reference.ReferenceImplementation.run>` method for each provided 
reference implementation.

.. code-block:: python

    ref = pybryt.ReferenceImplementation.load("reference.pkl")
    stu = pybryt.StudentImplementation("subm.ipynb")
    stu.check(ref)

To run the references for a single group of annotations, pass the ``group`` argument, which should 
be a string that corresponds to the name of a group of annotations. For example, to run the checks 
for a single question in a reference that contains multiple questions, the pattern might be

.. code-block:: python

    stu.check(ref, group="q1")


Checking from the Notebook
++++++++++++++++++++++++++

For running checks against a reference implementation from inside the notebook, PyBryt also provides
the context manager :py:class:`check<pybryt.student.check>`. This context manager initializes 
PyBryt's tracing function for any code executed inside of the context and generates a memory 
footprint of that code, which can be reconciled against a reference implementation. The context
manager prints a report when it exits to inform students of any messages and the passing or failing 
of each reference.

A general pattern for using this context manager would be to have students encapsulate some logic in
a function and then write test cases that are checked by the reference implementation inside the
context manager. For exmaple, consider the median example below:

.. code-block:: python

    def median(S):
        sorted_S = sorted(S)
        size_of_set = len(S)
        middle = size_of_set // 2
        is_set_size_even = (size_of_set % 2) == 0
        if is_set_size_even:
            return (sorted_S[middle-1] + sorted_S[middle]) / 2
        else:
            return sorted_S[middle]

    with pybryt.check("median.pkl"):
        import numpy as np
        np.random.seed(42)
        for _ in range(10):
            vals = [np.random.randint(-1000, 1000) for _ in range(np.random.randint(1, 1000))]
            val = median(vals)

The ``check`` context manager takes as its arguments a path to a reference implementation, a reference
implementation object, or lists thereof. By default, the report printed out at the end includes the
results of all reference implementations being checked; this can be changed using the ``show_only``
argument, which takes on 3 values: ``{"satisfied", "unsatisfied", None}``. If it is set to 
``"satisfied"``, only the results of satisfied reference will be included (unless there are none and
``fill_empty`` is ``True``), and similarly for ``"unsatisfied"``.


Working with Memory Footprints
------------------------------

Once the notebook has been executed, which happens when the constructor is called, the submission's
memory footprint can be found in the ``footprint`` field of the 
:py:class:`StudentImplementation<pybryt.student.StudentImplementation>` object. This field contains a 
:py:class:`MemoryFootprint<pybryt.execution.memory_footprint.MemoryFootprint>` object, which has 
fields and method for accessing the values in the footprint, the function calls observed by the 
trace function, the set of imported modules, and the processed notebook that was executed by PyBryt. 
See the API reference for
:py:class:`MemoryFootprint<pybryt.execution.memory_footprint.MemoryFootprint>` objects for more information.


Storing Implementations
-----------------------

Because generating the memory footprints of students' code can be time consuming and computationally
expensive, :py:class:`StudentImplementation<pybryt.student.StudentImplementation>` objects can also be 
serialized to make multiple runs across sessions easier. The 
:py:class:`StudentImplementation<pybryt.StudentImplementation>` class provides the 
:py:meth:`dump<pybryt.student.StudentImplementation.dump>` and 
:py:meth:`load<pybryt.student.StudentImplementation.load>` methods, which function the same as with 
:ref:`reference implementations<storing_refs>`.
:py:class:`StudentImplementation<pybryt.student.StudentImplementation>` objects can also be serialized to 
base-64-encoded strings using the :py:meth:`dumps<pybryt.student.StudentImplementation.dumps>` and 
:py:meth:`loads<pybryt.student.StudentImplementation.loads>` methods.
