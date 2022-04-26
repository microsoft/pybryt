Structural Pattern Matching
===========================

PyBryt supports structural pattern matching in order to allow you to create annotations that check
the structure of objects instead of using an ``==`` check. Structural patterns can be created by
accessing attributes of the singleton
:py:obj:`pybryt.structural<pybryt.annotations.structural.structural>` and calling them
with attribute-value pairs as arguments. For example, if you're matching an instance of
``mypackage.Foo`` with attribute ``bar`` set to ``2``; a structural pattern for this could be
created with

.. code-block:: python

    pybryt.structural.mypackage.Foo(bar=2)

If there are attributes you want to look for without a specific name, you can pass these as
positional arguments:

.. code-block:: python

    pybryt.structural.mypackage.Foo(3, bar=2)

To determine whether an object matches the structural pattern, PyBryt imports the package and
retrieves the specified class. In the examples above, this would look like

.. code-block:: python

    getattr(importlib.import_module("mypackage"), "Foo")

If the provided object is an instance of this class and has the specified attributes, the object
matches. You can determine if an object matches a structural pattern using an ``==`` comparison.

If no package is specified for the class, the pattern just checks that the name of the class
matches the name of the class in the structural pattern, without importing any modules. For
example:

.. code-block:: python

    df_pattern = pybryt.structural.DataFrame()
    df_pattern == pd.DataFrame()  # returns True

    class DataFrame:
        pass

    df_pattern == DataFrame()     # returns True

Attribute values are matched using the same algorithm as
:py:class:`Value<pybryt.annotations.value.Value>` annotations. If you would like to make use of
the options available to :py:class:`Value<pybryt.annotations.value.Value>` annotations, you can
also pass an annotation as an attribute value:

.. code-block:: python

    pybryt.structural.mypackage.Foo(pi=pybryt.Value(np.pi, atol=1e-5))

For checking whether an object contains specific members (determined via the use of Python's
``in`` operator), use the ``contains_`` method:

.. code-block:: python

    pybryt.structural.mypackage.MyList().contains_(1, 2, 3)
