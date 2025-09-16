from mung.constants import ClassNamesConstants
from mung import Node, NotationGraph
from typing import Optional

from .strategies import MeasureSeparatorSnapEngineStrategy
from .utils import log_total
from ..staff_wrapper import StaffWrapper
from ...logger import logger


class MeasureSeparatorSnapEngine:
    def __init__(self, strategy: Optional[MeasureSeparatorSnapEngineStrategy] = None):
        """
        Parameter ``staff_wrappers`` makes it possible to share
        created ``StaffWrapper``s between multiple other snap engines,
        and to save some time creating new instances inside every engine.
        """
        self._strategy = MeasureSeparatorSnapEngineStrategy() if strategy is None else strategy
    
    def __call__(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        self.snap_measure_separators_to_staffs(graph, StaffWrapper.from_graph(graph) if staff_wrappers is None else staff_wrappers)

    @classmethod
    def run(
        cls,
        graph: NotationGraph,
        staff_wrappers: Optional[list[StaffWrapper]] = None,
        strategy: Optional[MeasureSeparatorSnapEngineStrategy] = None
        ):
        cls(strategy)(graph, staff_wrappers)
    
    def snap_measure_separator_based_on_overlap(self, measure_separator: Node, graph: NotationGraph, staff_wrappers: list[StaffWrapper]):
        for sw in staff_wrappers:
            overlap = sw.vertical_overlap_geometry_normalized(measure_separator)
            if overlap >= self._strategy.MEASURE_ASSIGNMENT_THRESHOLD:
                graph.add_edge(measure_separator.id, sw.parent_staff_id)
                logger.debug(f"Snapping measure separator {measure_separator.id} to {sw.staff.id}, overlap is {overlap}.")

    def snap_measure_separators_to_staffs(self, graph: NotationGraph, staff_wrappers: list[StaffWrapper]):
        separators = graph.filter_vertices(ClassNamesConstants.MEASURE_SEPARATOR)
        total = 0
        for separator in separators:
            self.snap_measure_separator_based_on_overlap(separator, graph, staff_wrappers)
            total += 1
        
        log_total(total, ClassNamesConstants.MEASURE_SEPARATOR)
