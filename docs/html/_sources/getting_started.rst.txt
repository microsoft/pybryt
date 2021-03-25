Getting Started
===============

Installing pybryt
-----------------

You can install pybyrt inside a Python Virtual Environment, a Conda environment, or within a Jupyter Notebook.

Installing inside an existing Jupyter Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add a magic-line command to a Jupyter notebook to install the requirements for a pip environment:

.. code-block:: python

    %pip install pybryt

    import pybryt

Or, for a conda environment:

.. code-block:: python

    %pip install pybryt

    import pybryt

Installing on Windows PowerShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before installing, make sure you have a recent version of `Python 3 installed <https://python.org/downloads>`_.

Next, create a virtual environment, update pip and then install ``pybryt``:

.. code-block:: console

    py -3 -m venv .venv
    .\venv\scripts\activate.ps1
    pip install -U pip
    pip install pybryt

Installing on macOS or Linux command-line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before installing, make sure you have a recent version of `Python 3 installed <https://python.org/downloads>`_.

Next, create a virtual environment, update pip and then install ``pybryt``:

.. code-block:: console

    python3.8 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install pybryt

Annotating a working example
----------------------------

The first step after installing pybryt would be to create a working example for pybryt to model from.

pybryt works by observing working reference implementations and looking for annotated types and variables in any implementation.

Take this example, you want students to complete a simple task of counting the number of words in a piece of text.

You send them the signature of the function to be completed inside a Jupyter notebook:

.. code-block:: python

    def count_words(text: str) -> int:
        """
        Given the input string, ``text``, return the number
        of complete words.
        """
        pass

You could write this function by splitting the string using the builtin ``str.split()`` method, which will automatically 
remove empty strings, and then to count the number of items in the result:

.. code-block:: python

    def count_words(text: str) -> int:
        """
        Given the input string, ``text``, return the number
        of complete words.
        """
        # Split the text by spaces
        fragments = text.split()

        # Count the number of items in the result
        length = len(fragments)
        return length

To annotate the example and train pybryt on what values to look for, you next use the ``pybryt.Value`` class from the :ref:`api`
to annotate the example. ``pybryt.Value`` takes any Python value as the required input for its constructor.

The two key variables to observe in the reference implementation were:

 * The ``list`` of words created by splitting the text (``fragments``)
 * The count of words as a Python ``int`` (``length``)

Update the reference implementation and create a ``pybryt.Value()`` instance for both of these variables:

 .. code-block:: python

    def count_words(text: str) -> int:
        """
        Given the input string, ``text``, return the number
        of complete words.
        """
        # Split the text by spaces
        fragments = text.split()
        pybryt.Value(fragments)

        # Count the number of items in the result
        length = len(fragments)
        pybryt.Value(length)
        return length

Next, check your own implementation with some sample text that will also be used to test the student implementations:

.. code-block:: python

    assert count_words("Waltz, bad nymph, for quick jigs vex.") == 7
    assert count_words("The five boxing wizards-- \njump quickly!") == 6
    assert count_words("Sphinx of black quartz,          judge my vow.") == 7

Next Steps
----------

pybryt can do much more beyond this simple example, such as automating the assessment of student implementations and detecting plagiarism.

To learn more about pybryt, check out the following

* The example projects in the `demos folder <https://github.com/microsoft/pybryt/tree/main/demo/>`_
* Read the :ref:`api` for details on the annotation types