.. _import:

Import Annotations
==================

Import annotations can be used to either require or forbid the use of specific libraries. When PyBryt
executes a notebook, it parses the AST of each code cell to determine any libraries imported in the
code. It also captures the modules that any functions or classes it finds belong to when it is
tracing through the notebook's code. These are collected into a set of library names, which are 
included in the memory footprint.

All import annotations are subclasses of the abstract 
:py:class:`ImportAnnotation<pybryt.annotations.import_.ImportAnnotation>` class. When these
annotations are instantiated, they attempt to import the module to ensure that the string passed
for the module name is valid. This means that any modules used in import annotations must be installed
in the environment in which the reference implementation is compiled.


Require Import
--------------

To require an import, use the :py:class:`RequireImport<pybryt.annotations.import_.RequireImport>`
annotation, which takes the name of the library as a string (along with the usual set of arguments
that annotation constructors accept).

.. code-block:: python

    pybryt.RequireImport("pandas")


Forbid Import
-------------

To forbid an import, use the :py:class:`ForbidImport<pybryt.annotations.import_.ForbidImport>`
annotation, which, like the :py:class:`RequireImport<pybryt.annotations.import_.RequireImport>`
annotation, takes the name of the libary as its only positional argument.

.. code-block:: python

    pybryt.ForbidImport("numpy")
