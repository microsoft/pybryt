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

    py -3-m venv .venv
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

