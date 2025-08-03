from typing import TypeVar, Generic, Iterable
from collections import defaultdict

from ..constants import GrammarConstants


K = TypeVar('K')
V = TypeVar('V')

class _GrammarDefaultDict(defaultdict,  Generic[K, V]):
    """
    A specialized ``defaultdict`` that supports wildcard access via the ``GrammarConstants.ANY_SYMBOL`` key.

    This dictionary behaves like a regular ``defaultdict``, but when accessed with
    the special key, it aggregates and returns all values stored under
    all keys as a single merged list.

    It also supports multiple keys given as a ``list``.

    Example:

        >>> d = _GrammarDefaultDict(list)
        >>> d["a"].append(1)
        >>> d["b"].extend([2, 3])
        >>> d["c"].extend([4, 5])
        >>> d["__ANY__"]
        [1, 2, 3, 4, 5]
        >>> d[["a", "b"]]
        [1, 2, 3]
    """
    def get_group(self, keys: Iterable[K]) -> V:
        output = []
        for key in keys:
            output += super().__getitem__(key)
        return output # type: ignore
    
    def __getitem__(self, key: K ) -> V:
        if GrammarConstants.ANY_SYMBOL == key:
            all_values = []
            for value in self.values():
                all_values.extend(value)
            return all_values # type: ignore
         
        return super().__getitem__(key)

