from dataclasses import dataclass

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
    
    @property
    def edge_signature(self) -> EdgeSignature:
        return EdgeSignature(self.from_node.symbol, self.to_node.symbol)
    