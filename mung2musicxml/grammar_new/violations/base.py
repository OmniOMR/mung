from abc import ABC, abstractmethod

from mung import NotationGraph
from ..parts import GrammarEdge, GrammarNode
from ..corrections import GrammarCorrection


class GrammarViolation(ABC):
    @property
    @abstractmethod
    def message(self) -> str:
        pass

    @property
    @abstractmethod
    def affected_edges(self) -> list[GrammarEdge]:
        pass

    @property
    @abstractmethod
    def affected_nodes(self) -> list[GrammarNode]:
        pass

    @property
    @abstractmethod
    def corrections(self) -> list[GrammarCorrection]:
        pass

    def __str__(self) -> str:
        return f"{self.message} Suggested corrections: {[str(c) for c in self.corrections]}"

    def apply_corrections_to_mung(self, graph: NotationGraph):
        for correction in self.corrections:
            correction.apply_to_mung(graph)