from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes

from ...graph import *


def construct_tremolo_single(
        subevent: Subevent,
        mung_subevent_nodes: list[Node],
        mung_tremolo_singles: list[Node],
        graph: NotationGraph
) -> TremoloSingle:
    return TremoloSingle(
        subevent,
        len(mung_tremolo_singles),
        AboveBelowToken.from_int(
            infer_vertical_object_placement_relative_to_notes(
                mung_tremolo_singles[0],
                graph,
                mung_subevent_nodes
            )
        )
    )
