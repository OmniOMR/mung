from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes

from ...graph import Subevent, Segno, AboveBelowToken


def construct_segno(
    mung_segno: Node, subevent: Subevent, graph: NotationGraph
) -> Segno:
    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_segno, graph)
    )

    return Segno(subevent, placement)
