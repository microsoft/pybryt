.. _annotations:

Annotations
===========

.. toctree::
    :maxdepth: 3
    :hidden:

    value_annotations
    relational_annotations
    complexity_annotations
    type_annotations
    import_annotations
    collections
    initial_conditions
    invariants

Annotations are the basic building blocks, out of which reference
implementations are constructed. The annotations represent a single condition
that a student's implementation should meet, and they define a set of behaviors
for responding to the passing or failing of those conditions. Annotations
provide conditions not only for expecting a specific value but also for
combining those expectations to form conditions on the structure of the
student's code, including the temporal relationship of values and complex
boolean logic surrounding the presence or absence of those values.

All annotations are created by instantiating subclasses of the abstract
:py:class:`Annotation<pybryt.annotations.annotation.Annotation>` class. There 
are five main types of annotations: 
 
* :ref:`value annotations<value>`
* :ref:`relational annotations<relational>`
* :ref:`complexity annotations<complexity>`
* :ref:`type annotations<type>`
* :ref:`import annotations<import>`
* :ref:`annotation collections<collections>`


Annotation Arguments
--------------------

All annotations contain some core configurations that can be set using keyword arguments in the
constructor or by accessing the instance variables of that object. The table below lists these 
arguments.

.. list-table::
    :widths: 10 10 10 70

    * - Field Name
      - Keyword Argument
      - Type
      - Description
    * - ``name``
      - ``name``
      - ``str``
      - The name of the annotation; used to process ``limit``; automatically set if unspecified
    * - ``limit``
      - ``limit``
      - ``str``
      - The maximum number of annotations with a given ``name`` to track
    * - ``group``
      - ``group``
      - ``str``
      - The name of a group to which this annotation belongs; for running specific groups of annotations
        from a reference implementation
    * - ``success_message``
      - ``success_message``
      - ``str``
      - A message to be displayed to the student if the annotation is satisfied
    * - ``failure_message``
      - ``failure_message``
      - ``str``
      - A message to be displayed to the student if the annotation is *not* satisfied
