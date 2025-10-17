from .graph import Node, NotationGraph
from .constants import ClassNamesConstants as C
from .constants import InferenceEngineConstants as I
from .logger import logger


def form_chords(noteheads: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Sorts a list of noteheads into chords by looking at shared stems.
    """
    output = []
    stems: list[Node] = []
    for node in noteheads:
        s = graph.children(node, class_filter=C.STEM)
        if len(s) > 1:
            logger.warning(f"Found double stemmed notehead {node.id}, "
                       "should have been resolved earlier")
        if len(s) == 0:
            logger.warning(f"{node.class_name} {node.id} should have exactly one stem. "
                            "Working with notehead as if it was alone on a stem")
            output.append([node])
        stems.extend(s)

    # find unique stems
    stems_unique = set(stems)
    # resolve to notehead groups
    return output + [
        graph.parents(s, class_filter=I.NONGRACE_NOTEHEAD_CLASS_NAMES) 
        for s in stems_unique]


def subevents_from_list_of_symbols(symbols: list[Node], graph: NotationGraph) -> list[list[Node]]:
    """
    Groups a list of given nodes into subevents.
    All whole notes are considered to be a single subevent.
    Other notes are grouped based on chords.
    Every other symbol (rests, ...) is its own subevent.
    """
    # notehead wholes are special case
    # TODO: for now, lets suppose that there are not two chords of whole notes
    wholes = [n for n in symbols if n.class_name == C.NOTEHEAD_WHOLE]
    # other noteheads are also special, as they can form chords
    noteheads = [n for n in symbols
                    if n.class_name in I.NONGRACE_NOTEHEAD_CLASS_NAMES and n not in wholes]
    # and than there are other symbols, like rests, that cannot form chords
    others = [n for n in symbols if n not in wholes + noteheads]

    # resolution should be done on non double-stemmed noteheads
    chords = form_chords(noteheads, graph)

    subevents = [[o] for o in others] + chords
    if len(wholes) > 0:
        subevents += [wholes]
    
    return subevents