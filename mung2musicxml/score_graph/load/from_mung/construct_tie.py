from typing import Optional
from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes
from mung.constants import InferenceEngineConstants as I

from ....logger import logger
from ...graph import *
from .collector import needs_graph
from .utils import get_durable_pitch
from .construct_slur import construct_slur


@needs_graph
def try_construct_tie(mung_tie: Node, durables: list[Durable], graph: NotationGraph) -> Optional[Slur | Tie]:
    """
    A slur might be misclassified as a tie, in which case,
    it might happen that the connected noteheads differ in pitch.
    A tie constructed for these noteheads would be invalid.

    The method first tries to construct a tie and if it fails,
    it creates a slur.
    """
    
    if graph.has_parents(mung_tie, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES):
        logger.warning(f"{mung_tie} contains grace notes, skipping")
        return None
    
    unique_onsets = set(d.global_fractional_onset for d in durables)
    unique_pitches = set(d.pitch for d in durables if isinstance(d, Note))
    
    def _slur_from_tie_input(mung_tie: Node, durables: list[Durable], graph: NotationGraph) -> Optional[Slur | Tie]:
        return construct_slur(mung_tie, list(set(d.subevent for d in durables)), graph)
    
    # invalid tie specification, outputting as slur
    if len(unique_onsets) > 2 or len(unique_pitches) > 1:
        if len(unique_onsets) > 2:
            logger.warning(f"Too many onsets for tie {mung_tie}, {unique_onsets}, has to be at most 2, processing as {Slur.__name__}")
        if len(unique_pitches) > 1:
            logger.warning(f"Too many pitches for tie {mung_tie}, {[p.to_tuple_repr() for p in unique_pitches]}, has to be at most 1, processing as {Slur.__name__}")
        
        return _slur_from_tie_input(mung_tie, durables, graph)
    
    placement = AboveBelowToken.from_int(infer_vertical_object_placement_relative_to_notes(mung_tie, graph))
    
    if placement == AboveBelowToken.ABOVE:
        # minimizing:
        #  - onset (minimal onset wanted)
        #  - note/rest (minimizing for notes (0))
        #  - -pitch (minimizing midi pitch)
        start = min(durables, key=lambda d: (d.global_fractional_onset, not isinstance(d, Note), -get_durable_pitch(d)))
    else:
        # same as above but lowest pitch first
        start = min(durables, key=lambda d: (d.global_fractional_onset, not isinstance(d, Note), get_durable_pitch(d)))


    if len(unique_onsets) == 1:
        return Tie(
            start=start,
            placement=placement
        )
    
    stop_onset = max(unique_onsets)

    # try match start with stop based on pitch
    possible_stops = [
        d for d in durables
        if (
            isinstance(d, Rest)
            or isinstance(start, Rest)
            or (isinstance(d, Note) and isinstance(start, Note) and d.pitch == start.pitch)
        )
        and d.global_fractional_onset == stop_onset
    ]

    if len(possible_stops) == 0:
        logger.warning(f"Unable to find same pitch notes for {mung_tie}, processing as {Slur.__name__}")
        return _slur_from_tie_input(mung_tie, durables, graph)

    # try match voice
    for stop in possible_stops:
        if stop.voice.id == start.voice.id:
            return Tie(
                start=start,
                stop=stop,
                placement=placement
            )
    
    logger.warning(f"Unable to match voice for {mung_tie}")
    
    return Tie(
        start=start,
        stop=possible_stops[0],
        placement=placement,
    )
