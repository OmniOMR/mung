from typing import Optional
from mung import NotationGraph

from .precedence_linking import PrecedenceLinker
from .multistem import MultistemResolver, MultistemResolverStrategy
from ..inference import OnsetInferenceEngineWrapper, PitchInferenceEngineWrapper, OnsetsInferenceEngineWrapperStrategy
from .voices import VoiceEngine, VoiceEngineStrategy
from .in_measure_modifiers import tag_in_measure_part_modifiers_with_onset
from .repeats import tag_repeats_with_onset
from .grace_note_linking import link_grace_notes_to_parent

class MuNGPreprocessingPipeline:
    """
    Adds information to the graph.

    - Resolves multistem noteheads.
    - Adds missing precedence links between chords.
    - Infers onsets of durables.
    - Infers pitches of noteheads.
    - Infers voices of durables.
    - Computes onset for in measure modifiers (clef, key, ...).
    - Links grace noteheads to parent noteheads.
    """
    def __init__(
            self,
            multistem_strategy: Optional[MultistemResolverStrategy] = None,
            onset_strategy: Optional[OnsetsInferenceEngineWrapperStrategy] = None,
            voice_strategy: Optional[VoiceEngineStrategy] = None
        ):
        self._multistem = MultistemResolver(multistem_strategy)
        self._linker = PrecedenceLinker()
        self._onset_engine = OnsetInferenceEngineWrapper(onset_strategy)
        self._pitch_engine = PitchInferenceEngineWrapper()
        self._voice_engine = VoiceEngine(voice_strategy)
    
    def __call__(self, graph: NotationGraph) -> NotationGraph:
        graph = self._multistem(graph)
        self._linker.complete_precedence_graph(graph)
        link_grace_notes_to_parent(graph)
        self._onset_engine(graph)
        self._pitch_engine(graph)
        self._voice_engine(graph)
        tag_in_measure_part_modifiers_with_onset(graph)
        tag_repeats_with_onset(graph)
        return graph

    @classmethod
    def run(
        cls,
        graph: NotationGraph,
        multistem_strategy: Optional[MultistemResolverStrategy] = None,
        onset_strategy: Optional[OnsetsInferenceEngineWrapperStrategy] = None,
        voice_strategy: Optional[VoiceEngineStrategy] = None
    ) -> NotationGraph:
        return cls(multistem_strategy, onset_strategy, voice_strategy)(graph)
