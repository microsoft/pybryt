"""Memory footprint container for PyBryt"""

import nbformat

from dataclasses import astuple, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ..utils import filter_pickleable_list, pickle_and_hash


class Event(Enum):
    """
    An enum of event ``sys.settrace`` event types traced by PyBryt.
    """

    LINE = "line"
    """indicates that a value was seen in a "line" event"""

    RETURN = "return"
    """indicates that a value was seen in a "return" event"""

    LINE_AND_RETURN = "line_and_return"
    """indicates that a value was seen in both a "line" and "return" event"""

    @classmethod
    def from_event_name(cls, event_name: str) -> Optional["Event"]:
        """
        Return the enum value corresponding to the event name, if present.

        Args:
            event_name (``str``): the event name provided by ``sys.settrace``

        Returns:
            :py:class:`Event`: the enum value corresponding to the event name if present,
                otherwise ``None``
        """
        return cls(event_name) if event_name in {v.value for v in cls.__members__.values()} else None


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


@dataclass
class MemoryFootprintValue:
    """
    A data class for an observed value in the memory footprint.

    The fields and their order should correspond to the structure of the tuples in
    :py:attribute:`MemoryFootprint.values`.
    """

    value: Any
    """the value"""

    timestamp: int
    """the timestamp at which this value was observed"""

    event: Optional[Event]
    """the trace function event that created this value, if applicable"""

    def to_list(self):
        return list(astuple(self))


class MemoryFootprint:
    """
    A memory footprint for an executed notebook.

    Args:
        counter (:py:class:`pybryt.execution.memory_footprint.Counter`, optional): a counter to use 
            for this footprint; if unprovided, a new one is initialized
    """

    counter: Counter
    """the counter used to construct this footprint"""

    _value_indices_by_hash: Dict[str, int]
    """indices of values keyed on their hashes"""

    values: List[Tuple[Any, int, Optional[Event]]]
    """the values, timestamps, and event types in the footprint"""

    calls: List[Tuple[str, str]]
    """the list of function calls tracked by the trace function"""

    imports: Set[str]
    """the set of modules imported during execution"""

    executed_notebook: Optional[nbformat.NotebookNode]
    """the final (pre-processed) notebook that was executed, with outputs"""

    def __init__(self, counter: Optional[Counter] = None):
        self.counter = counter if counter is not None else Counter()
        self._value_indices_by_hash = {}
        self.values = []
        self.calls = []
        self.imports = set()
        self.executed_notebook = None

    @classmethod
    def from_values(cls, *values: MemoryFootprintValue) -> 'MemoryFootprint':
        """
        Generate a memory footprint from values and their timestamps.
        Args:
            values_and_timestamps (:py:class:`MemoryFootprintValue`): the values

        Returns:
            :py:class:`pybryt.execution.memory_footprint.MemoryFootprint`: the memory footprint

        Raises:
            ``TypeError``: if any of the values is of the wrong type
        """
        if not all(isinstance(v, MemoryFootprintValue) for v in values):
            raise TypeError("Arguments to from_values must be of type MemoryFootprintValue")

        values = [astuple(v) for v in values]

        footprint = cls()
        footprint.values.extend(values)
        footprint.offset_counter(footprint.num_steps)
        return footprint

    @classmethod
    def combine(cls, *footprints: 'MemoryFootprint') -> 'MemoryFootprint':
        """
        Generate a memory footprint by combining memory footprints in-sequence.

        Duplicate values in different footprints are removed, keeping the first instance seen. The
        timestmaps of each footprint are offset by the number of steps in all preceding footprints.

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
            for fp_val in fp:
                h = pickle_and_hash(fp_val.value)
                if h not in seen:
                    fp_val.timestamp += timestamp_offset
                    new_fp.add_value(
                        fp_val.value,
                        fp_val.timestamp,
                        fp_val.event,
                        allow_duplicates=True,
                    )
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

    def add_value(
        self,
        val: Any,
        timestamp: Optional[int] = None,
        event: Optional[Event] = None,
        allow_duplicates: bool = False,
    ) -> None:
        """
        Add a value to the memory footprint.

        If the timestamp is unspeficied, the step counter is polled for the current value. By default,
        this method does not allow duplicate values to be entered into the footprint; this can be
        disabled using ``allow_duplicates``.

        Args:
            value (``object``): the value to add
            timestamp (``int``, optional): the timestamp
            event (:py:class:`Event`, optional): the event that produced the value
            allow_duplicates(``bool``): whether duplicate values should be allowed in the footprint
        """
        if not allow_duplicates:
            h = pickle_and_hash(val)
            if h in self._value_indices_by_hash:
                tup = self.values[self._value_indices_by_hash[h]]
                tup_event = tup[2]

                # update the event type if necessary
                if tup_event is None and event is not None:
                    tup_event = event
                elif tup_event is not None and event is not None and tup_event != event:
                    tup_event = Event.LINE_AND_RETURN
                
                self.values[self._value_indices_by_hash[h]] = (tup[0], tup[1], tup_event)

                return

            self._value_indices_by_hash[h] = len(self.values)

        if timestamp is None:
            timestamp = self.counter.get_value()

        self.values.append((val, timestamp, event))

    def get_value(self, index: int) -> MemoryFootprintValue: # TODO: change name??
        """
        Get the value at the specified index.

        Args:
            index (``int``): the index

        Returns:
            :py:class:`MemoryFootprintValue`: the value
        """
        return MemoryFootprintValue(*self.values[index])

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

    def filter_out_unpickleable_values(self) -> None:
        """
        Filter any unpickleable objects out of the list of value-timestamp tuples in-place.
        """
        filter_pickleable_list(self.values)

    def clear(self) -> None:
        """
        """
        self.values.clear()

    @property
    def num_steps(self) -> int:
        """
        ``int``: the total number of steps this implementation took
        """
        timestamps = [t[1] for t in self.values]
        return max(timestamps) if len(timestamps) else -1

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return MemoryFootprintIterator(self)

    def __eq__(self, other: Any):
        """
        Return whether another object is equal to this one.

        An object is equal to a memory footprint if it is also a memory footprint and has the same
        values, calls, imports, and executed notebook.
        """
        return isinstance(other, type(self)) and self.calls == other.calls \
            and self.imports == other.imports \
            and self.executed_notebook == other.executed_notebook \
            and pickle_and_hash(self.values) == pickle_and_hash(other.values)


class MemoryFootprintIterator:
    """
    An iterator class for memory footprints.

    Args:
        footprint (:py:class:`MemoryFootprint`): the memory footprint to iterate over
        start (``int``, optional): the index to start at
    """

    footprint: MemoryFootprint
    """the memory footprint being iterated over"""

    _index: int
    """the next index in the memory footprint to yield"""

    def __init__(self, footprint: MemoryFootprint, start: int = 0):
        self.footprint = footprint
        self._index = start

    def __next__(self) -> MemoryFootprintValue:
        if self._index < len(self.footprint):
            value = self.footprint.get_value(self._index)
            self._index += 1
            return value
        raise StopIteration()
