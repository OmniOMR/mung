from .base import GrammarViolation
from ..parts import GrammarEdge, GrammarNode
from ..corrections import GrammarCorrection, RemoveEdgeCorrection, TurnAroundEdgeCorrection


class EdgeNotInAlphabetViolation(GrammarViolation):
    def __init__(self, edge: GrammarEdge, turn_around: bool = False):
        self.__edge = edge
        if turn_around:
            self.__correction = TurnAroundEdgeCorrection(edge)
        else:
            self.__correction = RemoveEdgeCorrection(edge)

    @property
    def affected_edges(self) -> list[GrammarEdge]:
        return []

    @property
    def affected_nodes(self) -> list[GrammarNode]:
        return [self.__edge.from_node, self.__edge.to_node]

    @property
    def corrections(self) -> list[GrammarCorrection]:
        return [self.__correction]

    @property
    def message(self) -> str:
        return (
            f"Outlink {self.__edge.from_node} -> {self.__edge.to_node} not in alphabet."
        )