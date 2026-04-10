from mung import Node, NotationGraph

from ...graph import *
from .utils import duration_beats, onset_beats


def construct_repeat(durable: Node, graph: NotationGraph) -> RepeatBar:
    return RepeatBar(
            type_=NoteTypeValue.NONE,
            fractional_duration_=duration_beats(durable),
            fractional_onset_=onset_beats(durable),
        )
