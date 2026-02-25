from dataclasses import dataclass, field
from typing import Optional

from .scene_object import SceneObject
from .durable import Durable
from .note import Note
from .tokens import PlacementToken

@dataclass
class Tie(SceneObject):
    start: Durable
    placement: PlacementToken
    stop: Optional[Durable] = None

    all_durables: list[Durable] = field(init=False, repr=False)

    def __post_init__(self):
        if self.stop is not None:
            assert self.start.in_measure_fractional_end_onset == self.stop.in_measure_fractional_onset
        if isinstance(self.start, Note) and isinstance(self.stop, Note):
            assert self.start.pitch == self.stop.pitch
        
        self.all_durables = self._collect()
    
    def __len__(self) -> int:
        return len(self.all_durables)
    
    def _collect(self) -> list[Durable]:
        if self.stop is not None:
            return [self.start, self.stop]
        else:
            return [self.start]

    def is_start(self, durable: Durable) -> bool:
        return self.start == durable
    
    def is_stop(self, durable: Durable) -> bool:
        if self.stop is None:
            return False
        return self.stop == durable
    
    @property
    def is_let_ring(self) -> bool:
        return len(self) == 1
    