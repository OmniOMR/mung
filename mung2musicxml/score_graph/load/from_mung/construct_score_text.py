from mung import Node, NotationGraph
from mung.graph import infer_vertical_object_placement_relative_to_notes

from typing import Iterable, Optional, Type, TypeVar
from ....logger import logger
from ...graph import Subevent, AboveBelowToken
from ...graph.interface import ScoreText
from .utils import get_start_stop_subevents

T = TypeVar("T", bound=ScoreText)


def _construct_score_text(
    mung_text: Node,
    subevents: Iterable[Subevent],
    graph: NotationGraph,
    type_: Type[T]
) -> Optional[T]:

    if mung_text.text_transcription is None:
        logger.warning(f"No text transcription provided for {mung_text}")
        return None

    placement = AboveBelowToken.from_int(
        infer_vertical_object_placement_relative_to_notes(mung_text, graph)
    )

    start, stop = get_start_stop_subevents(list(subevents))
    assert start is not None

    return type_(
        start=start, stop=stop, text=mung_text.text_transcription, placement=placement
    )
