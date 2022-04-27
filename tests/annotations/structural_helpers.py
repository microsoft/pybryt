"""Helpers for structural pattern tests"""

from typing import Any, Dict, List


class AttrContainer:

    attrs: Dict[str, Any]

    def __init__(self, **kwargs) -> None:
        self.attrs = {**kwargs}

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "attrs":
            self.__dict__["attrs"] = value
        else:
            self.attrs[name] = value

    def __getattr__(self, name: str) -> Any:
        if name not in self.attrs:
            raise AttributeError
        return self.attrs[name]

    def __dir__(self) -> List[str]:
        return sorted(list(self.attrs.keys()) + ["attrs"])


class Container(AttrContainer):

    def __init__(self, *elements: Any) -> None:
        super().__init__()
        self.elements = list(elements)

    def __contains__(self, element: Any) -> bool:
        return element in self.elements
