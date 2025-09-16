from abc import ABC
from mung import NotationGraph, Node
from mung.constants import ClassNamesConstants
from typing import Optional

from .strategies import GeneralSnapEngineStrategy
from .utils import log_total
from ..staff_wrapper import StaffWrapper
from ...logger import logger


class SnapEngineBase(ABC):
    """
    Automatically links object with class names
    given by ``_SYMBOL_NAMES`` to staff.

    If the object is already connected to a staffline,
    it tries to use the parent staff of said staffline.
    """
    _SYMBOL_NAMES: list[str] | set[str] | str

    def __init__(self, strategy: Optional[GeneralSnapEngineStrategy] = None):
        self._graph: NotationGraph = None #type: ignore
        self._staff_wrappers: list[StaffWrapper] = None #type: ignore
        self._strategy = GeneralSnapEngineStrategy() if strategy is None else strategy
    
    def __call__(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        self.snap_symbols(graph, staff_wrappers)
        self.reset()
    
    @classmethod
    def run(
        cls,
        graph: NotationGraph,
        staff_wrappers: Optional[list[StaffWrapper]] = None,
        strategy: Optional[GeneralSnapEngineStrategy] = None
        ):
        cls(strategy).snap_symbols(graph, staff_wrappers)
    
    def _warning_or_error(self, msg: str) -> None:
        if not self._strategy.PERMISSIVE:
            raise ValueError(msg)
        else:
            logger.warning(msg)
    
    def _set_wrappers(self, staff_wrappers: list[StaffWrapper]) -> None:
        self._staff_wrappers = staff_wrappers
    
    def _set_graph(self, graph: NotationGraph) -> None:
        self._graph = graph
    
    def reset(self) -> None:
        self._graph = None #type: ignore
        self._staff_wrappers = None #type: ignore
    
    def snap_symbols(self, graph: NotationGraph, staff_wrappers: Optional[list[StaffWrapper]] = None) -> None:
        self._set_wrappers(StaffWrapper.from_graph(graph) if staff_wrappers is None else staff_wrappers)
        self._set_graph(graph)

        symbols = self._graph.filter_vertices(self._SYMBOL_NAMES)
        total = 0
        for symbol in symbols:
            self._snap_symbol(symbol)
            total += 1
        
        log_total(total, self._SYMBOL_NAMES)
    
    def _staff_id_from_staffline(self, staffline: Node) -> Optional[int]:
        staff_from_staffline = self._graph.parents(staffline, class_filter=ClassNamesConstants.STAFF)
        if len(staff_from_staffline) != 1:
            self._warning_or_error(f"Staffline is assigned to {len(staff_from_staffline)} number of staffs")
            return None
        
        return staff_from_staffline[0].id
    
    def _retrieve_staff_id_if_assigned(self, symbol: Node) -> Optional[int]:
        """
        Retrieves staff id based on connection already made - symbol to staff
        or symbol to staffline.

        Raises warnings (or errors, if strategy is strict) if the symbol is
        assigned to multiple stafflines or staffs, or the assigned staffline
        is not a children of the assigned staff.
        """
        stafflines = self._graph.children(symbol, class_filter=ClassNamesConstants.STAFFLINE)
        staffs = self._graph.children(symbol, class_filter=ClassNamesConstants.STAFF)

        if len(stafflines) > 1:
            self._warning_or_error("Symbol cannot be connected to more than one staffline")
            return None
        
        if len(staffs) > 1:
            self._warning_or_error("Symbol cannot be connected to more than one staff")
            return None
        
        if len(stafflines) == 1 and len(staffs) == 1:
            staffline = stafflines[0]
            staff = staffs[0]

            staff_from_staffline_id = self._staff_id_from_staffline(staffline)
            if staff_from_staffline_id is None:
                return None
            
            if staff_from_staffline_id != staff.id:
                self._warning_or_error("Staffline parent staff id "
                                       "and symbol parent staff id do not match: "
                                       f"{staff_from_staffline_id} vs {staff.id}")
                return None
            
            return staff.id
        
        if len(stafflines) == 1:
            staffline = stafflines[0]
            staff_from_staffline_id = self._staff_id_from_staffline(staffline)            
            return staff_from_staffline_id
        
        if len(staffs) == 1:
            return staffs[0].id

        return None 
   
    def _closest_staff_for_symbol(self, symbol: Node) -> tuple[int,int]:
        """
        Find the closest staff to a given symbol.
        Returns data as ``distance, staff_id``.

        Should be used exclusive to snap symbols located **inside** the staff.
        """
        distance, staff_id = min(
            [(sw.absolute_vertical_distance_from_geometry(symbol), sw.parent_staff_id)
            for sw in self._staff_wrappers],
            key=lambda x: x[0]
        )

        return distance, staff_id
    
    def _snap_symbol(self, symbol: Node):
        derived_id = self._retrieve_staff_id_if_assigned(symbol)
        distance, computed_id = self._closest_staff_for_symbol(symbol)

        if derived_id is None:
            self._graph.add_edge(symbol.id, computed_id)
        
            logger.debug(f"Closest staff for {symbol.id} is {computed_id}, "
                         f"distance is {distance}")
        
        else:
            if derived_id != computed_id:
                logger.warning("Computed id and id derived from graph do not match, "
                               f"will use the {'computed' if self._strategy.DEFAULT_TO_COMPUTED else 'derived'} id")
            
            logger.debug(f"Snapping symbol {symbol.id} to staff {derived_id}, derived from graph")
            self._graph.add_edge(symbol.id, computed_id if self._strategy.DEFAULT_TO_COMPUTED else derived_id)
