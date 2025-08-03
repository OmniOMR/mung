from .base import GrammarViolation
from ..parts import GrammarEdge, GrammarNode
from ..corrections import GrammarCorrection


class SymbolNotInAlphabetViolation(GrammarViolation):
    def __init__(self, node: GrammarNode):
        self.__node = node

    @property
    def affected_edges(self) -> list[GrammarEdge]:
        return []

    @property
    def affected_nodes(self) -> list[GrammarNode]:
        return [self.__node]

    @property
    def corrections(self) -> list[GrammarCorrection]:
        return []

    @property
    def message(self) -> str:
        return f"Symbol {self.__node} not in alphabet."