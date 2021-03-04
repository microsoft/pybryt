.. PyBryt documentation master file, created by
   sphinx-quickstart on Sun Feb 21 11:51:56 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyBryt Documentation
====================

.. toctree::
   :maxdepth: 3
   :hidden:

   annotations/index
   reference_implementations
   student_implementations
   api_reference

PyBryt is an open source  Python auto-assessment library for teaching and learning. Our goal is to empower students and educators to learn about technology through fun, guided, hands-on content aimed at specific learning goals. PyBryt is designed to work with existing autograding solutions and workflows such as `Otter Grader`_, `OkPy`_, and `Autolab`_.

.. image:: _static/images/pybryt_goals.png

Educators and institutions can leverage PyBryt to integrate auto-assessment and reference models to hands-on labs and assessments.

- Educators do not have to enforce the structure of the solution
- Learners practice the design process, code design, and solution implementation
- Meaningful pedagogical feedback to the learners
- Analysis of complexity within the learner's solution
- Plagiarism detection and support for reference implementations
- Easy integration into existing organizational or institutional grading infrastructure

PyBryt's core auto-assessment behavior operates by comparing a student's implementation of some 
programming problem to a series of reference implementations provided by an instructor. A 
**reference implementation** defines a pattern of values, and conditions on those values, to look 
for in students' code.

A reference implementation is created by annotating code written or found by an instructor and 
executing this code to create a :py:class:`ReferenceImplementation<pybryt.ReferenceImplementation>` 
object. Annotations are created by creating instances of subclasses of the abstract 
:py:class:`Annotation<pybryt.Annotation>` class.

.. _Otter Grader: https://otter-grader.readthedocs.io
.. _OkPy: https://okpy.org
.. _Autolab: https://autolab.readthedocs.io/
