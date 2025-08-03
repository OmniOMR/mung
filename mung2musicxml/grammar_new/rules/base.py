from abc import ABC, abstractmethod

from ..parts import (
    EdgeSignature,
    GrammarNode,
    _GrammarDefaultDict,
    Cardinality
)
from ..symbol import Symbol

from ..constants import LinkDirection, GrammarConstants
from ..violations import GrammarViolation, InvalidLinkCountViolation


class GrammarRule(ABC):
    """
    Abstract base class for the Grammar Rule.
    Has an edge signature and can be evaluated.
    """

    @property
    @abstractmethod
    def direction(self) -> LinkDirection:
        """
        The general direction of the rule.
        """
        pass

    @property
    @abstractmethod
    def input_class(self) -> Symbol:
        """
        Name of the class to which the rule is applied.
        """
        pass

    @abstractmethod
    def edge_signatures(self) -> list[EdgeSignature]:
        """
        Edge signature is a directed edge with ``from`` and ``to`` class names
        represented as two ``Symbols``.

        Returns a list of ``EdgeSignature``s that the rule describes.
        """
        pass

    @abstractmethod
    def find_invalid(
        self,
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> list[GrammarViolation]:
        """
        Returns a list of ``GrammarViolations`` based on the rule's cardinality and inputted counts.

        :param node: Root node for which from which the rule is checked.
        :param node_links: Dictionary of other nodes connected to the root node sorted by their class name.
        :return: List of ``GrammarViolation``s.
        """
        pass


class TokenizedRule(GrammarRule):
    _TOKEN_NAME: str

    def __init__(
        self,
        input_class: Symbol,
        output_classes: list[Symbol],
        cardinality: Cardinality,
        direction: LinkDirection,
    ):
        self.__input_class = input_class
        self.output_classes = output_classes
        self.cardinality = cardinality
        self.__direction = direction

        if (
            GrammarConstants.ANY_SYMBOL in output_classes
            or GrammarConstants.ANY_SYMBOL == input_class
        ):
            raise ValueError()
    
    @property
    def direction(self) -> LinkDirection:
        return self.__direction
    
    @property
    def input_class(self) -> Symbol:
        return self.__input_class

    def edge_signatures(self) -> list[EdgeSignature]:
        if self.direction == LinkDirection.INLINK:
            return [
                EdgeSignature(output_class, self.input_class)
                for output_class in self.output_classes
            ]
        elif self.direction == LinkDirection.OUTLINK:
            return [
                EdgeSignature(self.input_class, output_class)
                for output_class in self.output_classes
            ]

        raise ValueError(f"Unknown LinkDirection: {self.direction}")

    @abstractmethod
    def _is_valid_check_impl(
        self,
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> bool:
        pass

    def find_invalid(
        self,
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> list[GrammarViolation]:
        is_valid = self._is_valid_check_impl(node, node_links)
        if not is_valid:
            return [
                InvalidLinkCountViolation(
                    root_node=node,
                    other_nodes=node_links.get_group(self.output_classes),
                    direction=self.direction,
                    output_classes=[x.name for x in self.output_classes],
                    rule_repre=str(self),
                )
            ]

        return []

    def __repr__(self) -> str:
        output_class_names = ", ".join([str(oc) for oc in self.output_classes])
        if self.direction == LinkDirection.INLINK:
            return f"{self._TOKEN_NAME}({output_class_names}) {GrammarConstants.RULE_DELIMITER} {self.input_class}{self.cardinality}"
        elif self.direction == LinkDirection.OUTLINK:
            return f"{self.input_class}{self.cardinality} {GrammarConstants.RULE_DELIMITER} {self._TOKEN_NAME}({output_class_names})"
        raise ValueError()
