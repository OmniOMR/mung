from typing import Optional
from enum import StrEnum

from mung import NotationGraph
from mung.constants import InferenceEngineConstants as I, ClassNameConstants as C
from mung2midi.inference import PitchInferenceEngine, PitchInferenceStrategy, Pitch
from ...logger import logger


class PitchDataConstants(StrEnum):
    PITCH = "pitch"


class PitchInferenceEngineWrapper:
    """
    Layer of abstraction above the original ``mung`` ``PitchInferenceEngine``.
    """
    def __init__(self, strategy: Optional[PitchInferenceStrategy] = None):
        self._strategy = strategy if strategy is not None else PitchInferenceStrategy()
        self._engine = PitchInferenceEngine(strategy)

    def __call__(
        self, graph: NotationGraph, add_data_to_nodes: bool = True
    ) -> dict[int, Pitch]:
        """
        Infers pitches for all notes inside the graph.
        """
        self._check_notehead_assignment(graph)
        
        _, pitches = self._engine.infer_pitches(graph.vertices, with_pitch_objects = True)
        pitches: dict[int, Pitch]
        if add_data_to_nodes:
            self._add_pitch_data_to_nodes(graph, pitches)
        return pitches
    
    def _check_notehead_assignment(self, graph: NotationGraph) -> None:
        for notehead in graph.filter_vertices(class_filter=I.NOTEHEAD_CLASS_NAMES):
            staffs = graph.children(notehead, class_filter=C.Staves.STAFF)
            if len(staffs) == 0:
                self._warn_or_raise(f"{notehead} is not connected to any staff")
            elif len(staffs) > 1:
                self._warn_or_raise(f"{notehead} is connect to too many staffs (>1), {staffs}")
    
    def _warn_or_raise(self, msg: str) -> None:
        if self._strategy.permissive:
            logger.warning(msg)
        else:
            raise AssertionError(msg)

    @staticmethod
    def _add_pitch_data_to_nodes(graph: NotationGraph, pitch_data: dict[int, Pitch]):
        for _id, pitch in pitch_data.items():
            graph[_id].data[PitchDataConstants.PITCH] = pitch
