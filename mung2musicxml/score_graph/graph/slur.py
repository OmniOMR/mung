from dataclasses import dataclass, field
from typing import Optional

from .tokens import PlacementToken

from .generic_start_stop import GenericStartStop
from .subevent import Subevent


@dataclass
class Slur(GenericStartStop):
    placement: PlacementToken = field(default=PlacementToken.default())
    
    def __post_init__(self):
        super().__post_init__()
        self._check_start_stop_onset_strong()
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    