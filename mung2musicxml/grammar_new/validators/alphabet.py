from ..parts import GrammarNode
from ..symbol import Symbol
from ..violations import GrammarViolation, SymbolNotInAlphabetViolation


class AlphabetValidator:
    def __init__(self, alphabet: list[Symbol] | set[Symbol]):
        self._alphabet = set(alphabet)

    @property
    def alphabet(self) -> set[Symbol]:
        return self._alphabet

    def find_invalid(self, nodes: list[GrammarNode]) -> list[GrammarViolation]:
        """
        Checks names of given Nodes against its alphabet.
        If node's name is not inside the alphabet,
        creates a ``GrammarViolation`` instance.

        :param nodes: List of ``GrammarNode``s to check.
        :return: List of all alphabet grammar violations found.
        """
        violations: list[GrammarViolation] = []

        for node in nodes:
            if node.symbol not in self._alphabet:
                violations.append(SymbolNotInAlphabetViolation(node))

        return violations
