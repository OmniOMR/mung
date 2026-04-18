from fractions import Fraction
from mung import Node, NotationGraph
from typing import TypeVar, Callable
from mung.constants import (
    ClassNameConstants as C,
    OnsetDataConstants as O
)
from mung.graph import infer_stem_orientation
from ....inference import PitchDataConstants as P
from ....preprocessing.voices.engine import VoiceDataConstants as V
from ...graph import *
from ....logger import logger


def duration_beats(durable: Node) -> Fraction:
    return durable.data[O.DURATION_BEATS]


def duration_beats_w_m(durable: Node) -> Fraction:
    return durable.data[O.DURATION_BEATS_WO_M]


def onset_beats(durable: Node) -> Fraction:
    return durable.data[O.ONSET_BEATS]


def pitch(durable: Node) -> Pitch:
    return durable.data[P.PITCH]


def voice(durable: Node) -> int:
    return durable.data[V.VOICE_ID]


def tuple_time_modification(tuplet: Node) -> Fraction:
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
    from mung2midi.inference.clefs_impl import get_clef_data_from_node
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


T = TypeVar("T")


def find_subgraphs_bfs(nodes: list[T], has_edge: Callable[[T, T], bool]) -> list[list[T]]:
    """
    Find all connected components (subgraphs) using BFS.
    
    :param nodes: list of objects (nodes in the graph)
    :param has_edge: function(a, b) -> bool,
        returns ``True`` if an edge exists between a and b
    
    :return: list of components, where each component is a list of connected nodes
    """
    unvisited = set(range(len(nodes)))
    components = []

    while unvisited:
        # Start a new component from an arbitrary unvisited node
        start = next(iter(unvisited))
        component = []
        queue = [start]
        unvisited.remove(start)

        while queue:
            curr = queue.pop(0)
            component.append(nodes[curr])

            # Check all remaining unvisited nodes for adjacency
            neighbors = {n for n in unvisited if has_edge(nodes[curr], nodes[n])}
            unvisited -= neighbors
            queue.extend(neighbors)

        components.append(component)

    return components
