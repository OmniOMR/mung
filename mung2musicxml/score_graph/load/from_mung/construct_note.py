from mung import Node, NotationGraph
from mung.constants import ClassNameConstants as C, InferenceEngineConstants as I

from ...graph import *
from ....logger import logger
from .utils import (
    get_pitch,
    get_duration_beats,
    get_duration_beats_w_m,
    get_onset_beats,
    get_note_stem_orientation,
)
from .construct_dots import construct_dots_for_durable_like
from .construct_accidental import construct_accidental_for_notehead


def _note_type_from_node(node: Node) -> NoteTypeValue:
    match node.class_name:
        case C.Noteheads.NOTEHEAD_WHOLE:
            return NoteTypeValue.WHOLE
        case _:
            return NoteTypeValue.from_fraction(get_duration_beats_w_m(node))


def construct_note(durable: Node, graph: NotationGraph) -> Note:
    stem_orientation = get_note_stem_orientation(durable, graph)
    note_type = _note_type_from_node(durable)
    if stem_orientation is StemValueToken.NONE and note_type.has_stem():
        logger.warning(
            f"Note {durable} must have a stem but no was found, using default {StemValueToken.default()}"
        )
        stem_orientation = StemValueToken.default()
    n = Note(
        fractional_duration_=get_duration_beats(durable),
        type_=note_type,
        fractional_onset_=get_onset_beats(durable),
        pitch=get_pitch(durable),
        stem_orientation=stem_orientation,
    )

    construct_dots_for_durable_like(durable, n, graph)
    construct_accidental_for_notehead(durable, n, graph)
    return n
