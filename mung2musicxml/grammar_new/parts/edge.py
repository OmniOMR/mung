from dataclasses import dataclass
from typing import Self
from mung import Node

from .node import GrammarNode
from .edge_signature import EdgeSignature


@dataclass(frozen=True, eq=True)
class GrammarEdge:
    """
    Directed edge between two Grammar Nodes.
    """
    from_node: GrammarNode
    to_node: GrammarNode

    def __str__(self) -> str:
        return f"{self.from_node} -> {self.to_node}"

    @classmethod
    def from_mung(cls, from_node: Node, to_node: Node) -> Self:
        return cls(GrammarNode.from_mung(from_node), GrammarNode.from_mung(to_node))
    
    @property
    def edge_signature(self) -> EdgeSignature:
        return EdgeSignature(self.from_node.symbol, self.to_node.symbol)
    