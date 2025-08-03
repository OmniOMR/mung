from .base import GrammarViolation
from ..parts import GrammarEdge, GrammarNode
from ..constants import LinkDirection
from ..corrections import GrammarCorrection


class InvalidLinkCountViolation(GrammarViolation):
    def __init__(
        self,
        direction: LinkDirection,
        other_nodes: list[GrammarNode],
        root_node: GrammarNode,
        output_classes: list[str],
        rule_repre: str,
    ):
        self.__other_nodes = other_nodes
        self.__root_node = root_node

        if direction == LinkDirection.INLINK:
            self.__edges = [GrammarEdge(on, root_node) for on in other_nodes]
        elif direction == LinkDirection.OUTLINK:
            self.__edges = [GrammarEdge(root_node, on) for on in other_nodes]
        else:
            raise ValueError()

        self.__rule_repre = rule_repre
        self.__output_classes = output_classes
        self.__direction = direction        

    @property
    def affected_edges(self) -> list[GrammarEdge]:
        return self.__edges

    @property
    def affected_nodes(self) -> list[GrammarNode]:
        return [self.__root_node] + self.__other_nodes

    @property
    def corrections(self) -> list[GrammarCorrection]:
        return []

    @property
    def message(self) -> str:
        return (
            f"Symbol {self.__root_node} has {len(self.__other_nodes)} {self.__direction.value}links to {self.__output_classes}, "
            f"but grammar specifies rule: {self.__rule_repre}. "
            f"Affected nodes: {self.__root_node.id}; {[x.id for x in self.__other_nodes]}."
        )
