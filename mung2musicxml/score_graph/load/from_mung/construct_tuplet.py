from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes
from mung.constants import (
    ClassNameConstants as C,
    InferenceEngineConstants as I
)

from ...graph import *
from .utils import get_tuple_time_modification


def construct_tuplet(mung_tuplet: Node, subevents: list[Subevent], graph: NotationGraph) -> Tuplet:
    assert len(subevents) > 0, f"No subevents for {mung_tuplet}"
    subevents.sort(key=lambda s: s.global_fractional_onset)
    
    def _has_number(mung_tuplet: Node, graph: NotationGraph) -> bool:
        return graph.has_children(mung_tuplet, class_filter=C.Tuplets.all_numeral_members())
    
    def _has_bracket(mung_tuplet: Node, graph: NotationGraph) -> bool:
        return graph.has_children(mung_tuplet, class_filter=C.Tuplets.TUPLET_BRACKET)
        
    if len(subevents) == 1:
        start = subevents[0]
        stop, continue_ = None, None
    else:
        start = subevents[0]
        stop = subevents[-1]
        continue_ = subevents[1:-1]
        if len(continue_) == 0:
            continue_ = None
    try:
        return Tuplet(
            start=start,
            stop=stop,
            continue_=continue_,
            time_modification=_construct_time_modification(mung_tuplet),
            bracket=YesNoToken.from_bool(_has_bracket(mung_tuplet, graph)),
            show_number=ShowTupleToken.ACTUAL if _has_number(mung_tuplet, graph) else ShowTupleToken.NONE,
            placement=AboveBelowToken.from_int(infer_vertical_object_placement_relative_to_notes(mung_tuplet, graph))
        )
    except ValueError as e:
        raise ValueError(f"Unable to construct {Tuplet.__name__} from MuNG tuplet {mung_tuplet}") from e


def _construct_time_modification(mung_tuplet: Node) -> TimeModification:
        return TimeModification.from_fraction(
            get_tuple_time_modification(mung_tuplet)
        )
