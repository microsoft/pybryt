"""Annotation helpers for structural pattern matching"""

__all__ = ["structural"]

import importlib

from typing import Any, Dict, List, Optional, Tuple


class _StructuralPattern:
    """
    A singleton that can be used for structural pattern matching.

    Structural patterns can be created by accessing attributes of this singleton and calling them
    with attribute-value pairs as arguments. For example, if you're matching an instance of
    ``mypackage.Foo`` with attribute ``bar`` set to ``2``, a structural pattern for this could be
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
    """

    _parents: List[str]
    """the package hierarchy this module or class is in"""

    _curr: Optional[str]
    """the name of this module or class"""

    _unnamed_attrs: List[Any]
    """a list of attributes the object described should have, ignoring the names of those attributes"""

    _named_attrs: Dict[str, Any]
    """attributes the object described should have by their names"""

    _elements: List[Any]
    """elements expected to be contained by a matching object"""

    def __init__(self, _parents=None, _curr=None, _unnamed_attrs=None, _elements=None, **named_attrs):
        self._parents = [] if _parents is None else _parents
        self._curr = _curr
        self._unnamed_attrs = [] if _unnamed_attrs is None else _unnamed_attrs
        self._elements = [] if _elements is None else _elements
        self._named_attrs = named_attrs

    def _get_mod_cls(self) -> Tuple[str, str]:
        """
        Get a tuple containing the importable module and class names.

        Returns:
            ``tuple[str, str]``: the module name and class name
        """
        return ".".join(self._parents), self._curr

    def __repr__(self):
        mod, cls = self._get_mod_cls()
        mod = mod + "." if mod else mod
        return f"pybryt.structural.{mod}{cls}({', '.join(f'{k}={v}' for k, v in self._named_attrs.items())})"

    def __getattr__(self, attr: str) -> "_StructuralPattern":
        if attr in {"__getstate__", "__slots__", "__setstate__"}:  # for dill
            raise AttributeError

        parents = self._parents.copy()
        if self._curr:
            parents += [self._curr]

        return type(self)(_parents=parents, _curr=attr)

    def __call__(self, *unnamed_attrs, **named_attrs) -> "_StructuralPattern":
        return type(self)(
            _parents=self._parents,
            _curr=self._curr,
            _unnamed_attrs=list(unnamed_attrs),
            _elements=self._elements.copy(),
            **named_attrs,
        )

    def _check_object_attrs(self, obj: Any) -> bool:
        """
        Check whether the specified object's attributes match those specified by this pattern.

        Args:
            obj (``object``): the object to check

        Returns:
            ``bool``: whether the object's attributes match
        """
        for a, v in self._named_attrs.items():
            if not hasattr(obj, a):
                return False

            if isinstance(v, type(self)):
                if v != getattr(obj, a):
                    return False

            else:
                v = v if isinstance(v, Value) else Value(v)
                if not v.check_against(getattr(obj, a)):
                    return False

        for v in self._unnamed_attrs:
            has_attr = False
            for a in dir(obj):
                if getattr(obj, a) == v:
                    has_attr = True
                    break

            if not has_attr:
                return False

        for e in self._elements:
            try:
                if e not in obj:
                    return False
            except TypeError:
                return False

        return True

    def contains_(self, *elements: Any) -> "_StructuralPattern":
        """
        Add a clause to this structural pattern indicating that a matching object should contain
        the specified elements.

        Args:
            *elements (``object``): the elements to check for

        Returns:
            a new structural pattern with the added condition
        """
        return type(self)(
            _parents=self._parents,
            _curr=self._curr,
            _unnamed_attrs=self._unnamed_attrs.copy(),
            _elements=list(elements),
            **self._named_attrs,
        )

    def __eq__(self, other: Any) -> bool:
        """
        Determine whether another object matches this structural pattern.

        Args:
            other (``object``): the object to check

        Returns:
            ``bool``: whether the object matches
        """
        mod, cls = self._get_mod_cls()
        class_ = getattr(importlib.import_module(mod), cls) if mod else None
        is_instance = isinstance(other, class_) if mod else other.__class__.__name__ == cls
        return is_instance and self._check_object_attrs(other)


structural = _StructuralPattern()


from .value import Value
