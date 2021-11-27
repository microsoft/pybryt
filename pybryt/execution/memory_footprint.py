"""Memory footprint container for PyBryt"""

import nbformat

from typing import Any, List, Optional, Set, Tuple, Union

from ..utils import filter_picklable_list, pickle_and_hash


class Counter:
    """
    A counter for tacking the step number in the tracing function.

    Args:
        start (``int``): the starting value of the counter
    """

    val: int
    """the current value of the counter"""

    def __init__(self, start: int = 0):
        self.val = start

    def get_value(self) -> int:
        """
        Get the current value of the counter.

        Returns:
            ``int``: the current value of the counter
        """
        return self.val

    def increment(self) -> None:
        """
        Increment the counter by one.
        """
        self.val += 1

    def offset(self, val: int) -> None:
        """
        Offset the counter by a specific amount.

        Args:
            val (``int``): the amount to offset by
        """
        self.val += val


class MemoryFootprint:
    """
    A memory footprint for an executed notebook.

    Args:
        counter (:py:class:`pybryt.execution.memory_footprint.Counter`, optional): a counter to use 
            for this footprint; if unprovided, a new one is initialized
    """

    counter: Counter
    """the counter used to construct this footprint"""

    _hashes: Set[str]
    """set of hashed values present in the memory footprint"""

    values: List[Tuple[Any, int]]
    """the values and timestamps in the footprint"""

    calls: List[Tuple[str, str]]
    """the list of function calls tracked by the trace function"""

    imports: Set[str]
    """the set of modules imported during execution"""

    executed_notebook: Optional[nbformat.NotebookNode]
    """the final (pre-processed) notebook that was executed, with outputs"""

    def __init__(self, counter: Optional[Counter] = None):
        self.counter = counter if counter is not None else Counter()
        self._hashes = set()
        self.values = []
        self.calls = []
        self.imports = set()
        self.executed_notebook = None

    @classmethod
    def from_values(cls, *values_and_timestamps: Union[Any, int]) -> 'MemoryFootprint':
        """
        Generate a memory footprint from values and their timestamps.

        Values and timestamps should be provided in sequence, with a value followed by its timestmap.
        For example:

        .. code-block:: python

            MemoryFootprint.from_values(val1, ts1, val2, ts2, val3, ts3, ...)

        Args:
            values_and_timestamps (``object | int``): the values and timestamps

        Returns:
            :py:class:`pybryt.execution.memory_footprint.MemoryFootprint`: the memory footprint

        Raises:
            ``ValueError``: if an odd number of arguments is provided
            ``TypeError``: if one of the timestamps is not an ``int``
        """
        if len(values_and_timestamps) % 2 != 0:
            raise ValueError("Uneven number of arguments provided")

        values = [(values_and_timestamps[2 * i], values_and_timestamps[2 * i + 1]) \
            for i in range(len(values_and_timestamps) // 2)]

        not_ints = [not isinstance(ts, int) for _, ts in values]
        if any(not_ints):
            bad_idx = not_ints.index(True)
            raise TypeError(f"Provided timestamp is not an integer: {values[bad_idx][1]}")

        footprint = cls()
        footprint.values.extend(values)
        footprint.offset_counter(footprint.num_steps)
        return footprint

    @classmethod
    def combine(cls, *footprints: 'MemoryFootprint') -> 'MemoryFootprint':
        """
        Generate a memory footprint by combining memory footprints in-sequence.

        Duplicate values in different footprints are removed, keeping the first instance seen. The
        timestmaps of each footprint are offset by the number of steps in all preceeding footprints.

        Args:
            *footprints (:py:class:`pybryt.execution.memory_footprint.MemoryFootprint`): the 
                footprints

        Returns:
            :py:class:`pybryt.execution.memory_footprint.MemoryFootprint`: the memory footprint
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
        Increment the step counter by one.
        """
        self.counter.increment()

    def offset_counter(self, val: int) -> None:
        """
        Offset the step counter by a specific amount.

        Args:
            val (``int``): the amount to offset by
        """
        self.counter.offset(val)

    def add_value(self, val: Any, timestamp: Optional[int] = None, allow_duplicates: bool = False) -> None:
        """
        Add a value to the memory footprint.

        If the timestamp is unspeficied, the step counter is polled for the current value. By default,
        this method does not allow duplicate values to be entered into the footprint; this can be
        disabled using ``allow_duplicates``.

        Args:
            value (``object``): the value to add
            timestamp (``int``, optional): the timestamp
            allow_duplicates(``bool``): whether duplicate values should be allowed in the footprint
        """
        if not allow_duplicates:
            h = pickle_and_hash(val)
            if h in self._hashes:
                return

            self._hashes.add(h)

        if timestamp is None:
            timestamp = self.counter.get_value()

        self.values.append((val, timestamp))

    def get_value(self, index: int) -> Any:
        """
        Get the value at the specified index.

        Args:
            index (``int``): the index

        Returns:
            ``object``: the value
        """
        return self.values[index][0]

    def get_timestamp(self, index: int) -> int:
        """
        Get the timestamp of the value at the specified index.

        Args:
            index (``int``): the index

        Returns:
            ``int``: the timestamp
        """
        return self.values[index][1]

    def add_call(self, filename: str, fn_name: str) -> None:
        """
        Add a function call.

        Args:
            filename (``str``): the filename of the function
            fn_name (``str``): the name of the function
        """
        self.calls.append((filename, fn_name))

    def add_imports(self, *modules: str) -> None:
        """
        Add imports to the set of imports

        Args:
            *modules (``str``): the modules to add
        """
        self.imports.update(modules)

    def set_executed_notebook(self, nb: nbformat.NotebookNode) -> None:
        """
        Set the executed notebook of this memory footprint.

        Args:
            nb (``nbformat.NotebookNode``): the notebook
        """
        self.executed_notebook = nb

    def filter_out_unpicklable_values(self) -> None:
        """
        Filter any unpicklable objects out of the list of value-timestamp tuples in-place.
        """
        filter_picklable_list(self.values)

    @property
    def num_steps(self) -> int:
        """
        ``int``: the total number of steps this implementation took
        """
        timestamps = [t[1] for t in self.values]
        return max(timestamps) if len(timestamps) else -1

    def __eq__(self, other: Any):
        """
        Return whether another object is equal to this one.

        An object is equal to a memory footprint if it is also a memory fotprint and has the same
        values, calls, imports, and executed notebook.
        """
        return isinstance(other, type(self)) and self.values == other.values \
            and self.calls == other.calls and self.imports == other.imports \
            and self.executed_notebook == other.executed_notebook
