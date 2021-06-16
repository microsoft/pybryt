.. _collections:

Annotation Collections
======================

To faciliate the easy grouping and management of annotations, PyBryt provides the 
:py:class:`Collection<pybryt.annotations.collection.Collection>` annotation, which collects a series
of other annotations into a group. Collections can be instantiated by passing zero or more
annotations to the constructor, along with the other usual keyword arguments for other annotations.
To add additional annotations to the collection, use 
:py:meth:`Collection.add<pybryt.annotations.collection.Collection.add>`.

.. code-block:: python

    l = [3, 2, 1, 4, -3, -3, 3, 4]

    collection = pybryt.Collection(pybryt.Value(l))

    # calculate the partial products of a list
    prod = 1
    for i in range(len(l)):
        prod *= l[i]
        l[i] = prod
        collection.add(pybryt.Value(l))

Annotations can be removed from the collection using
:py:meth:`Collection.remove<pybryt.annotations.collection.Collection.remove>`:

.. code-block:: python

    val = pybryt.Value(l)
    collection = pybryt.Collection(val)
    collection.remove(val)

Collection annotations can be used to simplify the creation of temporal annotations. Rather than
reassigning variables and using the ``before`` method over and over again, you can simply create
a collection and set ``enforce_order=True`` in the constructor. This will mean that the collection
is only satisfied if the satisfying timestamps of its annotations occur in non-decreasing order based
on the order the annotations were added in. For the example above, this can be done with:

.. code-block:: python

    l = [3, 2, 1, 4, -3, -3, 3, 4]

    collection = pybryt.Collection(pybryt.Value(l), enforce_order=True)  # this is the only difference!

    # calculate the partial products of a list
    prod = 1
    for i in range(len(l)):
        prod *= l[i]
        l[i] = prod
        collection.add(pybryt.Value(l))

Collections can also be used to simplify the management of success and failure messages by linking
them to a specific group of annotations:

.. code-block:: python

    l = [3, 2, 1, 4, -3, -3, 3, 4]

    collection = pybryt.Collection(pybryt.Value(l), enforce_order=True,
                                   failure_message="Take a look at your partial product algorithm.")

    # calculate the partial products of a list
    prod = 1
    for i in range(len(l)):
        prod *= l[i]
        l[i] = prod
        collection.add(pybryt.Value(l))
