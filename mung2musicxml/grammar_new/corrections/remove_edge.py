from mung import NotationGraph
from dataclasses import dataclass

from .base import GrammarCorrection
from ..parts import GrammarEdge
from ...logger import logger

@dataclass(frozen=True)
class RemoveEdgeCorrection(GrammarCorrection):
    edge: GrammarEdge

    def apply_to_mung(self, graph: NotationGraph):
        graph.remove_edge(self.edge.from_node.id, self.edge.to_node.id)
        logger.info(
            f"Removing edge {self.edge.from_node.id} -> {self.edge.to_node.id} based on GrammarCorrection."
        )