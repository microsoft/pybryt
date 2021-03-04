Student Implementations
=======================

For tracking and managing student implementations, stored in PyBryt as a list of 2-tuples of the 
objects observed while tracing students' code and the timestamps of those objects, PyBryt provides
the :py:class:`StudentImplementation<pybryt.StudentImplementation>` class. The constructor for this
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
observed. 

To trace into code written in specific files, use the ``addl_filenames`` argument of the constructor 
to pass a list of absolute paths of files to trace inside of. This can be useful for cases in which
a testing harness is being used to test student's code and the student's *actual* submission is 
written in a Python script (which PyBryt would by default not trace).

.. code-block:: python

    stu = pybryt.StudentImplementation("harness.ipynb", addl_filenames=["subm.py"])

PyBryt also employs various custom notebook preprocessors for handling special cases that occur in 
the code to allow different types of values to be checked. To see the exact version of the code that 
PyBryt executes, set ``output`` to a path to a notebook that PyBryt will write with the executed 
notebook. This can be useful e.g. for debugging reference implementations by inserting ``print`` 
statements that show the values at various stages of execution.

.. code-block:: python

    stu = pybryt.StudentImplementation("subm.ipynb", output="executed-subm.ipynb")


Checking Implementations
------------------------

To reconcile a student implementation with a set of reference implementations, use the
:py:meth:`StudentImplementation.check<pybryt.StudentImplementation.check>` method, which takes in
a single :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` object, or a list of
them, and returns a :py:class:`ReferenceResult<pybryt.ReferenceResult>` object (or a list of them).
This method simply abstracts away managing the memory footprint tracked by the 
:py:class:`StudentImplementation<pybryt.StudentImplementation>` object and calls the 
:py:meth:`ReferenceImplementation.run<pybryt.ReferenceImplementation.run>` method for each provided 
reference implementation.

.. code-block:: python

    ref = pybryt.ReferenceImplementation.load("reference.ipynb")
    stu = pybryt.StudentImplementation("subm.ipynb")
    stu.check(ref)

To run the references for a single group of annotations, pass the ``group`` argument, which should 
be a string that corresponds to the name of a group of annotations. For example, to run the checks 
for a single question in a reference that contains multiple questions, the pattern might be

.. code-block:: python

    stu.check(ref, group="q1")


Storing Implementations
-----------------------

Because generating the memory footprints of students' code can be time consuming and computationally
expensive, :py:class:`StudentImplementation<pybryt.StudentImplementation>` objects can also be 
serialized to make multiple runs across sessions easier. The 
:py:class:`StudentImplementation<pybryt.StudentImplementation>` class provides the 
:py:class:`dump<pybryt.StudentImplementation.dump>` and 
:py:class:`load<pybryt.StudentImplementation.load>` methods, which function the same as with 
:ref:`reference implementations<storing_refs>`.
:py:class:`StudentImplementation<pybryt.StudentImplementation>` objects can also be serialized to 
base-64-encoded strings using the :py:class:`dumps<pybryt.StudentImplementation.dumps>` and 
:py:class:`loads<pybryt.StudentImplementation.loads>` methods.
