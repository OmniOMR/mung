from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I
from mung.graph import infer_vertical_object_placement_relative_to_notes
from mung2midi.inference.ottava_direction_size import compute_ottava_direction_and_size
from ...graph import Ottava, OctaveShiftType, AboveBelowToken, Subevent
from .collector import needs_graph


def _shift_type_from_placement(placement: AboveBelowToken) -> OctaveShiftType:
    if placement == AboveBelowToken.ABOVE:
        return OctaveShiftType.DOWN
    return OctaveShiftType.UP


@needs_graph
def construct_ottava(
    mung_ottava: Node, subevents: list[Subevent], graph: NotationGraph
) -> Ottava:
    subevents.sort(key=lambda s: s.global_onset)
    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_ottava, graph)
    )

    texts = graph.children(mung_ottava, class_filter=C.Octaves)
    if len(texts) == 0:
        mung_text = None
    else:
        mung_text = texts[0]
    _, size = compute_ottava_direction_and_size(
        mung_ottava,
        graph.parents(mung_ottava, class_filter=I.CLASSES_BEARING_DURATIONS),
        mung_text,
    )

    return Ottava(
        start=subevents[0],
        stop=subevents[-1],
        continue_=subevents[1:-1] if len(subevents) > 2 else None,
        placement=placement,
        direction=_shift_type_from_placement(placement),
        size=size,
    )
