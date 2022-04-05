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
    """

    parents: List[str]
    """the package hierarchy this module or class is in"""

    curr: Optional[str]
    """the name of this module or class"""

    unnamed_attrs: List[Any]
    """a list of attributes the object described should have, ignoring the names of those attributes"""

    named_attrs: Dict[str, Any]
    """attributes the object described should have by their names"""

    def __init__(self, parents=None, curr=None, unnamed_attrs=None, **named_attrs):
        self.parents = [] if parents is None else parents
        self.curr = curr
        self.unnamed_attrs = [] if unnamed_attrs is None else unnamed_attrs
        self.named_attrs = named_attrs

    def _get_mod_cls(self) -> Tuple[str, str]:
        """
        Get a tuple containing the importable module and class names.

        Returns:
            ``tuple[str, str]``: the module name and class name
        """
        return ".".join(self.parents), self.curr

    def __repr__(self):
        mod, cls = self._get_mod_cls()
        mod = mod + "." if mod else mod
        return f"pybryt.structural.{mod}{cls}({', '.join(f'{k}={v}' for k, v in self.named_attrs.items())})"

    def __getattr__(self, attr: str) -> "_StructuralPattern":
        if attr in {"__getstate__", "__slots__", "__setstate__"}:  # for dill
            raise AttributeError

        parents = self.parents.copy()
        if self.curr:
            parents += [self.curr]

        return type(self)(parents=parents, curr=attr)

    def __call__(self, *unnamed_attrs, **named_attrs) -> "_StructuralPattern":
        return type(self)(
            parents=self.parents,
            curr=self.curr,
            unnamed_attrs=list(unnamed_attrs),
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
        for a, v in self.named_attrs.items():
            if isinstance(v, type(self)):
                if v != getattr(obj, a):
                    return False

            else:
                v = v if isinstance(v, Value) else Value(v)
                if not v.check_against(getattr(obj, a)):
                    return False

        for v in self.unnamed_attrs:
            has_attr = False
            for a in dir(obj):
                if getattr(obj, a) == v:
                    has_attr = True
                    break

            if not has_attr:
                return False

        return True

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
