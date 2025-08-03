from ..base import TokenizedRule
from ...symbol import Symbol
from ...parts import GrammarNode, _GrammarDefaultDict


class ExactlyOneRule(TokenizedRule):
    _TOKEN_NAME = "EXACTLYONE"

    @staticmethod
    def _only_one_nonzero(nums: list[int]) -> bool:
        return sum(1 for n in nums if n != 0) == 1

    @staticmethod
    def _all_zeros(nums: list[int]) -> bool:
        return all(n == 0 for n in nums)

    def _is_valid_check_impl(
        self,
        node: GrammarNode,
        node_links: _GrammarDefaultDict[Symbol, list[GrammarNode]],
    ) -> bool:
        checked_symbols_counts = [len(node_links[cs]) for cs in self.output_classes]

        # Edge case where we allow ZERO connections
        if self._all_zeros(checked_symbols_counts) and self.cardinality.min == 0:
            return True

        # There are more classes with at least one instance
        if not self._only_one_nonzero(checked_symbols_counts):
            return False

        # There are instances of exactly one class, check cardinality
        max_count = max(checked_symbols_counts)
        return self.cardinality.is_in_bounds(max_count)
