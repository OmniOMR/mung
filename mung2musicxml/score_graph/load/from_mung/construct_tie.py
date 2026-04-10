from typing import Optional
from mung import Node, NotationGraph
from mung.graph import infer_horizontal_object_placement_relative_to_notes

from ....logger import logger
from ...graph import *
from .utils import get_durable_pitch
from .construct_slur import construct_slur


def try_construct_tie(mung_tie: Node, durables: list[Durable], graph: NotationGraph) -> Optional[Slur | Tie]:
    """
    A slur might be misclassified as a tie, in which case,
    it might happen that the connected noteheads differ in pitch.
    A tie constructed for these noteheads would be invalid.

    The method first tries to construct a tie and if it fails,
    it creates a slur.
    """
    unique_onsets = set(d.global_fractional_onset for d in durables)
    unique_pitches = set(d.pitch for d in durables if isinstance(d, Note))
    
    def _slur_from_tie_input(mung_tie: Node, durables: list[Durable], graph: NotationGraph) -> Optional[Slur | Tie]:
        return construct_slur(mung_tie, list(set(d.subevent for d in durables)), graph)
    
    # invalid tie specification, outputting as slur
    if len(unique_onsets) > 2 or len(unique_pitches) > 1:
        if len(unique_onsets) > 2:
            logger.warning(f"Too many onsets for tie, {unique_onsets}, has to be at most 2, processing as {Slur.__name__}")
        if len(unique_pitches) > 1:
            logger.warning(f"Too many pitches for tie, {unique_onsets}, has to be at most 1, processing as {Slur.__name__}")
        
        return _slur_from_tie_input(mung_tie, durables, graph)
    
    placement = AboveBelowToken.from_int(infer_horizontal_object_placement_relative_to_notes(mung_tie, graph))
    
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
    
    # try match start with stop based on pitch
    possible_stops = sorted([
        d for d in durables 
        # find durables that start at the maximal onset and immediately after the start durable
        if (d.in_measure_fractional_onset == max(unique_onsets)
            and start.in_measure_fractional_end_onset == d.in_measure_fractional_onset
            # if durable is Note, check that pitches are the same (if start is Note)
            and (not isinstance(d, Note) or (isinstance(start, Note) and d.pitch == start.pitch))
        )
        # prefer notes over rests
    ], key=lambda d: not isinstance(d, Note))

    if len(possible_stops) == 0:
        logger.warning(f"Unable to find same pitch notes for {mung_tie}, processing as {Slur.__name__}")
        return _slur_from_tie_input(mung_tie, durables, graph)
    
    return Tie(
        start=start,
        stop=possible_stops[0],
        placement=placement,
    )
