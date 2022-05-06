CLI Reference
=============

PyBryt includes a small command-line interface for performing quick tasks using its functionality.
The main tasks that the CLI currently supports are:

- compiling reference implementations and saving them to a file
- executing student implementations and saving them to a file
- checking reference implementations against student implementations (as notebooks or pickled objects)
  and saving/echoing the results

Each of the commands is detailed in the :ref:`refererence<cli_reference>` below, but a short summary
of each is provided here. The CLI can be invoked via the command ``pybryt`` or by calling PyBryt as a 
Python module: ``python3 -m pybryt``. For simplicity, the convention of the former is used here.


CLI Sub-commands
----------------


``check``
+++++++++

``pybryt check`` is used to check a student implementation against a reference implementation. It
takes two position arguments corresponding to the path to a reference implementation and the path to
a student implementation. Both paths can lead either to notebooks (which will be executed/compiled
if provided) or to pickle files.

The output of this command comes in three forms:

- a pickled :py:class:`ReferenceResult<pybryt.reference.ReferenceResult>` object, written to a file
- a JSON file with a text-based representation of the ``ReferenceResult`` object
- a report echoed to the console

To set the output type, use the ``-t`` flag. If a file is written, use the ``-o`` flag to set the 
output path (defaults to ``{stu.stem}_results.[pkl|json]``).

.. code-block:: console

    $ ls
    reference.ipynb         subm.ipynb
    $ pybryt check reference.ipynb subm.ipynb
    $ ls
    reference.ipynb         subm.ipynb              subm_results.pkl
    $ pybryt check reference.pkl subm.pkl -t json
    $ ls
    reference.ipynb         subm.ipynb              subm_results.json       subm_results.pkl
    $ pybryt check reference.ipynb subm.pkl -t report
    REFERENCE: median
    SATISFIED: True
    MESSAGES:
    ...


``compile``
+++++++++++

``pybryt compile`` is used to compile a reference implementation to a file. It takes a single positional
argument, the path to the notebook to be compiled. To set the destination path, use the ``-d`` flag.
If a name is needed for the reference implementation, it can be provided with the ``-n`` flag.

.. code-block:: console

    $ pybryt compile reference.ipynb
    $ pybryt compile reference.ipynb -d ref.pkl -n foo


``execute``
+++++++++++

``pybryte execute`` is used to execute one or more student implementations and write the memory 
footprints to files for futher processing. All paths passed as position arguments to this command
are paths to student implementation notebooks.

Because execution can be time-consuming, ``pybryt execute`` supports parallelism using Python's
``multiprocessing`` library. To enable parallelism, use the ``-p`` flag.

.. code-block:: console

    $ pybryt execute submissions/*.ipynb
    $ pybryt execute submissions/*.ipynb -p


.. _cli_reference:

Reference
---------

This section is a short reference for all of the commands and options for PyBryt's CLI.

.. click:: pybryt.cli:click_cli
    :prog: pybryt
    :nested: full
