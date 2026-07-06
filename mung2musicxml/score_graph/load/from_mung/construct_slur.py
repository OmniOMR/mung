from typing import Optional

from mung import Node, NotationGraph
from mung.constants import InferenceEngineConstants as I
from mung.graph import (
    infer_vertical_object_placement_relative_to_notes,
    infer_horizontal_object_placement_relative_to_notes
)

from ...graph import *
from ....logger import logger
from .collector import needs_graph


@needs_graph
def construct_slur(
        mung_slur: Node,
        subevents: list[Subevent],
        graph: NotationGraph
) -> Optional[Slur]:
    """
    Slurs is connected to the earliest and the latest two subevents.
    If there are multiple subevents at the start or the end,
    single start and stop subevents are chosen based on a computed
    `PlacementToken`.

    Creates slurs with only start or only stop,
    even though MusicXML does not support them.
    """
    assert len(subevents) > 0, f"No subevents for {mung_slur}"
    
    if graph.has_parents(mung_slur, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES):
        logger.warning(f"{mung_slur} contains grace notes, skipping")
        return None
    
    subevents.sort(key=lambda s: s.global_fractional_onset)

    placement = AboveBelowToken.from_int(infer_vertical_object_placement_relative_to_notes(mung_slur, graph))
    if placement == AboveBelowToken.ABOVE:
        # find the topmost subevent: lowest voice id and lowest staff id
        start = min(subevents, key=lambda s: (s.global_fractional_onset, s.voice.id, min(x.id for x in s.staffs)))
        stop = min(subevents, key=lambda s: (-s.global_fractional_onset, s.voice.id, min(x.id for x in s.staffs)))
    else:
        # find the bottom most subevent: highest voice id and highest staff id
        start = min(subevents, key=lambda s: (s.global_fractional_onset, -s.voice.id, max(x.id for x in s.staffs)))
        stop = min(subevents, key=lambda s: (-s.global_fractional_onset, -s.voice.id, max(x.id for x in s.staffs)))
    
    unique_onsets = set(x.global_fractional_onset for x in subevents)

    # only start (or stop)
    if len(unique_onsets) == 1:
        # the only durable connected to the slur should be start or stop
        hor = infer_horizontal_object_placement_relative_to_notes(mung_slur, graph)
        # the slur is on the right from the durable
        if hor < 0:
            return Slur(
                start=start,
                stop=None,
                placement=placement,
            )
        # the slur is on the left from the durable
        else:
            return Slur(
                start=None,
                stop=start,
                placement=placement
            )
    
    # both start and stop were found
    else:
        continue_ = [x for x in subevents if (x != start and x != stop)]
        if len(continue_) == 0:
            continue_ = None
        
        return Slur(
            start=start,
            continue_=continue_,
            stop=stop,
            placement=placement,
        )
