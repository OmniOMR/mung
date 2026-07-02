from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C
from mung.graph import infer_vertical_object_placement_relative_to_notes

from ...graph import *
from .collector import needs_graph


def _wedge_type_from_mung_class_name(class_name: str) -> WedgeType:
    match class_name:
        case C.Dynamics.DYNAMIC_CRESCENDO_HAIRPIN:
            return WedgeType.CRESCENDO
        case C.Dynamics.DYNAMIC_DIMINUENDO_HAIRPIN:
            return WedgeType.DIMINUENDO
        case _:
            raise ValueError(f"Unknown {WedgeType.__name__}: '{class_name}'")


def _has_niente(mung_hairpin: Node, graph: NotationGraph) -> YesNoToken:
    return YesNoToken.from_bool(
        graph.has_children(
            mung_hairpin, class_filter=C.Dynamics.DYNAMIC_NIENTE_FOR_HAIRPIN
        )
    )


@needs_graph
def construct_wedge(
    mung_hairpin: Node, subevents: list[Subevent], graph: NotationGraph
) -> Wedge:
    """
    Creates a wedge that starts and ends with elements from
    `subevents`. If there is only one Subevent, the wedge
    starts and ends at this Subevent.
    """
    assert len(subevents) > 0
    subevents.sort(key=lambda s: s.global_fractional_onset)

    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_hairpin, graph)
    )

    staff = min((s for s in subevents[0].staffs), key=lambda s: s.id)
    w = Wedge(
        start=subevents[0],
        stop=subevents[-1],
        continue_=subevents[1:-1] if len(subevents) > 2 else None,
        type_=_wedge_type_from_mung_class_name(mung_hairpin.class_name),
        placement=placement,
        niente=_has_niente(mung_hairpin, graph)
    )

    staff.other_symbols = staff.other_symbols + [w]
    return w
