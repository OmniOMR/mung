from typing import Optional
from mung2midi.inference import PitchInferenceEngine, PitchInferenceStrategy, Pitch
from mung import NotationGraph
from enum import StrEnum


class PitchDataConstants(StrEnum):
    PITCH = "pitch"


class PitchInferenceEngineWrapper:
    """
    Layer of abstraction above the original ``mung`` ``PitchInferenceEngine``.
    """
    def __init__(self, strategy: Optional[PitchInferenceStrategy] = None):
        self._strategy = strategy
        self._engine = PitchInferenceEngine(strategy)

    def __call__(
        self, graph: NotationGraph, add_data_to_nodes: bool = True
    ) -> dict[int, Pitch]:
        """
        Infers pitches for all notes inside the graph.
        """
        _, pitches = self._engine.infer_pitches(graph.vertices, with_pitch_objects = True)
        pitches: dict[int, Pitch]
        if add_data_to_nodes:
            self._add_pitch_data_to_nodes(graph, pitches)
        return pitches

    @staticmethod
    def _add_pitch_data_to_nodes(graph: NotationGraph, pitch_data: dict[int, Pitch]):
        for _id, pitch in pitch_data.items():
            graph[_id].data[PitchDataConstants.PITCH] = pitch
