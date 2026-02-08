from collections import defaultdict

from .graph import Node, NotationGraph
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
            logger.warning(f"{node.class_name} {node.id} should have exactly one stem. "
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

def form_chord_from_whole_notes(wholes: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Separates given whole notes based on their links to staffs.

    Assumes that the notes are all located in the same system measure.
    """
    staffs_to_wholes: defaultdict[Node, list[Node]] = defaultdict(list)
    def _get_staff(node: Node, graph: NotationGraph) -> Node:
        return graph.children(node, class_filter=C.Staves.STAFF)[0]
    
    for whole in wholes:
        staffs_to_wholes[_get_staff(whole, graph)].append(whole)
    
    output = []
    for _, value in staffs_to_wholes.items():
        output.append(value)
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