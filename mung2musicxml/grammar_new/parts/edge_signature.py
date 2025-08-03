from typing import Self
from dataclasses import dataclass

from ..constants import GrammarConstants
from ..symbol import Symbol


@dataclass(frozen=True, eq=True)
class EdgeSignature:
    """
    Directed relation between two Grammar Symbols.
    """
    from_symbol: Symbol
    to_symbol: Symbol
    
    @classmethod
    def from_str(cls, str_: str, delim: str = "->") -> Self:
        from_name, to_name = str_.split(delim)
        from_name, to_name = Symbol(from_name.strip()), Symbol(to_name.strip())
        return cls(from_name, to_name)
    
    @property
    def is_basic(self) -> bool:
        """
        Returns True, if both ``from`` and ``to`` Symbols are basic -
        they are not "ANY" Symbol.
        """
        return not (self.from_symbol == GrammarConstants.ANY_SYMBOL
                or self.to_symbol == GrammarConstants.ANY_SYMBOL)

    @property
    def turned(self) -> "EdgeSignature":
        return EdgeSignature(self.to_symbol, self.from_symbol)

    def __str__(self) -> str:
        return f"{self.from_symbol} -> {self.to_symbol}"
