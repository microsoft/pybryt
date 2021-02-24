Reference Implementations
=========================

.. toctree::
   :hidden:
   :maxdepth: 3

   annotations
   invariants
   reference_objects

PyBryt's core auto-assessment behavior operates by comparing a student's implementation of some 
programming problem to a series of reference implementations provided by an instructor. A 
**reference implementation** defines a pattern of values, and conditions on those values, to look 
for in students' code.

A reference implementation is created by annotating code written or found by an instructor and 
executing this code to create a :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` 
object. Annotations are created by creating instances of subclasses of the abstract 
:py:class:`Annotation<pybryt.Annotation>` class.

This section details the creation and behavior of the different annotation classes that PyBryt 
provides and describes how reference implementations as a single unit are created, manipulated, 
stored, and run.
