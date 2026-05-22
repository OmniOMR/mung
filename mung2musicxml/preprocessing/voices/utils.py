from mung import Node, NotationGraph
from typing import TypeAlias
from fractions import Fraction
from mung.constants import (
    ClassNameConstants as C,
    OnsetDataConstants as O,
    InferenceEngineConstants as I
)

from .voice_subevent import _Subevent
from ...utils import all_min, flatten, WrapperNode


_VoiceNode: TypeAlias = WrapperNode[_Subevent]


def find_staff_for_container(container: Node, graph: NotationGraph) -> tuple[Fraction, Node]:
    """
    Returns staff belonging the leftmost durable enclosed by the given container along with durable's onset.

    If there are multiple leftmost durables, returns the topmost found staff.
    """
    # retrieve all durables connected to beam
    nodes = graph.parents(container, class_filter=I.NONGRACE_NOTEHEAD_CLASS_NAMES + I.REST_CLASS_NAMES)
    # find all the leftmost notes (smallest onset)
    
    minimal = all_min(nodes, key=lambda n: n.data[O.ONSET_BEATS])
    if len(minimal) == 0:
        raise ValueError(f"Unable to find leftmost durable for {container}")
    
    onset: Fraction = minimal[0].data[O.ONSET_BEATS]

    # find the topmost staff
    return (
        onset,
        min(
            flatten(
                graph.children(n, class_filter=C.Staves.STAFF) for n in minimal
                ), key=lambda n: n.top
        )
    )


def find_all_durable_groups(subevents: list[_VoiceNode], graph: NotationGraph) -> list[list[_VoiceNode]]:
    """
    Returns list of groups of subevents that share: tuples, beams or tremolos.
    """
    mapping: dict[Node, _VoiceNode] = {}
    large_objects: set[Node] = set()
    for subevent in subevents:
        for node in subevent.obj:
            node: Node
            mapping[node] = subevent
            large_objects.update(graph.children(
                node,
                class_filter=[C.Tremolo.TREMOLO_BEAM, C.NoteheadAttachments.BEAM, C.Tuplets.TUPLET])
            )
    
    groups: list[list[_VoiceNode]] = []
    for lo in large_objects:
        durables = graph.parents(lo, class_filter=I.CLASSES_BEARING_DURATIONS)
        group = {vn for x in durables if (vn := mapping.get(x)) is not None}
        if len(group) > 0:
            groups.append(list(group))
    
    return groups
