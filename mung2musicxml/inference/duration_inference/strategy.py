from dataclasses import dataclass
from mung2midi.inference import OnsetsInferenceStrategy


@dataclass(frozen=True)
class OnsetsInferenceEngineWrapperStrategy(OnsetsInferenceStrategy):
    with_grace_notes: bool = True
    offset_next_measure_by_previous_measure: bool = True
