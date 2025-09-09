from typing import Optional
from mung2midi.inference import PitchInferenceEngine, PitchInferenceStrategy, Pitch
from mung import NotationGraph
from mung.constants import ClassNamesConstants


class PitchDataConstants:
    PITCH: str = "pitch"


class PitchInferenceEngineWrapper:
    """
    Layer of abstraction above the original ``mung`` ``PitchInferenceEngine``.
    """
    def __init__(self, strategy: Optional[PitchInferenceStrategy] = None):
        self._strategy = strategy
        self._engine = PitchInferenceEngine(strategy)

    def __call__(
        self, graph: NotationGraph, add_data_to_nodes: bool = False
    ) -> dict[int, Pitch]:
        """
        Infers pitches for all notes inside the graph.
        """
        _, pitches = self._engine.infer_pitches(graph.vertices, with_pitch_objects=True)
        pitches: dict[int, Pitch]
        if add_data_to_nodes:
            self._add_pitch_data_to_nodes(graph, pitches)
        return pitches

    @staticmethod
    def _add_pitch_data_to_nodes(graph: NotationGraph, pitch_data: dict[int, Pitch]):
        for _id, pitch in pitch_data.items():
            graph[_id].data[PitchDataConstants.PITCH] = pitch
    
    @staticmethod
    def _check(graph: NotationGraph):
        pass

    @staticmethod
    def _check_notehead_assignment(graph: NotationGraph):
        # for notehead in graph.filter_vertices(ClassNamesConstants.NOTEH)
        pass