from ..parts import GrammarNode, _GrammarDefaultDict
from ..symbol import Symbol
from ..constants import LinkDirection
from ..violations import GrammarViolation
from ..rules import GrammarRule


class CardinalityValidator:
    """
    Holds and runs checks again a given list of ``GrammarRule``s.
    """
    def __init__(self, rules: list[GrammarRule]):
        self._inlink_rules, self._outlink_rules = self._setup_rules(rules)

    @staticmethod
    def _setup_rules(rules: list[GrammarRule]):
        """
        Sorts rules by direction and input class.
        """
        inlinks: _GrammarDefaultDict[Symbol, list[GrammarRule]] = _GrammarDefaultDict(
            lambda: list()
        )
        outlinks: _GrammarDefaultDict[Symbol, list[GrammarRule]] = _GrammarDefaultDict(
            lambda: list()
        )

        for rule in rules:
            if rule.direction == LinkDirection.INLINK:
                inlinks[rule.input_class].append(rule)
            elif rule.direction == LinkDirection.OUTLINK:
                outlinks[rule.input_class].append(rule)
            else:
                raise ValueError()

        return inlinks, outlinks

    @staticmethod
    def _find_invalid_template(
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
        rules: list[GrammarRule],
    ) -> list[GrammarViolation]:
        violations: list[GrammarViolation] = []

        for rule in rules:
            violations += rule.find_invalid(node, node_links)

        return violations

    def find_invalid_inlinks(
        self,
        node: GrammarNode,
        node_inlinks: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> list[GrammarViolation]:
        """
        Returns a list of ``GrammarViolations`` that denote
        which rules were violated by the given node and its counts.
        """
        rules = self._inlink_rules[node.symbol]
        return self._find_invalid_template(node, node_inlinks, rules)

    def find_invalid_outlinks(
        self,
        node: GrammarNode,
        node_outlinks: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> list[GrammarViolation]:
        """
        Returns a list of ``GrammarViolations`` that denote
        which rules were violated by the given node and its counts.
        """
        rules = self._outlink_rules[node.symbol]
        return self._find_invalid_template(node, node_outlinks, rules)

