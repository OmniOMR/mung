from itertools import chain

from mung import Node, NotationGraph
from mung.constants import (
    ClassNameConstants as C,
    InferenceEngineConstants as I,
)

from ...logger import logger


def _link_ottava(ottava: Node, graph: NotationGraph) -> None:
    linked = graph.parents(ottava, class_filter=I.CLASSES_BEARING_DURATIONS)
    if len(linked) < 2:
        return

    linked.sort(key=lambda n: n.left)
    left_limit, right_limit = linked[0].left, linked[-1].right

    staffs = set(
        chain.from_iterable(
            graph.children(n, class_filter=C.Staves.STAFF) for n in linked
        )
    )

    if len(staffs) == 0:
        raise ValueError(f"Ottava durables are not linked to any staff {linked}")
    elif len(staffs) > 1:
        logger.warning("Found multiple staffs for ottava, will choose the closer one")

    staff = min(staffs, key=lambda s: abs(s.vertical_center - ottava.vertical_center))

    durables = graph.parents(staff, class_filter=I.CLASSES_BEARING_DURATIONS)

    for durable in durables:
        if left_limit <= durable.horizontal_center <= right_limit:
            if not graph.has_edge(durable, ottava):
                graph.add_edge(durable, ottava)
            # add whole chords
            for stem in graph.children(
                durable, class_filter=C.NoteheadAttachments.STEM
            ):
                for chord_durable in graph.parents(
                    stem,
                    class_filter=[
                        C.Noteheads.NOTEHEAD_BLACK,
                        C.Noteheads.NOTEHEAD_HALF,
                    ],
                ):
                    if not graph.has_edge(chord_durable, ottava):
                        graph.add_edge(chord_durable, ottava)


def link_ottavas(graph: NotationGraph) -> None:
    """
    Links ottava spanners to all durables at the same staff
    as their start and end.
    """

    for ottava in graph.filter_vertices(C.Octaves.OTTAVA_SPANNER):
        _link_ottava(ottava, graph)
