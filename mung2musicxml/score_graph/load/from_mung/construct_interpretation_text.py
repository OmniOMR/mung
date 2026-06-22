from mung import Node, NotationGraph

from typing import Iterable, Optional
from ...graph import InterpretationText, Subevent
from .construct_score_text import _construct_score_text


def construct_interpretation_text(
        mung_dynamics_text: Node,
        subevents: Iterable[Subevent],
        graph: NotationGraph
) -> Optional[InterpretationText]:
    return _construct_score_text(
        mung_dynamics_text,
        subevents,
        graph,
        InterpretationText
    )
