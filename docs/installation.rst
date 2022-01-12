Installation
============

PyBryt can be installed with ``pip``, in a Python virtual environment, or using line magic in a
Jupyter Notebook.


Installing with ``pip``
-----------------------

Before installing, make sure you have a recent version of `Python 3 installed
<https://python.org/downloads>`_. Then, you can install PyBryt with ``pip``:

.. code-block:: console

    pip install pybryt

This method also works for installing PyBryt in a Conda environment, as long as you have activated
the environment in which you want PyBryt installed. You can also use:

.. code-block:: console

    conda run -n ENVIRONMENT_NAME pip install pybryt


Installing in a Python Virtual Environment
------------------------------------------

To install PyBryt in a Python virtual environment, update ``pip`` and install ``pybryt``.


Windows PowerShell
++++++++++++++++++

.. code-block:: console

    py -3 -m venv .venv
    .\.venv\scripts\activate.ps1
    pip install -U pip
    pip install pybryt


macOS or Linux command-line
+++++++++++++++++++++++++++

.. code-block:: console

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install pybryt


Installing within a Jupyter Notebook
------------------------------------

You can add a line magic command to a Jupyter notebook to install the requirements for a ``pip``
environment:

.. code-block:: python

    %pip install pybryt
    import pybryt
