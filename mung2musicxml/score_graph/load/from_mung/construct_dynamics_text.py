from mung import Node, NotationGraph

from typing import Iterable, Optional
from ...graph import DynamicsText, Subevent
from .construct_score_text import _construct_score_text
from .collector import needs_graph


@needs_graph
def construct_dynamics_text(
        mung_dynamics_text: Node,
        subevents: Iterable[Subevent],
        graph: NotationGraph
) -> Optional[DynamicsText]:
    return _construct_score_text(
        mung_dynamics_text,
        subevents,
        graph,
        DynamicsText
    )
