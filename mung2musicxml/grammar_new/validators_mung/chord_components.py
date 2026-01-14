from typing import TypeVar
from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C, InferenceEngineConstants

from ..violations import InvalidSetViolation, GrammarViolation
from ..parts import GrammarNode
from ..constants import LinkDirection


T = TypeVar("T")


class ChordComponentValidator:
    _CLASSES_TO_CHECK = [
        *InferenceEngineConstants.FLAGS_AND_BEAMS,
        C.Tuplets.TUPLET,
        C.Dynamics.DYNAMIC_CRESCENDO_HAIRPIN,
        C.Dynamics.DYNAMIC_DIMINUENDO_HAIRPIN,
        C.Spanners.SLUR
        ]

    def __init__(self) -> None:
        pass
    
    def find_invalid(self, graph: NotationGraph) -> list[GrammarViolation]:
        chords = self._get_unambiguous_chords(graph)
        violations = []
        for chord in chords:
            violations.extend(self._check_chord(chord, graph))
        return violations


    def _has_single_stem(self, notehead: Node, graph: NotationGraph) -> bool:
        return len(graph.children(notehead, class_filter=C.NoteheadAttachments.STEM)) == 1
    
    def _single_stem_noteheads_from_stem(self, stem: Node, graph: NotationGraph) -> list[Node]:
        return [x for x in graph.parents(stem, class_filter=InferenceEngineConstants.NOTEHEAD_CLASS_NAMES) if self._has_single_stem(x, graph)]

    def _get_unambiguous_chords(self, graph: NotationGraph) -> list[list[Node]]:
        """
        Returns a list of chords, list of list of nodes, that are unambiguous. 
        Any notehead with multiple stems is removed from the chord.
        """
        stems = graph.filter_vertices(C.NoteheadAttachments.STEM)
        chords: list[list[Node]] = []
        for stem in stems:
            chords.append(self._single_stem_noteheads_from_stem(stem, graph))
        
        return chords
    
    @staticmethod
    def _get_missing(first: list[T], second: list[T]) -> list[T]:
        """
        Returns a list of Nodes inside ``first`` that are missing in ``second``.

        Example:

        >>> _get_missing([1, 2, 3], [3, 4, 5])
        [1, 2]
        """
        return [x for x in first if x not in second]
    
    def _create_violation_report(self, first: Node, second: Node, missing_connections: list[Node]) -> InvalidSetViolation:
        return InvalidSetViolation.from_missing_connections(
                GrammarNode.from_mung(first),
                GrammarNode.from_mung(second),
                [GrammarNode.from_mung(x) for x in missing_connections],
                LinkDirection.OUTLINK
                )
    
    def _crosscheck_two_noteheads(self, first: Node, second: Node, graph: NotationGraph) -> list[GrammarViolation]:
        first_components = graph.children(first, class_filter=self._CLASSES_TO_CHECK)
        second_components = graph.children(second, class_filter=self._CLASSES_TO_CHECK)

        first_missing = self._get_missing(second_components, first_components)
        second_missing = self._get_missing(first_components, second_components)

        violations = []
        if len(first_missing) > 0:
            violations.append(self._create_violation_report(first, second, first_missing))
        if len(second_missing) > 0:
            violations.append(self._create_violation_report(second, first, second_missing))
        
        return violations
    
    def _check_chord(self, chord: list[Node], graph: NotationGraph) -> list[GrammarViolation]:
        if len(chord) < 2:
            return []
        
        violations = []
        for index in range(len(chord) - 1):
            first = chord[index]
            for i in range(index + 1, len(chord)):
                second = chord[i]
                violations.extend(self._crosscheck_two_noteheads(first, second, graph))
        
        return violations