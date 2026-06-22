from mung import Node, NotationGraph

from typing import Iterable, Optional
from ...graph import Tempo, Subevent
from .construct_score_text import _construct_score_text


def construct_tempo(
        mung_tempo: Node,
        subevents: Iterable[Subevent],
        graph: NotationGraph
) -> Optional[Tempo]:
    return _construct_score_text(
        mung_tempo,
        subevents,
        graph,
        Tempo
    )
