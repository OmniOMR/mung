from mung import Node, NotationGraph

from ...graph import *
from .utils import get_duration_beats, get_onset_beats


def construct_repeat(durable: Node, graph: NotationGraph) -> RepeatBar:
    return RepeatBar(
            type_=NoteTypeValue.NONE,
            fractional_duration_=get_duration_beats(durable),
            fractional_onset_=get_onset_beats(durable),
        )
