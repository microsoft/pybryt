.. _invariants:

Invariants
==========

Invariants provide logic for determining whether a value satisfies a value annotation. They can be
used to ensure that annotations can still be satisfied independent of the different ways students
format their answers.


Invariant Structure
-------------------

Invariants are subclasses of the abstract base class 
:py:class:`invariants.invariant<pybryt.annotations.invariants.invariant>`. All subclasses implement
the static :py:meth:`run<pybryt.annotations.invariants.invariant.run>` method, which takes in a list of
objects and returns a transformed list of objects that contains all versions of every object in the
input list which are considered equal.

Consider an invariant for string capitalization. The ``run`` method of this invariant takes in a list 
of objects and returns the same list but with every string lowercased. For a matrix transposition
invariant, the ``run`` method might return a list with every 2D array's transpose included, as well
as the original array.

Invariants have a custom ``__new__`` method that calls the ``run`` method, so that they function as
callables rather than classes.

PyBryt supports custom invariants. To create your own invariant, subclass 
:py:class:`invariants.invariant<pybryt.annotations.invariants.invariant>` and implement the ``run``
method.


Built-In Invariants
-------------------

A list of built-in invariants can be found :ref:`here<invariants_ref>`.
