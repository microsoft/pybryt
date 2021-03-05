"""
"""

import os
import dill
import base64
import nbformat

from typing import Any, List, NoReturn, Optional, Tuple, Union

from .reference import ReferenceImplementation, ReferenceResult
from .execution import execute_notebook, ObservedValue


NBFORMAT_VERSION = 4


class StudentImplementation:
    """
    """

    nb: nbformat.NotebookNode
    values: List[Tuple[Any, float]]
    start: float
    end: float

    def __init__(
        self, path_or_nb: Union[str, nbformat.NotebookNode], addl_filenames: List[str] = [],
        output: Optional[str] = None
    ):
        if isinstance(path_or_nb, str):
            self.nb = nbformat.read(path_or_nb, as_version=NBFORMAT_VERSION)
        elif isinstance(path_or_nb, nbformat.NotebookNode):
            self.nb = path_or_nb
        else:
            raise ValueError(f"path_or_nb is of unsupported type {type(path_or_nb)}")

        self._execute(addl_filenames=addl_filenames, output=output)

    def _execute(self, addl_filenames: List[str] = [], output: Optional[str] = None) -> NoReturn:
        self.start, self.end, self.values = execute_notebook(self.nb, addl_filenames=addl_filenames, output=output)

    def dump(self, dest: str = "student.pkl") -> NoReturn:
        with open(dest, "wb+") as f:
            dill.dump(self, f)

    def dumps(self) -> str:
        bits = dill.dumps(self)
        return base64.b64encode(bits).decode("ascii")

    @staticmethod
    def load(file: str) -> Union['StudentImplementation']:
        with open(file, "rb") as f:
            instance = dill.load(f)
        return instance

    @classmethod
    def loads(cls, data: str) -> "StudentImplementation":
        return dill.loads(base64.b64decode(data.encode("ascii")))

    def check(self, ref: Union[ReferenceImplementation, List[ReferenceImplementation]], group=None) -> \
            Union[ReferenceResult, List[ReferenceResult]]:
        if isinstance(ref, ReferenceImplementation):
            return ref.run(self.values, group=group)
        elif isinstance(ref, list):
            return [r.run(self.values, group=group) for r in ref]
        else:
            raise ValueError(f"check cannot take values of type '{type(ref)}'")
    
    def check_plagiarism(self, student_impls: List["StudentImplementation"], **kwargs) -> List[ReferenceResult]:
        refs = create_references([self], **kwargs)
        return get_impl_results(refs[0], student_impls, **kwargs)


from .plagiarism import create_references, get_impl_results
