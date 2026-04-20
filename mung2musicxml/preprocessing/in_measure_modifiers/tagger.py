from mung import NotationGraph
from mung.constants import (
    OnsetDataConstants as O,
    ClassNameConstants as C,
    InferenceEngineConstants as I
)
from ...logger import logger


def tag_in_measure_part_modifiers_with_onset(graph: NotationGraph) -> None:
    """
    Adds duration to every in measure modifier (clef, time signature, ...)
    based on its closest durable.
    """
    for modifier in graph.filter_vertices(I.IN_MEASURE_MODIFIERS):
        staff = graph.children(modifier, class_filter=C.Staves.STAFF)[0]
        durables = graph.parents(staff, class_filter=I.CLASSES_BEARING_DURATIONS)

        closest = min((d for d in durables if d.horizontal_center > modifier.horizontal_center),
                        key=lambda d: d.horizontal_center - modifier.horizontal_center,
                        default=None)
        
        if closest is None:
            logger.warning(f"Unable to find closest durable for {modifier}")
            continue

        graph.add_edge(closest, modifier)
        modifier.data[O.ONSET_BEATS] = closest.data[O.ONSET_BEATS]
        logger.info(f"Snapped clef change {modifier} to {closest}")
