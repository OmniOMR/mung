from typing import Optional
from mung import NotationGraph

from .staff_generator import StaffGenerator, StaffGeneratorStrategy
from .staffspace_generator import StaffspaceGenerator, StaffspaceGeneratorStrategy
from .snap_engines import (
    SnapEnginesWrapper,
    SnapWrapperStrategy,
    GeneralSnapEngineStrategy,
    NoteheadSnapEngineStrategy,
    MeasureSeparatorSnapEngineStrategy,
)
from .precedence_linking import PrecedenceLinker
from .staff_wrapper import StaffWrapper


class MuNGPreprocessingPipeline:
    def __init__(
            self,
            staff_strategy: Optional[StaffGeneratorStrategy] = None,
            staffspace_strategy: Optional[StaffspaceGeneratorStrategy] = None,
            snap_strategy: Optional[SnapWrapperStrategy] = None
        ):
        self._staff_generator = StaffGenerator(staff_strategy)
        self._staffspace_generator = StaffspaceGenerator(staffspace_strategy)
        self._snap_engine = SnapEnginesWrapper(snap_strategy)
        self._precedence_linker = PrecedenceLinker()
    
    def __call__(self, graph: NotationGraph) -> NotationGraph:
        graph = self._staff_generator(graph)
        graph = self._staffspace_generator(graph)

        self._snap_engine(graph)
        
        self._precedence_linker(graph)
        
        return graph

    @classmethod
    def run(
        cls,
        graph: NotationGraph, 
        staff_strategy: Optional[StaffGeneratorStrategy] = None,
        staffspace_strategy: Optional[StaffspaceGeneratorStrategy] = None,
        snap_strategy: Optional[SnapWrapperStrategy] = None
        ) -> NotationGraph:
        return cls(staff_strategy, staffspace_strategy, snap_strategy)(graph)