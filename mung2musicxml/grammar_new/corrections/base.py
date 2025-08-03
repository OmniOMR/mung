from abc import ABC, abstractmethod
from mung import NotationGraph


class GrammarCorrection(ABC):
    @abstractmethod
    def apply_to_mung(self, graph: NotationGraph):
        pass