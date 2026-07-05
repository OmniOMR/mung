from collections import defaultdict
from typing import Iterable
from itertools import chain

from mung import Node, NotationGraph
from mung.constants import InferenceEngineConstants as I, ClassNameConstants as C

from ....logger import logger
from ...graph import GraceChord, GraceNote, StemValueToken, Subevent
from .utils import (
    get_onset_beats,
    get_pitch,
)
from .utils import get_note_stem_orientation
from .construct_beam import construct_durable_beam
from .construct_accidental import construct_accidental_for_notehead
from .construct_dots import construct_dots_for_durable_like


def _grace_notes_to_chords(
    notes: Iterable[Node], graph: NotationGraph
) -> list[list[Node]]:
    chords: defaultdict[Node, list[Node]] = defaultdict(list)
    wholes: list[list[Node]] = []

    for note in notes:
        stems = graph.children(note, class_filter=C.NoteheadAttachments.STEM)
        if len(stems) == 0:
            wholes.append([note])
        stem = stems[0]
        chords[stem].append(note)

    return list(chords.values()) + wholes


def _construct_grace_note(mung_note: Node, graph: NotationGraph) -> GraceNote:
    from .construct_note import _note_type_from_node

    stem_orientation = get_note_stem_orientation(mung_note, graph)
    note_type = _note_type_from_node(mung_note)
    if stem_orientation is StemValueToken.NONE and note_type.has_stem():
        logger.warning(
            f"Note {mung_note} must have a stem but no was found, using default {StemValueToken.default()}"
        )
        stem_orientation = StemValueToken.default()

    n = GraceNote(
        type_=note_type,
        fractional_onset_=get_onset_beats(mung_note),
        pitch=get_pitch(mung_note),
        stem_orientation=stem_orientation,
    )

    construct_dots_for_durable_like(mung_note, n, graph)
    construct_accidental_for_notehead(mung_note, n, graph)
    return n


def construct_grace_notes_for_durable(
    mung_chord: list[Node], parent: Subevent, graph: NotationGraph
) -> list[tuple[Node, GraceNote]]:

    # This mapping is used to link created grace notes to staff
    found_beams: defaultdict[Node, set[GraceChord]] = defaultdict(set)

    # Collect all grace notes connected to one chord in graph
    mung_gns = set(
        chain.from_iterable(
            graph.children(md, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES)
            for md in mung_chord
        )
    )
    if len(mung_gns) > 0:
        mapping: list[tuple[Node, GraceNote]] = []
        g_chords = _grace_notes_to_chords(mung_gns, graph)
        for chord in g_chords:
            beams: list[Node] = []
            c: list[GraceNote] = []
            for note in chord:
                gn = _construct_grace_note(note, graph)
                c.append(gn)
                mapping.append((note, gn))

                beams.extend(
                    graph.children(note, class_filter=C.NoteheadAttachments.BEAM)
                )

            gc = GraceChord(
                notes=c,
                parent=parent,
            )

            for beam in beams:
                found_beams[beam].add(gc)

        for mung_beam, gcs in found_beams.items():
            beam = construct_durable_beam(mung_beam, list(gcs))

        return mapping
    else:
        return []
