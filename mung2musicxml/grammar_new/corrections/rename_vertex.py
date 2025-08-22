from mung import NotationGraph
from dataclasses import dataclass

from .base import GrammarCorrection
from ..parts import GrammarNode
from ...logger import logger


@dataclass(frozen=True)
class RenameVertexCorrection(GrammarCorrection):
    node: GrammarNode
    new_name: str

    def apply_to_mung(self, graph: NotationGraph):
        graph[self.node.id].set_class_name(self.new_name)
        logger.info(
            f"Renamed vertex {self.node.id} to {self.new_name} based on GrammarCorrection."
        )
