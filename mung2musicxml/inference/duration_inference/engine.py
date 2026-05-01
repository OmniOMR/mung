from fractions import Fraction
from mung import NotationGraph, Node
from typing import Optional

from mung.constants import (
    InferenceEngineConstants as I,
    OnsetDataConstants as O,
    ClassNameConstants as C
)
from mung2midi.inference import OnsetsInferenceEngine
from .utils import _add_duration_data_to_node
from .grace_notes_inference import _GraceOnsetInference
from .onset_system_measure import _OnsetSystemMeasureWrapper
from .strategy import OnsetsInferenceEngineWrapperStrategy
from ...logger import logger


class OnsetInferenceEngineWrapper:
    def __init__(self, strategy: Optional[OnsetsInferenceEngineWrapperStrategy] = None):
        if strategy is None:
            strategy = OnsetsInferenceEngineWrapperStrategy()
        self._strategy = strategy
        self._engine = OnsetsInferenceEngine(self._strategy)
        self._grace_engine = _GraceOnsetInference(self._strategy)
    
    def _check_durables_assignment(self, graph: NotationGraph) -> None:
        for notehead in graph.filter_vertices(class_filter=I.CLASSES_BEARING_DURATIONS):
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
    
    def durations(self, graph: NotationGraph, nodes: list[Node], ignore_modifiers: bool = False) -> dict[int, Fraction]:
        self._engine.initialize_graph(graph)
        return self._engine.durations(nodes, ignore_modifiers=ignore_modifiers)
        
    def __call__(
            self,
            graph: NotationGraph
        ) -> tuple[dict[int, Fraction], dict[int, Fraction], dict[int, Fraction]]:
        """
        Computes the onsets and durations for duration-related symbols,
        stores them inside the ``data`` of each affected notehead.

        For retrieval of particular data as a ``dict[node_id, data]``
        use ``NotationGraph`` function ``collect_data``.

        :param graph: ``NotationGraph`` instance to process

        :return: Tuple of onsets, durations, and duration without modifiers
        """
        self._check_durables_assignment(graph)
        durations = self.durations(graph, graph.vertices)
        durations_wo_m = self.durations(graph, graph.vertices, ignore_modifiers=True)

        for node in graph.filter_vertices(I.CLASSES_BEARING_DURATIONS):
            _add_duration_data_to_node(
                node, durations[node.id], durations_wo_m[node.id]
            )
        
        system_measures = _OnsetSystemMeasureWrapper.from_graph(graph)

        # Process onsets in the order of system measures one by one,
        # always offset the next measure to the end of the last one.
        offset = Fraction(0)
        for i, sm in enumerate(system_measures):
            logger.debug(f"Inferring onset for {len(sm)} durables with start offset {offset} "
                        f"for measure {i}")
            sm.infer_onsets(offset, permissive=self._strategy.permissive_desynchronization)
            if self._strategy.offset_next_measure_by_previous_measure:
                offset = sm.get_end_onset()
            if not sm.is_synchronized():
                msg = f"End of system measure {i} is not synchronized"
                if self._strategy.permissive_desynchronization:
                    logger.warning(msg)
                else:
                    raise ValueError(msg)
        
        onsets: dict[int, Fraction] = graph.collect_data(O.ONSET_BEATS, log_level=0)

        if self._strategy.with_grace_notes:
            g_onsets, g_durations, g_durations_wo_m = self._grace_engine(graph)
            onsets |= g_onsets
            durations |= g_durations
            durations_wo_m |= g_durations_wo_m
        
        return onsets, durations, durations_wo_m
