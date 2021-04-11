""""""

import numpy as np
import pandas as pd

class AttrDict(dict):

    def __getattr__(self, attr):
        return self[attr]


def assert_notebook_contents_equal(nb1, nb2):
    """
    """
    for c1, c2 in zip(nb1["cells"], nb2["cells"]):
        assert c1["cell_type"] == c2["cell_type"], f"{c1}\n\n{c2}"
        assert c1["source"] == c2["source"], f"{c1}\n\n{c2}"
        assert c1.get("outputs", []) == c2.get("outputs", []), f"{c1}\n\n{c2}"


def check_values_equal(v1, v2):
    """
    """
    if isinstance(v1, np.ndarray) and isinstance(v2, np.ndarray):
        return np.allclose(v1, v2), f"{v1}\n\n{v2}"
    elif isinstance(v1, pd.DataFrame) or isinstance(v2, pd.DataFrame):
        return (v1 == v2).all().all(), f"{v1}\n\n{v2}"
    elif isinstance(v1, (np.ndarray, pd.Series)) or isinstance(v2, (np.ndarray, pd.Series)):
        return (v1 == v2).all(), f"{v1}\n\n{v2}"
    else:
        return v1 == v2, f"{v1}\n\n{v2}"
