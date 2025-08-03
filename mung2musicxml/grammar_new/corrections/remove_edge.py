from mung import NotationGraph
from dataclasses import dataclass
import logging

from .base import GrammarCorrection
from ..parts import GrammarEdge


@dataclass(frozen=True)
class RemoveEdgeCorrection(GrammarCorrection):
    edge: GrammarEdge

    def apply_to_mung(self, graph: NotationGraph):
        graph.remove_edge(self.edge.from_node.id, self.edge.to_node.id)
        logging.info(
            f"Removing edge {self.edge.from_node.id} -> {self.edge.to_node.id} based on GrammarCorrection."
        )