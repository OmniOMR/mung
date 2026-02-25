from dataclasses import dataclass, field
from typing import ClassVar

from .scene_object import SceneObject
from .subevent import Subevent
from .tokens import TremoloType
from .time_modification import TimeModification


@dataclass
class TremoloBeam(SceneObject):
    """
    Equivalent to MusicXML Tremolo Double.

    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/tremolo/
    """
    start: Subevent
    stop: Subevent
    marks: int
    all_subevents: list[Subevent] = field(init=False)
    time_modification: ClassVar[TimeModification] = TimeModification(2, 1)

    def __post_init__(self) -> None:
        assert self.start.in_measure_onset < self.stop.in_measure_fractional_onset
        self.all_subevents = [self.start, self.stop]

    def is_start(self, durable: Subevent) -> bool:
        return self.start == durable
    
    def is_stop(self, durable: Subevent) -> bool:
        return self.stop == durable
    

    