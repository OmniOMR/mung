from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C
from mung.graph import infer_vertical_object_placement_relative_to_notes

from ...graph import (
    Subevent,
    Turn,
    Trill,
    ShortTrill,
    AboveBelowToken,
    Arpeggiato,
    DirectionToken,
)
from .collector import needs_graph


def _ornament_base(
    mung_ornament: Node, subevents: list[Subevent], graph: NotationGraph
) -> tuple[Subevent, AboveBelowToken]:
    """
    Base for all ornament construction.

    Selects the earliest subevent with lowest voice id
    as ornament's parent and infers its placement from graph.
    """
    sub = min(subevents, key=lambda s: (s.global_onset, s.voice.id))
    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_ornament, graph)
    )
    return sub, placement


@needs_graph
def construct_turn(
    mung_turn: Node, subevents: list[Subevent], graph: NotationGraph
) -> Turn:
    assert len(subevents) > 0

    def _is_inverted(mung_turn: Node) -> bool:
        return mung_turn.class_name == C.Ornaments.ORNAMENT_TURN_INVERTED

    sub, placement = _ornament_base(mung_turn, subevents, graph)
    return Turn(sub, placement, _is_inverted(mung_turn))


@needs_graph
def construct_trill(
    mung_trill: Node, subevents: list[Subevent], graph: NotationGraph
) -> Trill:

    def _has_wiggle(mung_trill: Node, graph: NotationGraph) -> bool:
        return graph.has_children(mung_trill, class_filter=C.Ornaments.WIGGLE_TRILL)

    sub, placement = _ornament_base(mung_trill, subevents, graph)
    return Trill(sub, placement, _has_wiggle(mung_trill, graph))


@needs_graph
def construct_short_trill(
    mung_s_trill: Node, subevents: list[Subevent], graph: NotationGraph
) -> ShortTrill:
    sub, placement = _ornament_base(mung_s_trill, subevents, graph)
    return ShortTrill(sub, placement)


@needs_graph
def construct_arpeggiato(
    mung_arpeggiato: Node, subevents: list[Subevent], graph: NotationGraph
) -> Arpeggiato:

    def _name_to_direction(mung_arpeggiato: Node) -> DirectionToken | None:
        if mung_arpeggiato.class_name == C.Arpeggiato.ARPEGGIATO_UP:
            return DirectionToken.UP
        elif mung_arpeggiato.class_name == C.Arpeggiato.ARPEGGIATO_DOWN:
            return DirectionToken.DOWN
        return None

    sub, placement = _ornament_base(mung_arpeggiato, subevents, graph)
    return Arpeggiato(sub, placement, _name_to_direction(mung_arpeggiato))
