from enum import Enum
from typing import Self
from dataclasses import dataclass, field

from ..parts import Cardinality
from ..symbol import Symbol
from ..constants import GrammarConstants

class _RuleSideGroupType(Enum):
    ATOMIC = "atomic"
    ANYOF = "anyof"
    EXACTLYONE = "exactlyone"

    @classmethod
    def from_str(cls, input_str: str) -> Self:
        input_str = input_str.lower()
        for e in cls:
            if e.value == input_str:
                return e
        
        raise ValueError(f"Unknown input string '{input_str}'")

@dataclass(frozen=True)
class _RuleSideGroup:
    """
    Holds information about a Left or Right side of a given rule
    immediately after parsing.
    """
    type: _RuleSideGroupType = _RuleSideGroupType.ATOMIC
    symbols: list[Symbol] = field(default_factory=lambda: [GrammarConstants.ANY_SYMBOL])
    cardinality: Cardinality = field(default_factory=Cardinality)

    def __post_init__(self):
        if self.type == _RuleSideGroupType.ATOMIC and len(self.symbols) > 1:
            raise ValueError("Does not support grouping outside of special token groups.")
        if len(self.symbols) == 0:
            raise ValueError("Has to have at least one class name specified.")
