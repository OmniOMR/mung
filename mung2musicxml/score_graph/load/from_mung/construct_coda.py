from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes

from ...graph import Subevent, Coda, AboveBelowToken
from .collector import needs_graph


@needs_graph
def construct_coda(mung_coda: Node, subevent: Subevent, graph: NotationGraph) -> Coda:
    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_coda, graph)
    )

    return Coda(subevent, placement)
