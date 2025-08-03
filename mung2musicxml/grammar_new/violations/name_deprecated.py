from typing import Optional

from .base import GrammarViolation
from ..parts import GrammarEdge, GrammarNode
from ..corrections import GrammarCorrection, RenameVertexCorrection


class ClassNameDeprecatedViolation(GrammarViolation):
    def __init__(self, node: GrammarNode, new_name: Optional[str] = None):
        self.__node = node
        self.__new_name = new_name
        if new_name is not None:
            self.__correction = RenameVertexCorrection(node, new_name=new_name)
        else:
            self.__correction = None

    @property
    def affected_edges(self) -> list[GrammarEdge]:
        return []

    @property
    def affected_nodes(self) -> list[GrammarNode]:
        return [self.__node]

    @property
    def corrections(self) -> list[GrammarCorrection]:
        return [self.__correction] if self.__correction is not None else []
    
    @property
    def message(self) -> str:
        if self.__new_name is not None:
            return f"Symbol {self.__node} has deprecated name. Rename to {self.__new_name}"
        else:
            return f"Symbol {self.__node} has deprecated name. Unable to automatically assign new name."
