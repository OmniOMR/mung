from mung import NotationGraph

from .grammar import Grammar
from .deprules import SYNTAX_GRAMMAR_DEPRULES_TEXT, PRECEDENCE_GRAMMAR_DEPRULES_TEXT, GRAMMAR_ALPHABET
from .violations import GrammarViolation


class NotationGraphGrammarWrapper:
    """
    Dependency grammar wrapper for use with MuNG Notation Graph.

    Automatically loads all the necessary files -
    syntax and precedence rule and alphabet.
    """
    def __init__(self):
        self._syntax = Grammar.from_text(SYNTAX_GRAMMAR_DEPRULES_TEXT, GRAMMAR_ALPHABET)
        self._precedence = Grammar.from_text(PRECEDENCE_GRAMMAR_DEPRULES_TEXT, GRAMMAR_ALPHABET)
        pass

    def find_invalid_syntax(self, graph: NotationGraph) -> list[GrammarViolation]:
        return self._syntax.find_invalid(
            {node.id: node.class_name for node in graph.vertices},
            graph.edges
            )
    
    def find_invalid_precedence(self, graph: NotationGraph) -> list[GrammarViolation]:
        return self._precedence.find_invalid(
            {node.id: node.class_name for node in graph.vertices},
            graph.precedence_edges
            )