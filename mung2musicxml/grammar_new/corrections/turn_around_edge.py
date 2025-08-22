from mung import NotationGraph
from dataclasses import dataclass

from .base import GrammarCorrection
from ..parts import GrammarEdge
from ...logger import logger


@dataclass(frozen=True)
class TurnAroundEdgeCorrection(GrammarCorrection):
    """
    Turns over the given edge
    - deletes the given edge (from, to) an adds and edge (to, from).
    """
    edge: GrammarEdge

    def apply_to_mung(self, graph: NotationGraph):
        graph.remove_edge(self.edge.from_node.id, self.edge.to_node.id)
        graph.add_edge(self.edge.to_node.id, self.edge.from_node.id)
        logger.info(
            f"Turning around edge {self.edge.from_node.id} -> {self.edge.to_node.id} "
            f"to {self.edge.to_node.id} -> {self.edge.from_node.id} based on GrammarCorrection."
        )