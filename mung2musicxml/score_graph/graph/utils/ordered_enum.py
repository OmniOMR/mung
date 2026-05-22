
from typing import Any
from enum import StrEnum


class AutoOrderedStrEnum(StrEnum):
    """
    Orders constants defined in the `StrEnum`
    by the order in which they were defined,
    from top to bottom.

    Example::

        class D(AutoOrderedStrEnum):
            FIRST = "first"
            SECOND = "second"
            THIRD = "third"

        >>> D.FIRST > D.SECOND
        False
        >>> D.SECOND < D.THIRD
        True
    """
    @classmethod
    def _order_map(cls):
        return {name: i for i, name in enumerate(cls._member_names_)}

    def _rank(self):
        return self._order_map()[self.name]

    def __lt__(self, other: Any):
        if type(other) is type(self):
            return self._rank() < other._rank()
        return NotImplemented

    def __le__(self, other: Any):
        if type(other) is type(self):
            return self._rank() <= other._rank()
        return NotImplemented

    def __gt__(self, other: Any):
        if type(other) is type(self):
            return self._rank() > other._rank()
        return NotImplemented

    def __ge__(self, other: Any):
        if type(other) is type(self):
            return self._rank() >= other._rank()
        return NotImplemented


if __name__ == "__main__":
    print(f"Running {AutoOrderedStrEnum.__name__} demo")
    class DemoClass(AutoOrderedStrEnum):
        FIRST = "first"
        SECOND = "second"
        THIRD = "third"

    first, second, third = DemoClass.FIRST, DemoClass.SECOND, DemoClass.THIRD

    print(f"{first < second=}")
    print(f"{first < third=}")