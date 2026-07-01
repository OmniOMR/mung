from dataclasses import dataclass, field

from .tokens import AboveBelowToken

from .interface import GenericStartStopContinueOnset
from .subevent import Subevent


@dataclass
class Slur(GenericStartStopContinueOnset[Subevent]):
    """
    https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/slur/
    """
    placement: AboveBelowToken = field(default=AboveBelowToken.default())
    
    def __post_init__(self):
        super().__post_init__()
        self._check_start_stop_onset_strong()
    
    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, other: object) -> bool:
        return self is other
    