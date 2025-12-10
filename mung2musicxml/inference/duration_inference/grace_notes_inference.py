from fractions import Fraction
from mung import NotationGraph, Node
from typing import Optional, Self

from mung.constants import InferenceEngineConstants as I, OnsetDataConstants as O
from mung2midi.inference import OnsetsInferenceStrategy
from ...logger import logger
from .utils import _add_duration_data_to_node


class _GraceGroupWrapper:
    """
    Grace Group is an internal representation for groups
    of grace notes that are children of the same notehead.

    I resolves the ordering of the grace notes.
    Even though grace notes have no duration and no onset,
    internally they have:

    - onset, based on their order, integer from 0 to N-1
    - duration, 0
    - duration without modifiers, 0

    This graph component has to be a path.
    """        
    def __init__(self, notes: list[Node]) -> None:
        self._notes = notes
        self._valid = self._is_valid_graph()
        if not self._valid:
            logger.warning(f"Grace note graph not valid: {', '.join([str(x.id) for x in self._notes])}")
        else:
            logger.debug(f"Grace note graph is valid: {', '.join([str(x.id) for x in self._notes])}")
    
    @staticmethod
    def _sort_with_queue(nodes: list[Node]) -> list[Node]:
        output: list[Node] = []
        q = [x for x in nodes if len(x.precedence_inlinks) == 0 and len(x.precedence_outlinks) == 1]
        assert len(q) == 1
        current = q[0]
        mapping = {x.id: x for x in nodes}

        # traverse the path
        while len(current.precedence_outlinks) > 0:
            output.append(current)
            assert len(current.precedence_outlinks) == 1
            current = mapping[current.precedence_outlinks[0]]
        output.append(current)

        logger.debug(f"Sorted to: {[x.id for x in output]}")

        assert len(nodes) == len(output)
        return output
    
    @staticmethod
    def _sort_left_to_right(nodes: list[Node]) -> list[Node]:
        # There is no way to represent polyphonic grace notes in MusicXML,
        # in the end we are sorting them from left to right anyway.
        return sorted(nodes, key=lambda x: x.left)

    def _sort(self):
        """
        Sorts contained grace notes into order
        in which they should appear in an MusicXML outputs.

        If the graph is valid, defined by the notes,
        the notes are sorted based on precedence linkage,
        the graph is a path.
        If the graph is not valid, the notes are simply sorted
        from left to right based on their image coordinates.
        """
        if self._valid:
            self._notes = self._sort_with_queue(self._notes)
        else:
            self._notes = self._sort_left_to_right(self._notes)

    def compute(self, graph: NotationGraph) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        self._sort()
        onsets, durations, durations_wo_m = dict(), dict(), dict()
        for i, note in enumerate(self._notes):
            onsets[note.id] = Fraction(i)
            mod = len(graph.children(note, class_filter=I.FLAGS_AND_BEAMS))
            duration = Fraction(1) if note.class_name == I.NOTEHEAD_FULL_SMALL else Fraction(2)
            if mod > 0:
                duration = duration * Fraction(1, 2 ** mod)
            durations[note.id] = duration
            durations_wo_m[note.id] = duration
                
        for node in self._notes:
            _add_duration_data_to_node(
                node, durations[node.id], durations_wo_m[node.id]
            )
            node.data[O.ONSET_BEATS] = onsets[node.id]
        
        return onsets, durations, durations_wo_m

    @classmethod
    def compute_multiple(cls, groups: list[Self], graph: NotationGraph) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        onsets, durations, durations_wo_m = dict(), dict(), dict()
        for g in groups:
            o, d, w = g.compute(graph)
            onsets |= o
            durations |= d
            durations_wo_m |= w
        
        return onsets, durations, durations_wo_m

    def _is_valid_graph(self) -> bool:
        # graph is a path
        # - one source,
        # - one sink,
        # - all other have to have one inlink a one outlink
        source, sink = 0, 0
        for note in self._notes:
            if len(note.precedence_inlinks) == 0 and len(note.precedence_outlinks) == 1:
                source += 1
                if source > 1:
                    return False
            elif len(note.precedence_inlinks) == 1 and len(note.precedence_outlinks) == 0:
                sink += 1
                if sink > 1:
                    return False
            elif len(note.precedence_inlinks) == 1 and len(note.precedence_outlinks) == 1:
                pass
            else:
                return False
        return True

    @classmethod
    def from_graph(cls, graph: NotationGraph) -> list[Self]:
        output: list[Self] = []
        for notehead in graph.filter_vertices(I.NONGRACE_NOTEHEAD_CLASS_NAMES):
            grace = graph.children(notehead, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES)
            if len(grace) > 0:
                output.append(cls(grace))
        return output


class _GraceOnsetInference:
    """
    Computes the ordering of grace notes within each group -
    grace notes that are linked to the same notehead.
    """
    def __init__(self, strategy: Optional[OnsetsInferenceStrategy] = None):
        if strategy is None:
            strategy = OnsetsInferenceStrategy()
        self._strategy = strategy
    
    def __call__(
            self,
            graph: NotationGraph
        ) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        ggw = _GraceGroupWrapper.from_graph(graph)
        logger.info(f"We have {len(ggw)} grace note groups")
        return _GraceGroupWrapper.compute_multiple(ggw, graph)
