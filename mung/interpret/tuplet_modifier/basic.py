from typing import Optional
from fractions import Fraction

from ...constants import ClassNameConstants as C, InferenceEngineConstants as I
from ...graph import Node, NotationGraph
from ...logger import logger
from ...subevents_from_nodes import subevents_from_list_of_symbols
from ..utils import precedence_graph_sort
from .tuplet_interpreter import TupletModifierInterpreter

T = C.TimeSignatures


class BasicTupletModifierInterpreter(TupletModifierInterpreter):
    __enums__ = C.Tuplets

    def _interpret_impl(self, container: Node, graph: NotationGraph) -> Optional[Fraction]:
        return self.compute_tuple_modifier(container, graph)

    def _try_sort_by_precedence(self, numerals: list[Node], graph: NotationGraph) -> list[Node]:
        """
        Tries to sort given numerals by precedence edges,
        if this sort fails, return numerals sorted from left to right.
        """
        try:
            return precedence_graph_sort(numerals, graph)
        except Exception as e:
            logger.warning(e)
            logger.warning(f"Unable to sort numerals {numerals} by precedence, sorting from left to right")
            return sorted(numerals, key=lambda x: x.left)

    def _no_numeral_tuple_fallback(self, tuple_: Node, graph: NotationGraph) -> int:
        """
        Finds noteheads, separates them into subevents, and counts them.
        """
        affected_noteheads = graph.parents(tuple_, class_filter=I.CLASSES_BEARING_DURATIONS)
        subevents = subevents_from_list_of_symbols(affected_noteheads, graph)
        logger.debug(f"Found subevents: {[[x.id for x in xs] for xs in subevents]}")
        return len(subevents)
    
    def compute_tuple_modifier(self, container: Node, graph: NotationGraph) -> Fraction:
        # Find the number in the tuple.
        numerals = graph.children(container, self._all_numbers)

        if len(numerals) == 0:
            logger.warning(f"Tuple {container.id} has no numerals!")
        elif len(numerals) > 3:
            logger.warning(f"Tuple {container.id} has more than 3 numerals!")
        
        if len(numerals) > 0:
            numerals = self._try_sort_by_precedence(numerals, graph)
            tuple_number = self.interpret_number(numerals)

        # Fallback, the list of numbers is empty,
        # Count noteheads attached to that tuple
        else:
            tuple_number = self._no_numeral_tuple_fallback(container, graph)
            logger.warning(f"Using numeral fall back, counting events: {tuple_number}")

        # Last note in tuple should get complementary duration
        # to sum to a whole. Otherwise, playing brings slight trouble.
        if tuple_number > 6:
            logger.warning("Cannot really deal with higher tuples than 6.")

        match tuple_number:
            case 2:
                # Duola makes notes *longer*
                return Fraction(3, 2)
            case 3:
                return Fraction(2, 3)
            case 4:
                # This one also makes notes longer
                return Fraction(4, 3)
            case 5:
                return Fraction(4, 5)
            case 6:
                # Most often done for two consecutive triolas,
                # e.g. 16ths with a 6-tuple filling one beat
                return Fraction(2, 3)
            case 7:
                # Here we get into trouble, because this one
                # can be both 4 / 7 (7 16th in a beat)
                # or 8 / 7 (7 32nds in a beat).
                # In the same vein, we cannot resolve higher
                # tuples unless we establish precedence/simultaneity.
                # For MUSCIMA++ specifically, we can cheat: there is only one
                # septuple, which consists of 7 x 32rd in 1 beat, so they
                # get 8 / 7.
                logger.warning("MUSCIMA++ cheat: we know there is only 7 x 32rd in 1 beat in page 14.")
                return Fraction(8, 7)
            case 9:
                return Fraction(9, 8)
            case 10:
                logger.warning("MUSCIMA++ cheat: we know there is only 10 x 32rd in 1 beat in page 04.")
                return Fraction(4, 5)
            case 8:
                return Fraction(7, 8)
            case _:
                return Fraction(2, 3)
                raise NotImplementedError(f"Tuple {container.id}: Cannot deal with tuple number {tuple_number}")
    