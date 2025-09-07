from mung import Node
from typing import Self

from .base import GrammarViolation
from ..parts import GrammarEdge, GrammarNode
from ..corrections import GrammarCorrection


class MissingRelationViolation(GrammarViolation):
    def __init__(self, first: GrammarNode, second: GrammarNode):
        self._first = first
        self._second = second
    
    @classmethod
    def from_mung(cls, first: Node, second: Node) -> Self:
        return cls(
            GrammarNode.from_mung(first),
            GrammarNode.from_mung(second)
            )

    @property
    def affected_edges(self) -> list[GrammarEdge]:
        return []

    @property
    def affected_nodes(self) -> list[GrammarNode]:
        return [self._first, self._second]

    @property
    def corrections(self) -> list[GrammarCorrection]:
        return []

    @property
    def message(self) -> str:
        return (
            f"Two symbols: {self._first} and {self._second} should be connected by an edge."
        )