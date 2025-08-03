from mung import NotationGraph
from dataclasses import dataclass
import logging

from .base import GrammarCorrection
from ..parts import GrammarEdge


@dataclass(frozen=True)
class AddEdgeCorrection(GrammarCorrection):
    edge: GrammarEdge

    def apply_to_mung(self, graph: NotationGraph):
        graph.add_edge(self.edge.from_node.id, self.edge.to_node.id)
        logging.info(
            f"Adding edge {self.edge.from_node.id} -> {self.edge.to_node.id} based on GrammarCorrection."
        )