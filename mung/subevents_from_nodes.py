from collections import defaultdict
from itertools import chain

from .graph import Node, NotationGraph, UnionFind
from .constants import ClassNameConstants as C
from .constants import InferenceEngineConstants as I
from .logger import logger


def form_chords(noteheads: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Sorts a list of noteheads into chords by looking at shared stems.
    """
    output = []
    stems: list[Node] = []
    for node in noteheads:
        s = graph.children(node, class_filter=C.NoteheadAttachments.STEM)
        if len(s) > 1:
            logger.warning(f"Found double stemmed notehead {node.id}, "
                       "should have been resolved earlier")
        if len(s) == 0:
            logger.warning(f"{node} should have exactly one stem. "
                           f"Has {len(s)}. "
                           "Working with notehead as if it was alone on a stem")
            output.append([node])
        stems.extend(s)

    # find unique stems
    stems_unique = set(stems)
    # resolve to notehead groups
    return output + [
        graph.parents(s, class_filter=I.NONGRACE_NOTEHEAD_CLASS_NAMES) 
        for s in stems_unique]


def check_tremolo_beams_for_whole(wholes: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Separates a group of whole noteheads (located in the same measure)
    into chords based on tremolo beams.

    If a tremolo beam is found, noteheads are separated
    into two chords based on their horizontal distance
    from the mean horizontal coordinate (left, right).
    """
    wholes_linked_tremolos: list[list[Node]] = []

    tremolos: set[Node] = set()
    for whole in wholes:
        tremolos.update(graph.children(whole, class_filter=C.Tremolo.TREMOLO_BEAM))

    if len(tremolos) == 0:
        return [wholes]
    
    for tremolo in tremolos:
        wholes_linked_tremolos.append([
            w for w in graph.parents(tremolo, class_filter=C.Noteheads.NOTEHEAD_WHOLE)
            if w in wholes
        ])

    # list of whole noteheads that share tremolos
    tremolo_groups = UnionFind.merge_groups(wholes_linked_tremolos)

    def _resolve_single_tremolo_group(tremolo_group: list[Node]) -> tuple[list[Node], list[Node]]:
        assert len(tremolo_group) >= 2
        mean_horizontal = sum(w.horizontal_center for w in tremolo_group) / len(tremolo_group)
        left, right = [], []
        for w in tremolo_group:
            if w.horizontal_center < mean_horizontal:
                left.append(w)
            else:
                right.append(w)
        
        return left, right
    
    chords: list[list[Node]] = []
    for group in tremolo_groups:
        if len(group) >= 2:
            chords.extend(_resolve_single_tremolo_group(group))

    other: list[Node] = []
    for whole in wholes:
        if whole not in set(chain.from_iterable(chords)):
            other.append(whole)
    
    if len(other) > 0:
        chords.append(other)
    
    return chords


def form_chord_from_whole_notes(wholes: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Separates given whole notes based on their links to staffs.

    Assumes that the notes are all located in the same system measure.
    """
    staffs_to_wholes: defaultdict[Node, list[Node]] = defaultdict(list)
    def _get_staff(node: Node, graph: NotationGraph) -> Node:
        return graph.children(node, class_filter=C.Staves.STAFF)[0]
    
    # TODO: support tremolo beams

    for whole in wholes:
        staffs_to_wholes[_get_staff(whole, graph)].append(whole)
    
    output: list[list[Node]] = []
    for _, value in staffs_to_wholes.items():
        output.extend(
            
        check_tremolo_beams_for_whole(value, graph)
        )
    return output


def subevents_from_list_of_symbols(symbols: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Groups a list of given nodes into subevents.
    All whole notes are considered to be a single subevent.
    Other notes are grouped based on chords.
    Every other symbol (rests, ...) is its own subevent.

    Assumes that all notes are located in the same system measure.
    """
    # notehead wholes are special case
    wholes = [n for n in symbols if n.class_name == C.Noteheads.NOTEHEAD_WHOLE]
    # other noteheads are also special, as they can form chords
    noteheads = [n for n in symbols
                    if n.class_name in I.NONGRACE_NOTEHEAD_CLASS_NAMES and n not in wholes]
    # and than there are other symbols, like rests, that cannot form chords
    others = [n for n in symbols if n not in wholes + noteheads]

    # resolution should be done on non double-stemmed noteheads
    chords = form_chords(noteheads, graph)

    subevents = [[o] for o in others] + chords + form_chord_from_whole_notes(wholes, graph)
    # if len(wholes) > 0:
    #     subevents += [wholes]
    
    return subevents
