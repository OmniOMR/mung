from collections import defaultdict
from mung import Node, NotationGraph
from mung.constants import InferenceEngineConstants as I

from ...graph import *
from .utils import (
    get_note_stem_orientation,
    get_duration_beats_w_m,
    get_onset_beats,
    get_pitch
)
from .construct_accidental import construct_accidental_for_notehead
from .construct_dots import construct_dots_for_durable_like
        

def construct_grace_notes_for_durable(durable: Node, graph: NotationGraph) -> list[GraceNote]:
    grace_notes = graph.children(durable, class_filter=I.GRACE_NOTEHEAD_CLASS_NAMES)
    if len(grace_notes) == 0:
        return []
    
    beams_to_grace: defaultdict[Node, set[GraceNote]] = defaultdict(set)
    
    output = []
    for index, note in enumerate(sorted(grace_notes, key=lambda n: get_onset_beats(n))):
        stem_orientation = get_note_stem_orientation(note, graph)
        if stem_orientation == StemValueToken.NONE:
            stem_orientation = StemValueToken.default()
        
        gn = GraceNote(
            pitch=get_pitch(note),
            type_=NoteTypeValue.from_fraction(get_duration_beats_w_m(note)),
            at_durable_index=index,
            stem_orientation=stem_orientation
            )
        
        construct_accidental_for_notehead(note, gn, graph)
        construct_dots_for_durable_like(note, gn, graph)
        for b in graph.children(note, class_filter=C.NoteheadAttachments.BEAM):
            beams_to_grace[b].add(gn)

        output.append(gn)
    
    for grace_notes in beams_to_grace.values():
        _construct_grace_note_beam(list(grace_notes))

    return output


def _construct_grace_note_beam(notes: list[GraceNote]) -> GraceNoteBeam:
    assert len(notes) > 0
    notes.sort(key=lambda s: s.at_durable_index)
    if len(notes) == 1:
        return GraceNoteBeam(
            begin=notes[0]
        )
    elif len(notes) == 2:
        return GraceNoteBeam(
            begin=notes[0],
            end=notes[1]
        )
    else:
        return GraceNoteBeam(
            begin=notes[0],
            continue_=notes[1:-1],
            end=notes[-1]
        )
    