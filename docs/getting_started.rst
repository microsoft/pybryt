Getting Started
===============

Installing PyBryt
-----------------

We can install PyBryt inside a Python Virtual Environment, a Conda environment, or within a Jupyter Notebook.

Installing within a Jupyter Notebook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can add a magic-line command to a Jupyter notebook to install the requirements for a pip environment:

.. code-block:: python

    %pip install pybryt
    import pybryt

or, similarly, for a conda environment:

.. code-block:: python

    %conda install pybryt
    import pybryt

Installing on Windows PowerShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before installing, make sure you have a recent version of `Python 3 installed
<https://python.org/downloads>`_. Next, create a virtual environment, update
``pip``, and install ``pybryt``:

.. code-block:: console

    py -3 -m venv .venv
    .\venv\scripts\activate.ps1
    pip install -U pip
    pip install pybryt

Installing on macOS or Linux command-line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before installing, make sure you have a recent version of `Python 3 installed
<https://python.org/downloads>`_. Next, create a virtual environment, update
``pip``, and then install ``pybryt``:

.. code-block:: console

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install pybryt

Annotating a working example
----------------------------

PyBryt works by observing working reference implementations and looking for
annotated types and variables in other implementations. The first step after
installing PyBryt would be to create a working example to serve as a reference
implementation.

Let us say we want students to complete a simple task of counting the number of
words in a string. We send them the signature of the function and ask them to
complete it inside a Jupyter notebook:

.. code-block:: python

    def count_words(text: str) -> int:
        """
        Given the input string, ``text``, return the number
        of complete words.
        """
        pass

We could write this function by splitting the string using the builtin
``str.split()`` method, which will automatically remove empty strings, and then
count the number of items in the resulting list:

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

To annotate this example and train PyBryt what values (variables) to look for in
other implementations, we use the ``pybryt.Value`` class from the :ref:`api`.
``pybryt.Value`` takes any Python value as an input for its constructor.

The two key variables we want to observe in our example are:

 * The ``list`` of words created by splitting the text (``fragments``)
 * The count of words as a Python ``int`` (``length``)

Now, let us update the reference implementation and create a ``pybryt.Value()``
instance for both of these variables:

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

Next, we check our implementation with some text samples that we will also use to test the student implementations:

.. code-block:: python

    assert count_words("Waltz, bad nymph, for quick jigs vex.") == 7
    assert count_words("The five boxing wizards-- \njump quickly!") == 6
    assert count_words("Sphinx of black quartz,          judge my vow.") == 7

Next Steps
----------

PyBryt can do much more beyond this simple example, such as automating the
assessment of student implementations and detecting plagiarism. To learn more
about pybryt, check out the following

* The example projects in the `demos folder <https://github.com/microsoft/pybryt/tree/main/demo/>`_
* Read the :ref:`api` for details on the annotation types