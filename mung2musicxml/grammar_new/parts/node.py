from typing import Self
from dataclasses import dataclass
from mung import Node

from ..symbol import Symbol

@dataclass(frozen=True, eq=True)
class GrammarNode:
    """
    Grammar graph vertex.
    """
    symbol: Symbol
    id: int

    def __str__(self) -> str:
        return f"{self.id} (\"{self.symbol.name}\")"
    
    @classmethod
    def from_mung(cls, node: Node) -> Self:
        return cls(symbol=Symbol(node.class_name), id=node.id)