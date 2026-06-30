from fractions import Fraction
from mung import Node, NotationGraph
from typing import TypeVar, Callable, Iterable, Optional
from mung.constants import (
    ClassNameConstants as C,
    OnsetDataConstants as O
)
from mung.graph import infer_stem_orientation
from mung2midi.inference.clefs_impl import get_clef_data_from_node
from ....inference import PitchDataConstants as P
from ....preprocessing.voices.engine import VoiceDataConstants as V
from ...graph import *
from ....logger import logger


def get_duration_beats(durable: Node) -> Fraction:
    return durable.data[O.DURATION_BEATS]


def get_duration_beats_w_m(durable: Node) -> Fraction:
    return durable.data[O.DURATION_BEATS_WO_M]


def get_onset_beats(durable: Node) -> Fraction:
    return durable.data[O.ONSET_BEATS]


def get_pitch(durable: Node) -> Pitch:
    return durable.data[P.PITCH]


def get_voice(durable: Node) -> int:
    return durable.data[V.VOICE_ID]


def get_tuple_time_modification(tuplet: Node) -> Fraction:
    return tuplet.data[O.TUPLE_TIME_MODIFICATION]


def get_durable_pitch(durable: Durable) -> int:
    """
    Returns the durable pitch as midi `int`,
    `-1` if the durable does not have a pitch.
    """
    if isinstance(durable, Note):
        return durable.pitch.to_midi()
    return -1


def get_note_stem_orientation(note: Node, graph: NotationGraph) -> StemValueToken:
    """
    Computes stem orientation of given note
    and caches it.
    """
    stems = graph.children(note, class_filter=C.NoteheadAttachments.STEM)
    
    # maybe a whole note
    if len(stems) == 0:
        return StemValueToken.NONE
    
    if len(stems) > 1:
        logger.warning(f"Too many stems found for notehead {note}, using the first one")
        stems.sort(key=lambda s: s.id)
    
    stem = stems[0]
    cached_so = stem.data.get("orientation")
    if cached_so is None:
        so = StemValueToken.from_int(infer_stem_orientation(stem, graph))
        stem.data["orientation"] = so
        return so
    
    return cached_so


def get_default_clef_line_from_node(clef: Node) -> int:
    """
    Default staffline delta is, for pitch inference,
    implemented as the number of staff lines and spaces
    from the middle staffline.
    This method matches the clef type and converts
    the staffline delta, so that the returner number
    is an index of its staff line from bottom to top,
    starting from 1.
    """
    base = get_clef_data_from_node(clef)
    return (base.default_staffline_delta // 2) + 3


def find_line_index_for_clef(clef: Node, graph: NotationGraph) -> int:
    """
    Finds the line index of `clef`. If the `clef` is not connected to any
    line, return the default clef line.
    """
    staffs = graph.children(clef, class_filter=C.Staves.STAFF)
    assert len(staffs) > 0, f"Unsupported number of staffs for {clef}, {staffs}"
    lines = graph.children(clef, class_filter=C.Staves.STAFF_LINE)
    
    if len(lines) == 0:
        index = get_default_clef_line_from_node(clef)
        logger.warning(f"{clef} is not assigned to any staff line, choosing default {index}")
        return index
    
    staff = staffs[0]
    line = lines[0]

    s_lines = graph.children(staff, class_filter=C.Staves.STAFF_LINE)
    assert len(s_lines) == 5
    # lowest staff line is first
    s_lines.sort(key=lambda l: l.top, reverse=True)
    return s_lines.index(line) + 1


def get_start_stop_subevents(
        subs: list[Subevent]
) -> tuple[Subevent, Optional[Subevent]]:
    """
    Returns start with the lowest global
    fractional onset and minimal voice.
    The highest gfo is returned as stop subevent,
    if it differs from the lowest one.

    :return: (start, stop or None)
    """
    assert len(subs) > 0
    
    subs.sort(key=lambda s: s.global_fractional_onset)
    # solve multiple links from subevents with the same onset
    # (choose one with the lowest voice)
    if subs[0].global_fractional_onset == subs[-1].global_fractional_onset:
        return min(subs, key=lambda s: s.voice.id), None

    min_onset = subs[0].global_fractional_onset # sorted, so first is min
    max_onset = subs[-1].global_fractional_onset # sorted, so last is max
    
    first = min(
        (s for s in subs if s.global_fractional_onset == min_onset),
        key=lambda s: s.voice.id
    )
    last = min(
        (s for s in subs if s.global_fractional_onset == max_onset),
        key=lambda s: s.voice.id
    )
    
    return first, last


def _log_object_creation(obj: SceneObject, source_mung_node_or_nodes: Node | list[Node]) -> None:
    """
    Logs object into console creations via the mung2musicxml logger.
    """
    if isinstance(source_mung_node_or_nodes, Node):
        source_str = str(source_mung_node_or_nodes)
    else:
        source_str = ", ".join(str(x) for x in source_mung_node_or_nodes)
    
    logger.debug(f"Added {type(obj).__name__} based on {source_str}")
    