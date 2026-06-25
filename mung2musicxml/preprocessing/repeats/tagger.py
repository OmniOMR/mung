from mung import NotationGraph
from mung.constants import (
    OnsetDataConstants as O,
    ClassNameConstants as C,
    InferenceEngineConstants as I
)
from itertools import chain
from ...logger import logger


def tag_repeats_with_onset(graph: NotationGraph) -> None:
    """
    Adds duration to every repeats that is not part
    of measure separator based on its closest durable (to the right).
    """
    for repeat in graph.filter_vertices([C.Repeat.REPEAT_LEFT, C.Repeat.REPEAT_RIGHT]):
        
        barlines = graph.children(repeat, class_filter=[C.Barlines.BARLINE_HEAVY, C.Barlines.BARLINE_FINAL, C.Barlines.BARLINE_SINGLE])
        # repeat is part of a measure separator
        if any(graph.has_parents(barline, class_filter=C.Barlines.MEASURE_SEPARATOR) for barline in barlines):
            continue

        staffs = [
            staff for staff in graph.filter_vertices(C.Staves.STAFF)
            if staff.overlaps(repeat)
        ]

        durables = chain.from_iterable(graph.parents(staff, class_filter=I.CLASSES_BEARING_DURATIONS) for staff in staffs)
        
        closest = min((d for d in durables if d.horizontal_center > repeat.horizontal_center),
                        key=lambda d: d.horizontal_center - repeat.horizontal_center,
                        default=None)
        
        if closest is None:
            logger.warning(f"Unable to find closest durable for {repeat}")
            continue

        graph.add_edge(closest, repeat)
        repeat.data[O.ONSET_BEATS] = closest.data[O.ONSET_BEATS]
        logger.debug(f"Snapped {repeat} to {closest}")
