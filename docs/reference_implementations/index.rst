Reference Implementations
=========================

.. toctree::
    :maxdepth: 3
    :hidden:

    debugging

The functional unit of PyBryt is a reference implementation. A **reference implenetation** is a set 
of conditions expected of students' code that determine whether a student has correctly implemented
some program. They are constructed by creating a series of :ref:`annotations<annotations>` that are
tracked in a :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` object.


Creating Reference Implementations
----------------------------------

Reference implemenations can be created by compiling Jupyter Notebooks that have been marked-up
with annotations. To compile a reference implementation, use 
:py:meth:`ReferenceImplementation.compile<pybryt.ReferenceImplementation.compile>`, which takes in
the path to a notebook file:

.. code-block:: python

    pybryt.ReferenceImplementation.compile("reference.ipynb")

There are two ways to mark-up a notebook: by creating annotations and having PyBryt track them 
automatically (for a single reference), or by tracking annotations in a list (for creating multiple
reference implementations from a single notebook).

When compiling a notebook, PyBryt executes all of the code in the notebook and searches the 
resulting global environment for instances of the 
:py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` class. If it finds them, it 
collects them into a list and returns the list of reference implementations (or a single reference
implementation if only one is found). If it doesn't find any reference implementations, it takes all
of the annotations :ref:`tracked by<tracked_annotations>` PyBryt and turns those into a single
reference implementation.


Automatic Reference Creation
++++++++++++++++++++++++++++

To create a single reference implementation from a notebook, create
:py:class:`Annotation<pybryt.Annotation>` instances (assigning them to variables is not necessary).
After annotating the notebook, when PyBryt compiles the notebook, it will find all of the 
annotations.

.. _tracked_annotations:

PyBryt finds the annotations because the ``__init__`` method automatically adds the instances 
created to a singleton list that PyBryt maintains, so assigning them to variables or tracking them 
further is unnecessary unless more advanced reference implementations are being built. This means 
that when marking up code, as below, creating new variables is unnecessary unless further conditions
are to be made later down the line.

.. code-block:: python

    fibs = np.zeros(n, dtype=int)

    fibs[0] = 0
    curr_val = pybryt.Value(fibs)
    if n == 1:
        return fibs

    fibs[1] = 1
    v = pybryt.Value(fibs)
    curr_val.before(v)         # not assigned to a variable, but still tracked
    curr_val = v
    if n == 2:
        return fibs

    for i in range(2, n-1):
        fibs[i] = fibs[i-1] + fibs[i-2]
        
        v = pybryt.Value(fibs)
        curr_val.before(v)     # not assigned to a variable, but still tracked
        curr_val = v


Manual Reference Creation
+++++++++++++++++++++++++

To create multiple reference implementations from a single notebook, begin by creating 
:py:class:`Annotation<pybryt.Annotation>` instances and grouping them into lists. These lists will 
be passed to the :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` constructor
to create the reference implementations. *These objects must be assigned to global variables, or 
PyBryt will not find them.* Note that the constructor takes an additional positional argument which
corresponds to the name of the reference implementation.

As an example, consider the code below, which creates two reference implementations for a Fibonacci
sequence generator:

.. code-block:: python

    n_fibs = 50
    first_ref = []
    second_ref =  []


    # first implementation: dynamic programming
    fibs = np.zeros(n_fibs, dtype=int)

    fibs[0] = 0
    first_ref.append(pybryt.Value(fibs))
    if n_fibs == 1:
        return fibs

    fibs[1] = 1
    v = pybryt.Value(fibs)
    first_ref.append(curr_val.before(v))
    curr_val = v
    if n_fibs == 2:
        return fibs

    for i in range(2, n_fibs-1):
        fibs[i] = fibs[i-1] + fibs[i-2]
        
        v = pybryt.Value(fibs)
        first_ref.append(curr_val.before(v))
        curr_val = v

    final_answer = fibs[-1]


    # second implementation: hash map
    fib_map = {}
    def fib(n):
        if n == 0:
            return 0
        
        if n == 1:
            return 1
        
        if n in fib_map:
            return fib_map[n]
        
        ans = fib(n-1) + fib(n-2)
        fib_map[n] = ans
        second_ref.append(pybryt.Value(fib_map))
        
        return ans

    final_answer = fib(n_fibs)


    # create references
    ref1 = pybryt.ReferenceImplementation("ref1", first_ref)
    ref2 = pybryt.ReferenceImplementation("ref2", second_ref)


Interacting with Reference Implementations
------------------------------------------

The :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` class defines an API for 
working with reference implementations. The core method for reconciling a student implementation,
encoded as a list of 2-tuples, is 
:py:meth:`ReferenceImplementation.run<pybryt.ReferenceImplementation.run>`. This method is 
abstracted away by the :py:meth:`StudentImplementation.check<pybryt.StudentImplementation.check>`
method, which calls it for that student implementation.


.. _storing_refs:

Storing Reference Implementations
---------------------------------

Reference implementation objects can be saved to a file by calling 
:py:meth:`ReferenceImplementation.dump<pybryt.ReferenceImplementation.dump>`, which takes in the 
path to the file and uses the ``dill`` library to serialize the object. To load a reference 
implementation, or a list of reference implementations, from a file, use the static method
:py:meth:`ReferenceImplementation.load<pybryt.ReferenceImplementation.load>`.

.. code-block:: python

    ref = pybryt.ReferenceImplementation("foo", [...])
    ref.dump() # defaults to filename '{ref.name}.pkl'
    ref = pybryt.ReferenceImplementation.load('foo.pkl')
