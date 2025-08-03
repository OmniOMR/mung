import re
from typing import Optional, Any

from ..constants import GrammarConstants


class Cardinality:
    """
    Keeps track of minimal and maximal value.
    Has the ability to check that a given number is within its bounds.

    Supported formats when parsing from string:
        - ``"{<number1>,<number2>}"`` = cardinality with min ``number1`` and max ``number2``
        - ``"{<number1>,}"`` = cardinality with min ``number1`` and max ``np.inf``
        - ``"{,<number1>}"`` = cardinality with min ``0`` and max ``number1``
        - ``"{<number1>}"`` = cardinality with min ``number1`` and max ``number1``

    Example:

    >>> c = Cardinality.from_string("{2,5}")
    >>> c.is_in_bounds(5)
    True
    >>> c.is_in_bounds(1)
    False
    """
    _DELIMITER = ","

    def __init__(self, min_links: Optional[int] = None, max_links: Optional[int] = None):
        if min_links is None:
            self.min: int = GrammarConstants.DEFAULT_LOWER_LIMIT
        else:
            self.min: int = min_links
        if max_links is None:
            self.max: int = GrammarConstants.DEFAULT_UPPER_LIMIT
        else:
            self.max: int = max_links
        
        if self.min > self.max:
            raise ValueError(f"Min {self.min} cannot be larger than Max {self.max}.")

    @classmethod
    def from_string(cls, text: str):
        if len(text) == 0:
            return cls()
        match = re.match(r'\{(\d*)?,?(\d*)?\}', text)
        if not match:
            raise ValueError(f"Invalid cardinality: {text}")
        
        min_str, max_str = match.groups()
        min_val = int(min_str) if min_str else None
        max_val = int(max_str) if max_str else None
        if min_val is None and max_val is None:
            raise ValueError(f"Invalid cardinality: {text}")

        if cls._DELIMITER not in text:
            max_val = min_val
        return cls(min_val, max_val)

    def is_in_bounds(self, value: int) -> bool:
        """
        Returns true if the given values is inside the bounds
        of this Cardinality.

        :param value: Input value to check.
        :return: True if inside bounds, False otherwise.
        """
        return self.min <= value <= self.max

    def __repr__(self):
        return f"{{min={self.min}, max={self.max}}}"
    
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Cardinality) and self.min == other.min and self.max == other.max
