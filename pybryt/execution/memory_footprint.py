"""Memory footprint container for PyBryt"""

import nbformat

from typing import Any, List, Optional, Set, Tuple

from ..utils import filter_picklable_list, pickle_and_hash


class Counter:
    """
    """

    val: int

    def __init__(self, start: int = 0):
        self.val = start

    def get_value(self) -> int:
        return self.val

    def increment(self) -> None:
        self.val += 1

    def offset(self, val: int) -> None:
        self.val += val


class MemoryFootprint:
    """
    """

    counter: Counter

    values: List[Tuple[Any, int]]

    calls: List[Tuple[str, str]]

    imports: Set[str]

    executed_notebook: Optional[nbformat.NotebookNode]

    def __init__(self, counter: Optional[Counter] = None):
        self.counter = counter if counter is not None else Counter()
        self.values = []
        self.calls = []
        self.imports = set()
        self.executed_notebook = None

    @classmethod
    def from_values(cls, values: List[Tuple[Any, int]]) -> 'MemoryFootprint':
        """
        """
        footprint = cls()
        footprint.values.extend(values)
        footprint.offset_counter(footprint.num_steps)
        return footprint

    @classmethod
    def combine(cls, *footprints: 'MemoryFootprint') -> 'MemoryFootprint':
        """
        """
        new_fp = cls()
        seen = set()          # set to track which values we've seen
        timestamp_offset = 0  # offset for timestamps in the new memory footprint
        for fp in footprints:
            map(lambda c: new_fp.add_call(*c), fp.calls)
            for obj, ts in fp.values:
                h = pickle_and_hash(obj)
                if h not in seen:
                    ts += timestamp_offset
                    new_fp.add_value(obj, ts)
                    seen.add(h)

            timestamp_offset += fp.num_steps

        new_fp.offset_counter(timestamp_offset)
        return new_fp

    def increment_counter(self) -> None:
        """
        """
        self.counter.increment()

    def offset_counter(self, val: int) -> None:
        """
        """
        self.counter.offset(val)

    def add_value(self, val: Any, timestamp: Optional[int] = None) -> None:
        """
        """
        if timestamp is None:
            timestamp = self.counter.get_value()
        self.values.append((val, timestamp))

    def get_value(self, index: int) -> Tuple[Any, int]:
        """
        """
        return self.values[index]

    def add_call(self, filename: str, fn_name: str) -> None:
        """
        """
        self.calls.append((filename, fn_name))

    def add_imports(self, *modules: str) -> None:
        """
        """
        self.imports.update(modules)

    def set_executed_notebook(self, nb: nbformat.NotebookNode) -> None:
        """
        """
        self.executed_notebook = nb

    def filter_out_unpicklable_values(self) -> None:
        """
        """
        filter_picklable_list(self.values)

    @property
    def num_steps(self) -> int:
        """"""
        timestamps = [t[1] for t in self.values]
        return max(timestamps) if len(timestamps) else -1

    # TODO: docstring
    def __eq__(self, other: Any):
        return isinstance(other, type(self)) and self.values == other.values \
            and self.calls == other.calls and self.imports == other.imports \
            and self.executed_notebook == other.executed_notebook
