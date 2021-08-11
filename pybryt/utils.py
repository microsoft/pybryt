"""Various utilities for PyBryt"""

import os
import json
import random
import base64
import string
import dill
import hashlib
import time
import nbformat

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union
from IPython import get_ipython
from IPython.display import publish_display_data


def pickle_and_hash(obj: Any) -> str:
    """
    Uses ``dill`` to pickle an object and returns the SHA-512 hash of the returned bytes.

    Args:
        obj (``object``): the object to pickle and hash
    
    Returns:
        ``str``: the hex digest of the SHA-512 hash of the pickled object
    """
    s = dill.dumps(obj)
    return hashlib.sha512(s).hexdigest()


def filter_picklable_list(lst: List[Any]) -> None:
    """
    Removes all elements from a list that cannot be pickled with ``dill``.

    Args:
        lst (``list[object]``): the list to filter
    """
    to_delete = []
    for i, v in enumerate(lst):
        try:
            dill.dumps(v)
        except:
            to_delete.append(i)
    
    to_delete.reverse()
    for i in to_delete:
        lst.pop(i)


def notebook_to_string(nb_path: Union[str, nbformat.NotebookNode]) -> str:
    """
    Converts a Jupyter Notebook to a string of executable Python code.

    Args:
        nb_path (``str`` or ``nbformat.NotebookNode``): the path to the notebook or the notebook
            in-memory
    
    Returns:
        ``str``: the string of all Python code from the notebook
    """   
    if isinstance(nb_path, str):
        with open(nb_path) as f:
            nb = json.load(f)
    elif isinstance(nb_path, nbformat.NotebookNode):
        nb = nb_path
    else:
        raise TypeError("invalid notebook type")
    
    source = ""
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            if isinstance(cell['source'], list):
                source += "".join(cell['source']) + "\n"
            else:
                assert isinstance(cell['source'], str), f"could not parse notebook cell: {cell}"
                source += cell['source'] + "\n"

    source = "\n".join(l for l in source.split("\n") if not l.startswith("%") and not l.startswith("!"))
    return source


def make_secret(size=6, chars=string.ascii_uppercase + string.digits):
    """
    This function generates a random string using the given length and character set.
    
    Args:
        size (``int``, optional): the length of output name
        chars (``str``, optional): the set of characters used to create function name
    
    Returns:
        ``str``: randomly-generated string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def save_notebook(filename, timeout=10):
    """
    Force-saves a Jupyter Notebook by displaying JavaScript.

    Args:
        filename (``str``): path to notebook file being saved
        timeout (``int`` or ``float``): number of seconds to wait for save before timing-out
    
    Returns
        ``bool``: whether the notebook was saved successfully
    """
    if get_ipython() is not None:
        f = open(filename, "rb")
        md5 = hashlib.md5(f.read()).hexdigest()
        start = time.time_ns()
        publish_display_data({"application/javascript": """
            if (typeof Jupyter !== "undefined") {
                Jupyter.notebook.save_notebook();
            }
        """})
        
        curr = md5
        while curr == md5 and time.time_ns() - start <= timeout * 10**9:
            time.sleep(1)
            f.seek(0)
            curr = hashlib.md5(f.read()).hexdigest()
        
        f.close()

        return curr != md5


def get_stem(fp) -> str:
    """
    Returns the stem of a filepath.

    Args:
        fp (``str``): the filepath

    Returns:
        ``str``: the stem of the filepath
    """
    return os.path.splitext(os.path.split(fp)[1])[0]


class Serializable(ABC):
    """
    A class that implements serialization using the ``dill`` library.
    """

    @property
    @abstractmethod
    def _default_dump_dest(self) -> str:
        """
        Default destination path for the ``dump`` method
        """
        ... # pragma: no cover

    def dump(self, dest: Optional[str] = None) -> None:
        """
        Pickles this object to a file.

        Args:
            dest (``str``, optional): the path to the file
        """
        if dest is None:
            dest = self._default_dump_dest
        with open(dest, "wb+") as f:
            dill.dump(self, f)

    def dumps(self) -> str:
        """
        Pickles this object to a base-64-encoded string.

        Returns:
           ``str``: the pickled and encoded object
        """
        bits = dill.dumps(self)
        return base64.b64encode(bits).decode("ascii")

    @classmethod
    def load(cls, file: str) -> 'Serializable':
        """
        Unpickles an object from a file.

        Args:
            file (``str``): the path to the file
        
        Returns:
            ``Serializable``: the unpickled object
        """
        with open(file, "rb") as f:
            instance = dill.load(f)
        if not isinstance(instance, cls):
            raise TypeError(f"Unpickled object is not of type {cls}")
        return instance

    @classmethod
    def loads(cls, data: str) -> "Serializable":
        """
        Unpickles an object from a base-64-encoded string.

        Args:
            data (``str``): the pickled and encoded object
        
        Returns:
            ``Serializable``: the unpickled object
        """
        instance = dill.loads(base64.b64decode(data.encode("ascii")))
        if not isinstance(instance, cls):
            raise TypeError(f"Unpickled object is not of type {cls}")
        return instance
