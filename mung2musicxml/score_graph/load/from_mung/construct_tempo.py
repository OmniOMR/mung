from typing import Iterable, Optional

from mung import Node, NotationGraph
from ...graph import Tempo, Subevent
from .construct_score_text import _construct_score_text
from .collector import needs_graph


@needs_graph
def construct_tempo(
        mung_tempo: Node,
        subevents: list[Subevent],
        graph: NotationGraph
) -> Optional[Tempo]:
    return _construct_score_text(
        mung_tempo,
        subevents,
        graph,
        Tempo
    )
