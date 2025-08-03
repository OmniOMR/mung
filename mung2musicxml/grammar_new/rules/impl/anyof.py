from ..base import TokenizedRule
from ...symbol import Symbol
from ...parts import GrammarNode, _GrammarDefaultDict


class AnyOfRule(TokenizedRule):
    """
    AnyOf rule has and mandatory left side and right side, exactly one of them has to have the "ANYOF" token.

        ANYOF(LHS) | RHS or LHS | ANYOF(RHS)

    The rule is split, while parsing, into a single ``AnyOfRule`` and multiple ``AtomicRules``:

        ANYOF(noteheadFull*, noteheadSmall*){1,2} | stem{1,}

    Becomes, in the inner representation:

        # AnyOf rule
        stem <- ANYOF([noteheadFull, noteheadFullSmall, noteheadHalf, noteheadHalfSmall]) {min=1, max=inf}
        # Atomic rules
        noteheadFull        -> stem {min=1, max=2}
        noteheadFullSmall   -> stem {min=1, max=2}
        noteheadHalf        -> stem {min=1, max=2}
        noteheadHalfSmall   -> stem {min=1, max=2}
    """

    _TOKEN_NAME = "ANYOF"

    def _is_valid_check_impl(
        self,
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> bool:
        return self.cardinality.is_in_bounds(
            len(node_links.get_group(self.output_classes))
        )
