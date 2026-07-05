from fractions import Fraction
from typing import Optional, Self

from mung import NotationGraph, Node
from mung.constants import InferenceEngineConstants as I, OnsetDataConstants as O, ClassNameConstants as C
from mung2midi.inference import OnsetsInferenceStrategy

from ...logger import logger
from .utils import _add_duration_data_to_node
from ...utils import topological_sort


class _GraceGroupWrapper:
    """
    Grace Group is an internal representation for groups
    of grace notes that are children of the same notehead.

    I resolves the ordering of the grace notes.
    Even though grace notes have no duration and no onset,
    internally they have:

    - onset, based on their order, integer from 0 to N-1
    - duration, corresponds to notehead type
    - duration without modifiers, same as duration

    This graph component has to be a DAG.
    """        
    def __init__(self, notes: list[Node]) -> None:
        self._notes = notes
        
    def _sort(self):
        """
        Sorts contained grace notes into order
        in which they should appear in an MusicXML outputs.
        """
        self._notes.sort(key=lambda n: n.left)
        self._notes = topological_sort(self._notes, lambda p, c: c.id in p.precedence_outlinks)

    def compute(self, graph: NotationGraph) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        """
        Sorts grace noteheads and computes their onsets and durations.
        
        Duration is computed the same as for regular noteheads,
        only skipping time modifiers, i.e. tuplets.
        
        Onsets are whole numbers, independent of preceding note
        onset and duration. These onsets are used only to further
        down in the pipeline sort the grace notes from left to right,
        as they have no real onset nor duration.
        """
        
        self._sort()
        onsets, durations, durations_wo_m = dict(), dict(), dict()
        for i, note in enumerate(self._notes):
            parents = graph.precedence_parents(note)
            onset = max((p.data[O.ONSET_BEATS] for p in parents), default=Fraction(-1))
            onset += 1
            
            note.data[O.ONSET_BEATS] = onset
            onsets[note.id] = onset
            
            flag_mod = len(graph.children(note, class_filter=I.FLAGS_AND_BEAMS))
            dot_mod = len(graph.children(note, class_filter=C.NoteheadAttachments.AUGMENTATION_DOT))
            
            duration = Fraction(1) if note.class_name == C.Noteheads.NOTEHEAD_BLACK_SMALL else Fraction(2)
            duration = duration * Fraction(1, 2 ** flag_mod)
            if dot_mod > 0:
                duration = duration * (2 - (Fraction(1,2) ** dot_mod))
                
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
