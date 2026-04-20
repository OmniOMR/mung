from mung import Node, NotationGraph
from mung.constants import (
    ClassNameConstants as C,
)

from ...graph import *
from .utils import  get_duration_beats, get_duration_beats_w_m, get_onset_beats
from .construct_dots import construct_dots_for_durable_like


def construct_rest(durable: Node, graph: NotationGraph) -> Rest:
    r = Rest(
        fractional_duration_=get_duration_beats(durable),
        type_=_rest_type_from_node(durable),
        fractional_onset_=get_onset_beats(durable),
    )
    construct_dots_for_durable_like(durable, r, graph)
    return r


def _rest_type_from_node(node: Node) -> NoteTypeValue:
    """
    Durables whose duration is dependant on measure
    duration might vary in duration. This function
    maps them directly to DurableType based on class
    name, not duration. Other durables are mapped based
    on their duration.

    For example: rest whole has duration 3 in 3/4 time
    signature, but duration 4 in 4/4 time signature.
    """
    match node.class_name:
        case C.Rests.REST_WHOLE:
            return NoteTypeValue.WHOLE
        case C.Rests.REST_DOUBLE_WHOLE:
            return NoteTypeValue.BREVE
        case C.Rests.REST_LONGA:
            return NoteTypeValue.LONG
        case _:
            return NoteTypeValue.from_fraction(get_duration_beats_w_m(node))
