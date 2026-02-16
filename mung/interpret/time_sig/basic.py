from typing import Optional

from ...graph import Node, NotationGraph
from ...constants import ClassNameConstants as C
from .time_signature_interpreter import (
    TimeSignatureInterpreter,
    TimeSigStruct
)
from ..utils import precedence_graph_sort
T = C.TimeSignatures


def digits_to_time_signature(digits: list[int]) -> Optional[tuple[int, int]]:
    """
    Advanced time signature parser with better heuristics.
    Tries to match denominators with `[1, 2, 4, 8, 16, 32, 64]`,
    but prefers `[2, 4, 8]`.

    :param digits: List of integers representing digits
    :return: (numerator, denominator) or None if invalid
    """
    if not digits or len(digits) < 2:
        return None

    valid_denominators = {1, 2, 4, 8, 16, 32, 64}
    preferred_denominators = {2, 4, 8}
    best_match = None

    def slice_to_int(ds: list[int]) -> int:
        value = 0
        for d in ds:
            value = value * 10 + d
        return value

    # Try all possible splits
    for i in range(1, len(digits)):
        num_digits = digits[:i]
        den_digits = digits[i:]

        # Reject leading zeros (except single-digit zero, which we don't want anyway)
        if len(num_digits) > 1 and num_digits[0] == 0:
            continue
        if len(den_digits) > 1 and den_digits[0] == 0:
            continue

        numerator = slice_to_int(num_digits)
        denominator = slice_to_int(den_digits)

        if numerator <= 0 or denominator not in valid_denominators:
            continue

        # Prefer common time signatures immediately
        if denominator in preferred_denominators:
            return (numerator, denominator)

        # Otherwise keep first valid fallback
        if best_match is None:
            best_match = (numerator, denominator)

    return best_match


class BasicTimeSignatureInterpreter(TimeSignatureInterpreter):
    """
    Basic interpreter:
    - Recognizes (cut) common time, single digit.
    - Any two nodes are interpreted as a fraction.
    - Time signature with a slash is interpreted as a fraction of number-before-slash / number-after-slash.
    - If all are numbers, the `digits_to_time_signature` algorithm is used to find the best match.
    """
    def _interpret_impl(self, container: Node, graph: NotationGraph) -> Optional[TimeSigStruct]:
        children = graph.children(container, class_filter=C.TimeSignatures.ALL())
        if len(children) == 0:
            return None

        # common, or cut common, or single digit
        if len(children) == 1:
            symbol = children[0]
            if symbol.class_name == T.TIME_SIG_COMMON:
                return TimeSigStruct(4, 4, is_common=True)
            elif symbol.class_name == T.TIME_SIG_CUT_COMMON:
                return TimeSigStruct(2, 2, is_common_cut=True)
            # suppose x/4 time signature, for a single number x
            else:
                return TimeSigStruct(self.interpret_single_number(symbol), 4, is_single_number=True)
        
        # two numbers
        elif len(children) == 2:
            # decide if digits are aligned left-right or top-bottom
            #  3
            #  -   or   3 | 4   
            #  4
            #
            # sort them left-right, or top-bottom
            if abs(children[0].vertical_center - children[1].vertical_center) > abs(children[0].horizontal_center - children[1].horizontal_center):
                # the top-down direction is more informative
                children.sort(key=lambda c: c.top)
            else:
                children.sort(key=lambda c: c.left)
            
            return TimeSigStruct(
                T(children[0].class_name).to_digit(),
                T(children[1].class_name).to_digit()
            )
        
        # numbers with slash
        elif any(c.class_name == T.TIME_SIG_SLASH for c in children):
            assert sum(1 for c in children if c.class_name == T.TIME_SIG_SLASH) == 1

            children = precedence_graph_sort(children, graph)
            print("sorted graph", children)
            slash_index = -1
            for i, c in enumerate(children):
                if c.class_name == T.TIME_SIG_SLASH:
                    slash_index = i
                    break
            assert slash_index != -1 and slash_index != 0 and slash_index != len(children) - 1

            numerator_nodes = children[:slash_index]
            denominator_nodes = children[slash_index + 1:]

            return TimeSigStruct(
                numerator=self.interpret_number(numerator_nodes),
                denominator=self.interpret_number(denominator_nodes),
                has_slash=True
            )
        
        # all are numbers
        elif all(c.class_name in self._all_numbers for c in children):
            children = precedence_graph_sort(children, graph)
            print("sorted graph", children)
            res = digits_to_time_signature([self.interpret_single_number(c) for c in children])
            if res is not None:
                return TimeSigStruct(res[0], res[1])
        
        raise ValueError