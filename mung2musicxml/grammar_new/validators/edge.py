from typing import Self

from ..parts import EdgeSignature, GrammarEdge
from ..constants import GrammarConstants
from ..violations import GrammarViolation, EdgeNotInAlphabetViolation
from ..rules import GrammarRule


class EdgeValidator:
    """
    Holds a list of allowed ``EdgeSignature``s described by the grammar.
    When asked, returns a list of ``GraphViolations`` if any of the inputted
    edges are not found in the list of allowed ones.
    """

    def __init__(self, valid_edges: set[EdgeSignature] | list[EdgeSignature]):
        # Set of Symbols that can have outlink to anything,
        # the edge signature is "Symbol -> ANY".
        self._can_have_any_outlink = {
            edge.from_symbol
            for edge in valid_edges
            if edge.to_symbol == GrammarConstants.ANY_SYMBOL
        }
        # Set of Symbols that can have inlink from anything,
        # the edge signature is "ANY -> Symbol".
        self._can_have_any_inlink = {
            edge.to_symbol
            for edge in valid_edges
            if edge.from_symbol == GrammarConstants.ANY_SYMBOL
        }

        self._valid_edges_basic = {edge for edge in valid_edges if edge.is_basic}

    @classmethod
    def from_rules(cls, rules: list[GrammarRule]) -> Self:
        """
        Retrieves the allowed edges from a list of rules.

        For example:

            noteheadFull{1,2} | stem{1,}

        Allows the edge ``(notehead, stem)`` to exist.
        """
        edges = []
        for rule in rules:
            edges += rule.edge_signatures()

        return cls(set(edges))

    def find_redundant_edge_rules(self) -> list[EdgeSignature]:
        """
        Finds and returns a list of possibly redundant rules based on edge validity.
        """
        redundant: list[EdgeSignature] = []
        for edge in self._valid_edges_basic:
            # If the from or to can have any outlink/inlink,
            # the edge rule is redundant.
            if (
                edge.from_symbol in self._can_have_any_outlink
                or edge.to_symbol in self._can_have_any_inlink
            ):
                redundant.append(edge)
        return redundant

    def _is_valid_any_inlink(self, edge: EdgeSignature) -> bool:
        return edge.to_symbol in self._can_have_any_inlink

    def _is_valid_any_outlink(self, edge: EdgeSignature) -> bool:
        return edge.from_symbol in self._can_have_any_outlink

    def _is_valid_basic(self, edge: EdgeSignature) -> bool:
        return edge in self._valid_edges_basic

    def is_valid_edge(self, edge: EdgeSignature) -> bool:
        """
        Returns True, if inputted edge's existence is allow in the grammar.
        """
        return (
            self._is_valid_any_inlink(edge)
            or self._is_valid_any_outlink(edge)
            or self._is_valid_basic(edge)
        )

    def find_invalid(self, edges: list[GrammarEdge]) -> list[GrammarViolation]:
        """
        Returns a list of ``GrammarViolation``s containing all issues found
        within the given list of edges.
        """
        output = []
        for edge in edges:
            if not self.is_valid_edge(edge.edge_signature):

                output.append(EdgeNotInAlphabetViolation(
                    edge,
                    # Check, if the edge is valid the other way around, if yes, turn it around.
                    # (This is ment to be used with human annotators, not ML models.)
                    turn_around=self.is_valid_edge(edge.edge_signature.turned)
                    ))

        return output
