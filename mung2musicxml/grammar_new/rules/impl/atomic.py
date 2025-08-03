from ..base import GrammarRule
from ...constants import LinkDirection, GrammarConstants
from ...parts import Cardinality, EdgeSignature, GrammarNode, _GrammarDefaultDict
from ...symbol import Symbol
from ...violations import InvalidLinkCountViolation, GrammarViolation

class AtomicRule(GrammarRule):
    """
    Atomic rule has and optional left side and optional right side (at least one has to be present).

        LHS | RHS

    The rule is split, while parsing, into an equivalent representation using the atomic rules:

        noteheadFull{1,2} | stem{1,}

    Becomes:

        noteheadFull{1,2} | stem    # (represented as: noteheadFull -> stem {min=1, max=2})
        noteheadFull | stem{1,}     # (represented as: stem <- noteheadFull {min=1, max=inf})

    This makes for easier implementation as we always check from left-to-right
    in the inner grammar representation.
    """

    def __init__(
        self,
        input_class: Symbol,
        output_class: Symbol,
        cardinality: Cardinality,
        direction: LinkDirection,
    ):
        self.__input_class = input_class
        self.output_class = output_class
        self.cardinality = cardinality
        self.__direction = direction
    
    @property
    def direction(self) -> LinkDirection:
        return self.__direction
    
    @property
    def input_class(self) -> Symbol:
        return self.__input_class

    def edge_signatures(self) -> list[EdgeSignature]:
        if self.direction == LinkDirection.INLINK:
            return [EdgeSignature(self.output_class, self.input_class)]
        elif self.direction == LinkDirection.OUTLINK:
            return [EdgeSignature(self.input_class, self.output_class)]

        raise ValueError(f"Unknown LinkDirection: {self.direction}")

    def find_invalid(
        self,
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> list[GrammarViolation]:
        checked_symbol = self.output_class
        checked_symbol_count = len(node_links[checked_symbol])
        if not self.cardinality.is_in_bounds(checked_symbol_count):
            return [
                InvalidLinkCountViolation(
                    root_node=node,
                    other_nodes=node_links[checked_symbol],
                    direction=self.direction,
                    output_classes=[checked_symbol.name],
                    rule_repre=str(self),
                )
            ]

        return []

    def __repr__(self) -> str:
        if self.direction == LinkDirection.INLINK:
            return f"{self.output_class} {GrammarConstants.RULE_DELIMITER} {self.input_class}{self.cardinality}"
        elif self.direction == LinkDirection.OUTLINK:
            return f"{self.input_class}{self.cardinality} {GrammarConstants.RULE_DELIMITER} {self.output_class}"
        raise ValueError()