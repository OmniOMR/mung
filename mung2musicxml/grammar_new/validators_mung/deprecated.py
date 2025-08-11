from mung import Node, NotationGraph
from mung.constants import ClassNamesConstants

from ..violations import ClassNameDeprecatedViolation, GrammarViolation
from ..parts import GrammarNode

# !!! Prototype
# Rest of the library still works with "noteheadFull" instead of "noteheadBlack".

class _DeprecatedNames:
    """
    Stores simple one-to-one mapping for deprecated class names
    in a format "old name" : "new name".
    """
    MAPPING = {
        "notehead-full": "noteheadBlack",
        "noteheadFull": "noteheadBlack",
        "repeat1Bar": "repeatOneBar",
        "rest_breve": "restBreve",
        "rest_longa": "restLonga",
        }

class DeprecationValidator(object):
    def _simple_rename_template(
        self, graph: NotationGraph, old_name: str, new_name: str
    ) -> list[GrammarViolation]:
        output = []
        for node in graph.filter_vertices(old_name):
            output.append(ClassNameDeprecatedViolation(GrammarNode.from_mung(node), new_name=new_name))
        return output

    def _notehead_empty(self, graph: NotationGraph) -> list[GrammarViolation]:
        def has_stem(graph: NotationGraph, node: Node) -> bool:
            return (
                len(graph.children(node, class_filter=ClassNamesConstants.STEM)) > 0
            )

        output = []
        for node in graph.filter_vertices(["noteheadEmpty", "notehead-empty"]):
            output.append(
                ClassNameDeprecatedViolation(
                    GrammarNode.from_mung(node),
                    new_name=ClassNamesConstants.NOTEHEAD_HALF
                    if has_stem(graph, node)
                    else ClassNamesConstants.NOTEHEAD_WHOLE,
                )
            )
        return output

    def find_invalid(self, graph: NotationGraph) -> list[GrammarViolation]:
        """
        Iterates through all nodes of the given graph.
        Returns list of deprecation warnings.
        """
        output = []
        for old_name, new_name in _DeprecatedNames.MAPPING.items():
            output += self._simple_rename_template(graph, old_name, new_name)
        
        output += self._notehead_empty(graph)
        return output