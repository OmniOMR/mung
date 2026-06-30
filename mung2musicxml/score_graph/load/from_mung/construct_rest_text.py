from mung import Node, NotationGraph

from typing import Iterable, Optional
from ...graph import RestText, Subevent
from .construct_score_text import _construct_score_text
from .collector import needs_graph


@needs_graph
def construct_rest_text(
        mung_rest_text: Node,
        subevents: Iterable[Subevent],
        graph: NotationGraph
) -> Optional[RestText]:
    return _construct_score_text(
        mung_rest_text,
        subevents,
        graph,
        RestText
    )
