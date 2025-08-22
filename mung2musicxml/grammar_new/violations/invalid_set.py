from typing import Self

from .base import GrammarViolation
from ..parts import GrammarEdge, GrammarNode
from ..corrections import GrammarCorrection, AddEdgeCorrection
from ..constants import LinkDirection


class InvalidSetViolation(GrammarViolation):
    def __init__(
            self,
            first: GrammarNode,
            second: GrammarNode,
            other_nodes: list[GrammarNode],
            direction: LinkDirection,
            corrections: list[GrammarCorrection]
            ):
        self.__first = first
        self.__second = second
        self.__other = other_nodes
        self.__direction = direction
        self.__corrections = corrections
    
    @classmethod
    def from_missing_connections(
        cls,
        first: GrammarNode,
        second: GrammarNode,
        missing_nodes: list[GrammarNode],
        direction: LinkDirection
        ) -> Self:
        corrections: list[GrammarCorrection]
        if direction == LinkDirection.OUTLINK:
            corrections = [AddEdgeCorrection(GrammarEdge(first, x)) for x in missing_nodes]
        elif direction == LinkDirection.INLINK:
            corrections = [AddEdgeCorrection(GrammarEdge(x, first)) for x in missing_nodes]
        else:
            raise ValueError()
        return cls(first, second, missing_nodes, direction, corrections)
        
    @property
    def affected_edges(self) -> list[GrammarEdge]:
        return []

    @property
    def affected_nodes(self) -> list[GrammarNode]:
        return [self.__first, self.__second]

    @property
    def corrections(self) -> list[GrammarCorrection]:
        return self.__corrections

    @property
    def message(self) -> str:
        return (
            f"Symbol {self.__first} and {self.__second} should have {self.__direction.value}links to the same subset of nodes: "
            f"{', '.join(set([x.symbol.name for x in self.__other]))}. "
            f"Symbol {self.__first} is missing connections to symbols: {', '.join([str(x.id) for x in self.__other])}."
        )