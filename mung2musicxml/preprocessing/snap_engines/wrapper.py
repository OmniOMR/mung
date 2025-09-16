from typing import Optional, Type
from mung import NotationGraph

from .strategies import SnapWrapperStrategy
from .base import SnapEngineBase
from .notehead_engine import NoteheadSnapEngine
from .separator_engine import MeasureSeparatorSnapEngine
from .utils import all_subclasses
from ..staff_wrapper import StaffWrapper


class SnapEnginesWrapper:
    """
    Wrapper to run all implementations of snap engines derived from ``SnapEngineBase``
    and special-case engine: ``NoteheadSnapEngine`` and ``MeasureSeparatorSnapEngine``.

    Modifies the graph in-place.
    """
    __ALL_SUBCLASSES = all_subclasses(SnapEngineBase)
    def __init__(
            self,
            strategy: Optional[SnapWrapperStrategy] = None,
            common_engines: Optional[set[Type[SnapEngineBase]]] = None
        ):
        self._strategy = SnapWrapperStrategy() if strategy is None else strategy
        self._notehead_engine = NoteheadSnapEngine(self._strategy.notehead_strategy)
        self._ms_engine = MeasureSeparatorSnapEngine(self._strategy.measure_separator_strategy)
        self._engines = [se(self._strategy.general_strategy) for se in (SnapEnginesWrapper.__ALL_SUBCLASSES if common_engines is None else common_engines)]
    
    def __call__(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        self.snap_symbols(graph, staff_wrappers)

    @classmethod
    def run(
        cls,
        graph: NotationGraph,
        staff_wrappers: Optional[list[StaffWrapper]] = None,
        strategy: Optional[SnapWrapperStrategy] = None,
        common_engines: Optional[set[Type[SnapEngineBase]]] = None
        ):
        """
        Runs all snap engines derived from ``SnapEngineBase``.
        Snaps symbols to staffs.

        Graph is modified in-place.
        """
        cls(strategy, common_engines).snap_symbols(graph, staff_wrappers)

    def snap_symbols(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        staff_wrappers = staff_wrappers if staff_wrappers is not None else StaffWrapper.from_graph(graph)

        self._notehead_engine(graph, staff_wrappers)
        self._ms_engine(graph, staff_wrappers)

        for engine in self._engines:
            engine(graph, staff_wrappers)